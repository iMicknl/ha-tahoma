"""The Tahoma integration."""
import asyncio

import voluptuous as vol
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_EXCLUDE

from .const import DOMAIN, TAHOMA_TYPES
from .tahoma_api import TahomaApi
from requests.exceptions import RequestException

from homeassistant.helpers import (
    config_validation as cv,
    device_registry as dr,
    discovery,
)

_LOGGER = logging.getLogger(__name__)

#TODO Deprecate EXCLUDE for the native method of disabling entities
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(CONF_EXCLUDE, default=[]): vol.All(
                    cv.ensure_list, [cv.string]
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

PLATFORMS = [
    "cover",
    "light",
    "lock",
    "sensor",
    "switch",
]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Tahoma component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Tahoma from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]

    try:
        controller = TahomaApi(username, password)
        controller.get_setup()
        devices = controller.get_devices()
        # scenes = api.get_action_groups()

    # TODO Add better exception handling
    except RequestException:
        _LOGGER.exception("Error when getting devices from the Tahoma API")
        return False

    hass.data[DOMAIN][entry.entry_id] = {"controller": controller, "devices": []}

    # List devices
    for device in devices:
        _device = controller.get_device(device)

        if _device.uiclass in TAHOMA_TYPES:
            if TAHOMA_TYPES[_device.uiclass] in PLATFORMS:
                component = TAHOMA_TYPES[_device.uiclass]

                hass.data[DOMAIN][entry.entry_id]["devices"].append(_device)

                hass.async_create_task(
                    hass.config_entries.async_forward_entry_setup(entry, component)
                )
        else:
            _LOGGER.warning(
                "Unsupported Tahoma device (%s - %s - %s)",
                _device.type,
                _device.uiclass,
                _device.widget,
            )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN][entry.entry_id].pop(entry.entry_id)

    return unload_ok
