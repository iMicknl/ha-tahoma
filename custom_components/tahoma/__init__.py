"""The TaHoma integration."""
import asyncio
from collections import defaultdict
from datetime import timedelta
import logging

from pyhoma.client import TahomaClient
from pyhoma.exceptions import BadCredentialsException, TooManyRequestsException

from homeassistant.components.scene import DOMAIN as SCENE
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import HomeAssistant

from .const import DOMAIN, TAHOMA_TYPES
from .coordinator import TahomaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)
DEFAULT_UPDATE_INTERVAL = timedelta(seconds=10)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the TaHoma component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up TaHoma from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)

    try:
        client = TahomaClient(username, password)
        await client.login()
    except TooManyRequestsException as exception:
        _LOGGER.exception(exception)
        return False
    except BadCredentialsException as exception:
        _LOGGER.exception(exception)
        return False
    except Exception as exception:  # pylint: disable=broad-except
        _LOGGER.exception(exception)
        return False

    tahoma_coordinator = TahomaDataUpdateCoordinator(
        hass,
        _LOGGER,
        # Name of the data. For logging purposes.
        name="TaHoma Event Fetcher",
        client=client,
        devices=await client.get_devices(),
        listener_id=await client.register_event_listener(),
        update_interval=DEFAULT_UPDATE_INTERVAL,
    )

    await tahoma_coordinator.async_refresh()

    entities = defaultdict(list)
    entities[SCENE] = await client.get_scenarios()

    hass.data[DOMAIN][entry.entry_id] = {
        "entities": entities,
        "coordinator": tahoma_coordinator,
    }

    for device in tahoma_coordinator.data.values():
        platform = TAHOMA_TYPES.get(device.widget) or TAHOMA_TYPES.get(device.ui_class)
        if platform:
            entities[platform].append(device)

        elif device.controllable_name not in [
            "ogp:Bridge",
            "internal:PodV2Component",
            "internal:TSKAlarmComponent",
        ]:  # Add here devices to hide from the debug log.
            _LOGGER.debug(
                "Unsupported TaHoma device detected (%s - %s - %s).",
                device.controllable_name,
                device.ui_class,
                device.widget,
            )

    for platform in entities:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    async def async_close_client(self, *_):
        """Close HTTP client."""
        await client.close()

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, async_close_client)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""

    await hass.data[DOMAIN][entry.entry_id].get("coordinator").client.close()

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
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
