"""Support for TaHoma binary sensors."""
from datetime import timedelta
import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import ATTR_BATTERY_LEVEL, STATE_OFF, STATE_ON

from .const import (
    CORE_CONTACT_STATE,
    CORE_OCCUPANCY_STATE,
    CORE_SMOKE_STATE,
    DOMAIN,
    TAHOMA_BINARY_SENSOR_DEVICE_CLASSES,
    TAHOMA_TYPES,
)
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=120)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma sensors from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]

    entities = []
    controller = data.get("controller")

    for device in data.get("devices"):
        if TAHOMA_TYPES[device.uiclass] == "binary_sensor":
            entities.append(TahomaBinarySensor(device, controller))

    async_add_entities(entities)


class TahomaBinarySensor(TahomaDevice, BinarySensorEntity):
    """Representation of a TaHoma Binary Sensor."""

    def __init__(self, tahoma_device, controller):
        """Initialize the sensor."""
        super().__init__(tahoma_device, controller)

        self._state = None

    @property
    def is_on(self):
        """Return the state of the sensor."""
        return bool(self._state == STATE_ON)

    @property
    def device_class(self):
        """Return the class of the device."""
        return (
            TAHOMA_BINARY_SENSOR_DEVICE_CLASSES.get(self.tahoma_device.widget)
            or TAHOMA_BINARY_SENSOR_DEVICE_CLASSES.get(self.tahoma_device.uiclass)
            or None
        )

    def update(self):
        """Update the state."""
        self.controller.get_states([self.tahoma_device])

        if CORE_CONTACT_STATE in self.tahoma_device.active_states:
            self.current_value = (
                self.tahoma_device.active_states.get(CORE_CONTACT_STATE) == "open"
            )

        if CORE_OCCUPANCY_STATE in self.tahoma_device.active_states:
            self.current_value = (
                self.tahoma_device.active_states.get(CORE_OCCUPANCY_STATE)
                == "personInside"
            )

        if CORE_SMOKE_STATE in self.tahoma_device.active_states:
            self.current_value = (
                self.tahoma_device.active_states.get(CORE_SMOKE_STATE) == "detected"
            )

        if self.current_value:
            self._state = STATE_ON
        else:
            self._state = STATE_OFF
