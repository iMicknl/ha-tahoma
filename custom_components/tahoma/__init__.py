"""The TaHoma integration."""
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
import logging

from aiohttp import ClientError, ServerDisconnectedError
from homeassistant.components.scene import DOMAIN as SCENE
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_EXCLUDE, CONF_PASSWORD, CONF_SOURCE, CONF_USERNAME
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import (
    config_validation as cv,
    device_registry as dr,
    service,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pyhoma.client import TahomaClient
from pyhoma.exceptions import (
    BadCredentialsException,
    InvalidCommandException,
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
    HUB_MANUFACTURER,
    IGNORED_TAHOMA_DEVICES,
    SUPPORTED_ENDPOINTS,
    TAHOMA_DEVICE_TO_PLATFORM,
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


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TaHoma from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)
    hub = entry.data.get(CONF_HUB, DEFAULT_HUB)
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

        tasks = [
            client.get_devices(),
            client.get_scenarios(),
            client.get_gateways(),
            client.get_places(),
        ]
        devices, scenarios, gateways, places = await asyncio.gather(*tasks)
    except BadCredentialsException as exception:
        raise ConfigEntryAuthFailed from exception
    except TooManyRequestsException as exception:
        raise ConfigEntryNotReady("Too many requests, try again later") from exception
    except (TimeoutError, ClientError, ServerDisconnectedError) as exception:
        raise ConfigEntryNotReady("Failed to connect") from exception
    except MaintenanceException as exception:
        raise ConfigEntryNotReady("Server is down for maintenance") from exception
    except Exception as exception:  # pylint: disable=broad-except
        _LOGGER.exception(exception)
        return False

    update_interval = timedelta(
        seconds=entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
    )

    tahoma_coordinator = TahomaDataUpdateCoordinator(
        hass,
        _LOGGER,
        name="device events",
        client=client,
        devices=devices,
        places=places,
        update_interval=update_interval,
    )

    _LOGGER.debug(
        "Initialized DataUpdateCoordinator with %s interval.", str(update_interval)
    )

    await tahoma_coordinator.async_refresh()

    platforms = defaultdict(list)
    platforms[SCENE] = scenarios
    platforms["sensor"] = []

    hass.data[DOMAIN][entry.entry_id] = {
        "platforms": platforms,
        "coordinator": tahoma_coordinator,
        "update_listener": entry.add_update_listener(update_listener),
    }

    for device in tahoma_coordinator.data.values():
        platform = TAHOMA_DEVICE_TO_PLATFORM.get(
            device.widget
        ) or TAHOMA_DEVICE_TO_PLATFORM.get(device.ui_class)
        if platform:
            platforms[platform].append(device)
            log_device("Added device", device)
        elif (
            device.widget not in IGNORED_TAHOMA_DEVICES
            and device.ui_class not in IGNORED_TAHOMA_DEVICES
        ):
            log_device("Unsupported device detected", device)

        if device.widget == HOMEKIT_STACK:
            print_homekit_setup_code(device)

    for platform in platforms:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    device_registry = await dr.async_get_registry(hass)

    for gateway in gateways:
        _LOGGER.debug(
            "Added gateway (%s - %s - %s)",
            gateway.id,
            gateway.type,
            gateway.sub_type,
        )

        gateway_model = (
            beautify_name(gateway.sub_type.name)
            if isinstance(gateway.sub_type, Enum)
            else None
        )

        gateway_name = (
            f"{beautify_name(gateway.type.name)} hub"
            if isinstance(gateway.type, Enum)
            else gateway.type
        )

        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, gateway.id)},
            model=gateway_model,
            manufacturer=HUB_MANUFACTURER[hub],
            name=gateway_name,
            sw_version=gateway.connectivity.protocol_version,
        )

    async def handle_execute_command(call: ServiceCall):
        """Handle execute command service."""
        entity_registry = await hass.helpers.entity_registry.async_get_registry()

        for entity_id in call.data.get("entity_id"):
            entity = entity_registry.entities.get(entity_id)

            try:
                await tahoma_coordinator.client.execute_command(
                    entity.unique_id,
                    Command(call.data.get("command"), call.data.get("args")),
                    "Home Assistant Service",
                )
            except InvalidCommandException as exception:
                _LOGGER.error(exception)

    service.async_register_admin_service(
        hass,
        DOMAIN,
        SERVICE_EXECUTE_COMMAND,
        handle_execute_command,
        vol.Schema(
            {
                vol.Required("entity_id"): [cv.entity_id],
                vol.Required("command"): cv.string,
                vol.Optional("args", default=[]): vol.All(
                    cv.ensure_list, [vol.Any(str, int)]
                ),
            },
        ),
    )

    async def handle_get_execution_history(call):
        """Handle get execution history service."""
        await write_execution_history_to_log(tahoma_coordinator.client)

    service.async_register_admin_service(
        hass,
        DOMAIN,
        "get_execution_history",
        handle_get_execution_history,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    entities_per_platform = hass.data[DOMAIN][entry.entry_id]["platforms"]

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


async def write_execution_history_to_log(client: TahomaClient):
    """Retrieve execution history and write output to log."""
    history = await client.get_execution_history()

    for item in history:
        timestamp = datetime.fromtimestamp(int(item.event_time) / 1000)

        for command in item.commands:
            date = timestamp.strftime("%Y-%m-%d %H:%M:%S")

            _LOGGER.info(
                "{timestamp}: {command} executed via {app} on {device}, with {parameters}.".format(
                    command=command.command,
                    timestamp=date,
                    device=command.deviceurl,
                    parameters=command.parameters,
                    app=item.label,
                )
            )


def beautify_name(name: str):
    """Return human readable string."""
    return name.replace("_", " ").title()


def log_device(message: str, device: Device) -> None:
    """Log device information."""
    _LOGGER.debug(
        "%s (%s - %s - %s - %s)",
        message,
        device.controllable_name,
        device.ui_class,
        device.widget,
        device.deviceurl,
    )
