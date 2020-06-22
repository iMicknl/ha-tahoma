"""The TaHoma integration."""
import asyncio
import json
import logging

from requests.exceptions import RequestException
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EXCLUDE, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    config_validation as cv,
    device_registry as dr,
    discovery,
)

from .const import DOMAIN, TAHOMA_TYPES
from .tahoma_api import TahomaApi

_LOGGER = logging.getLogger(__name__)

# TODO Deprecate EXCLUDE for the native method of disabling entities
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
    "binary_sensor",
    "climate",
    "cover",
    "light",
    "lock",
    "scene",
    "sensor",
    "switch",
]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the TaHoma component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up TaHoma from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]

    try:
        controller = await hass.async_add_executor_job(TahomaApi, username, password)
        await hass.async_add_executor_job(controller.get_setup)
        devices = await hass.async_add_executor_job(controller.get_devices)
        scenes = await hass.async_add_executor_job(controller.get_action_groups)

    # TODO Add better exception handling
    except RequestException:
        _LOGGER.exception("Error when getting devices from the TaHoma API")
        return False

    hass.data[DOMAIN][entry.entry_id] = {
        "controller": controller,
        "devices": [],
        "scenes": [],
    }

    for device in devices:
        _device = controller.get_device(device)

        if _device.uiclass in TAHOMA_TYPES:
            if TAHOMA_TYPES[_device.uiclass] in PLATFORMS:
                component = TAHOMA_TYPES[_device.uiclass]
                hass.data[DOMAIN][entry.entry_id]["devices"].append(_device)

        else:
            _LOGGER.debug(
                "Unsupported Tahoma device (%s). Create an issue on Github with the following information. \n\n %s \n %s \n %s",
                _device.type,
                _device.type + " - " + _device.uiclass + " - " + _device.widget,
                json.dumps(_device.command_def) + ",",
                json.dumps(_device.states_def),
            )

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    for scene in scenes:
        hass.data[DOMAIN][entry.entry_id]["scenes"].append(scene)

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
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
