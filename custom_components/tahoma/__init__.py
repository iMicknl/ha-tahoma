"""The TaHoma integration."""
import asyncio
from collections import defaultdict
from datetime import timedelta
import logging

import async_timeout
from tahoma_api.client import TahomaClient
from tahoma_api.exceptions import BadCredentialsException, TooManyRequestsException

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import HomeAssistant

from ...helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN, SUPPORTED_PLATFORMS, TAHOMA_TYPES
from .coordinator import TahomaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


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

    scenes = await client.get_scenarios()

    coordinator = TahomaDataUpdateCoordinator(
        hass,
        _LOGGER,
        # Name of the data. For logging purposes.
        name="Tahoma fetcher",
        client=client,
        devices=await client.get_devices(),
        listener_id=await client.register_event_listener(),
        update_interval=timedelta(seconds=5),
    )

    await coordinator.async_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "controller": client,
        "entities": defaultdict(list),
        "coordinator": coordinator,
    }

    hass.data[DOMAIN][entry.entry_id]["entities"]["scene"] = scenes

    for device in coordinator.data.values():
        if device.widget in TAHOMA_TYPES or device.ui_class in TAHOMA_TYPES:
            platform = TAHOMA_TYPES.get(device.widget) or TAHOMA_TYPES.get(
                device.ui_class
            )

            if platform in SUPPORTED_PLATFORMS:
                hass.data[DOMAIN][entry.entry_id]["entities"][platform].append(device)

        elif device.controllable_name not in [
            "ogp:Bridge",
            "internal:PodV2Component",
            "internal:TSKAlarmComponent",
        ]:  # Add here devices to hide from the debug log.
            _LOGGER.debug(
                "Unsupported Tahoma device detected (%s - %s - %s).",
                device.controllable_name,
                device.ui_class,
                device.widget,
            )

    entities_per_platform = hass.data[DOMAIN][entry.entry_id]["entities"]

    for platform in entities_per_platform:
        if len(entities_per_platform) > 0:
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

    client = hass.data[DOMAIN][entry.entry_id].get("controller")
    await client.close()

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
