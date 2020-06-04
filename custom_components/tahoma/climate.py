"""Support for Tahoma climate."""
from datetime import timedelta
import logging
from typing import List

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_OFF,
    HVAC_MODE_AUTO,
)

from .const import DOMAIN, TAHOMA_TYPES
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=120)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Tahoma sensors from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]

    entities = []
    controller = data.get("controller")

    for device in data.get("devices"):
        if TAHOMA_TYPES[device.uiclass] == "climate":
            entities.append(TahomaClimate(device, controller))

    async_add_entities(entities)

class TahomaClimate(TahomaDevice, ClimateEntity):
    """Representation of a Tahoma thermostat."""

    def __init__(self, tahoma_device, controller):
        """Initialize the sensor."""
        super().__init__(tahoma_device, controller)
        self._hvac_modes = [HVAC_MODE_OFF, HVAC_MODE_AUTO]
        self._hvac_mode = None

    def update(self):
        """Update the state."""
        self.controller.get_states([self.tahoma_device])
        #TODO implement update method

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode.

        Need to be one of HVAC_MODE_*.
        """
        return self._hvac_mode

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes.

        Need to be a subset of HVAC_MODES.
        """
        return self._hvac_modes