"""Support for Tahoma binary sensors."""
from datetime import timedelta
import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import ATTR_BATTERY_LEVEL, STATE_OFF, STATE_ON

from .const import DOMAIN, TAHOMA_TYPES, TAHOMA_BINARY_SENSOR_DEVICE_CLASSES
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=120)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Tahoma sensors from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]

    entities = []
    controller = data.get("controller")

    for device in data.get("devices"):
        if TAHOMA_TYPES[device.uiclass] == "binary_sensor":
            entities.append(TahomaBinarySensor(device, controller))

    async_add_entities(entities)


class TahomaBinarySensor(TahomaDevice, BinarySensorEntity):
    """Representation of a Tahoma Binary Sensor."""

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

        if "core:ContactState" in self.tahoma_device.active_states:
            self.current_value = self.tahoma_device.active_states.get("core:ContactState")

        if "core:OccupancyState" in self.tahoma_device.active_states:
            self.current_value = self.tahoma_device.active_states.get("core:OccupancyState")

        if "core:SmokeState" in self.tahoma_device.active_states:
            self.current_value = self.tahoma_device.active_states.get("core:SmokeState") != "notDetected"
           
        if self.current_value:
            self._state = STATE_ON
        else:
            self._sate = STATE_OFF

        _LOGGER.debug("Update %s, state: %s", self._name, self._state)
