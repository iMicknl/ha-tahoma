"""The TaHoma integration."""
import asyncio
from collections import defaultdict
from datetime import timedelta
import logging

from aiohttp import ClientError, ServerDisconnectedError
from homeassistant.components.scene import DOMAIN as SCENE
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_EXCLUDE, CONF_PASSWORD, CONF_SOURCE, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import (
    config_validation as cv,
    device_registry as dr,
    service,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pyhoma.client import TahomaClient
from pyhoma.exceptions import (
    BadCredentialsException,
    MaintenanceException,
    TooManyRequestsException,
)
from pyhoma.models import Command, Device
import voluptuous as vol

from .const import (
    CONF_HUB,
    CONF_UPDATE_INTERVAL,
    DEFAULT_HUB,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    IGNORED_TAHOMA_TYPES,
    SUPPORTED_ENDPOINTS,
    TAHOMA_TYPES,
)
from .coordinator import TahomaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SERVICE_EXECUTE_COMMAND = "execute_command"

HOMEKIT_SETUP_CODE = "homekit:SetupCode"
HOMEKIT_STACK = "HomekitStack"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            cv.deprecated(CONF_EXCLUDE),
            vol.Schema(
                {
                    vol.Required(CONF_USERNAME): cv.string,
                    vol.Required(CONF_PASSWORD): cv.string,
                    vol.Optional(CONF_EXCLUDE, default=[]): vol.All(
                        cv.ensure_list, [cv.string]
                    ),
                }
            ),
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the TaHoma component."""
    configuration = config.get(DOMAIN)

    if configuration is None:
        return True

    if any(
        configuration.get(CONF_USERNAME) in entry.data.get(CONF_USERNAME)
        for entry in hass.config_entries.async_entries(DOMAIN)
    ):
        return True

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={CONF_SOURCE: SOURCE_IMPORT},
            data=configuration,
        )
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up TaHoma from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)
    hub = entry.data.get(CONF_HUB) or DEFAULT_HUB
    endpoint = SUPPORTED_ENDPOINTS[hub]

    session = async_get_clientsession(hass)
    client = TahomaClient(
        username,
        password,
        session=session,
        api_url=endpoint,
    )

    try:
        await client.login()
        devices = await client.get_devices()
        scenarios = await client.get_scenarios()
        gateways = await client.get_gateways()
    except BadCredentialsException:
        _LOGGER.error("invalid_auth")
        return False
    except TooManyRequestsException as exception:
        _LOGGER.error("too_many_requests")
        raise ConfigEntryNotReady from exception
    except (TimeoutError, ClientError, ServerDisconnectedError) as exception:
        _LOGGER.error("cannot_connect")
        raise ConfigEntryNotReady from exception
    except MaintenanceException as exception:
        _LOGGER.error("server_in_maintenance")
        raise ConfigEntryNotReady from exception
    except Exception as exception:  # pylint: disable=broad-except
        _LOGGER.exception(exception)
        return False

    update_interval = entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)

    tahoma_coordinator = TahomaDataUpdateCoordinator(
        hass,
        _LOGGER,
        name="TaHoma Event Fetcher",
        client=client,
        devices=devices,
        update_interval=timedelta(seconds=update_interval),
    )

    await tahoma_coordinator.async_refresh()

    entities = defaultdict(list)
    entities[SCENE] = scenarios

    hass.data[DOMAIN][entry.entry_id] = {
        "entities": entities,
        "coordinator": tahoma_coordinator,
        "update_listener": entry.add_update_listener(update_listener),
    }

    for device in tahoma_coordinator.data.values():
        platform = TAHOMA_TYPES.get(device.widget) or TAHOMA_TYPES.get(device.ui_class)
        if platform:
            entities[platform].append(device)
            _LOGGER.debug(
                "Added TaHoma device (%s - %s - %s - %s)",
                device.controllable_name,
                device.ui_class,
                device.widget,
                device.deviceurl,
            )
        elif (
            device.widget not in IGNORED_TAHOMA_TYPES
            and device.ui_class not in IGNORED_TAHOMA_TYPES
        ):
            _LOGGER.debug(
                "Unsupported TaHoma device detected (%s - %s - %s - %s)",
                device.controllable_name,
                device.ui_class,
                device.widget,
                device.deviceurl,
            )

        if device.widget == HOMEKIT_STACK:
            print_homekit_setup_code(device)

    for platform in entities:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    async def handle_execute_command(call):
        """Handle execute command service."""
        entity_registry = await hass.helpers.entity_registry.async_get_registry()
        entity = entity_registry.entities.get(call.data.get("entity_id"))
        await tahoma_coordinator.client.execute_command(
            entity.unique_id,
            Command(call.data.get("command"), call.data.get("args")),
            "Home Assistant Service",
        )

    service.async_register_admin_service(
        hass,
        DOMAIN,
        SERVICE_EXECUTE_COMMAND,
        handle_execute_command,
        vol.Schema(
            {
                vol.Required("entity_id"): cv.string,
                vol.Required("command"): cv.string,
                vol.Optional("args", default=[]): vol.All(
                    cv.ensure_list, [vol.Any(str, int)]
                ),
            }
        ),
    )

    device_registry = await dr.async_get_registry(hass)

    for gateway in gateways:
        gateway_model = (
            beautify_name(gateway.sub_type.name) if gateway.sub_type else None
        )
        gateway_name = (
            f"{beautify_name(gateway.type.name)} hub" if gateway.type else None
        )

        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, gateway.id)},
            model=gateway_model,
            manufacturer="Somfy",
            name=gateway_name,
            sw_version=gateway.connectivity.protocol_version,
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    entities_per_platform = hass.data[DOMAIN][entry.entry_id]["entities"]

    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in entities_per_platform
            ]
        )
    )

    if unload_ok:
        hass.data[DOMAIN][entry.entry_id]["update_listener"]()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Update when config_entry options update."""
    if entry.options[CONF_UPDATE_INTERVAL]:
        coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        new_update_interval = timedelta(seconds=entry.options[CONF_UPDATE_INTERVAL])
        coordinator.update_interval = new_update_interval
        coordinator.original_update_interval = new_update_interval

        await coordinator.async_refresh()


def print_homekit_setup_code(device: Device):
    """Retrieve and print HomeKit Setup Code."""
    if device.attributes:
        homekit = device.attributes.get(HOMEKIT_SETUP_CODE)

        if homekit:
            _LOGGER.info("HomeKit support detected with setup code %s.", homekit.value)


def beautify_name(name: str):
    """Return human readable string."""
    return name.replace("_", " ").title()
