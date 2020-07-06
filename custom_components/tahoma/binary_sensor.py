"""Support for TaHoma binary sensors."""
from datetime import timedelta
import logging
from typing import Optional

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import ATTR_BATTERY_LEVEL, STATE_OFF, STATE_ON

from .const import (
    CORE_BUTTON_STATE,
    CORE_CONTACT_STATE,
    CORE_GAS_DETECTION_STATE,
    CORE_OCCUPANCY_STATE,
    CORE_RAIN_STATE,
    CORE_SMOKE_STATE,
    CORE_WATER_DETECTION_STATE,
    DEVICE_CLASS_GAS,
    DEVICE_CLASS_RAIN,
    DEVICE_CLASS_WATER,
    DOMAIN,
    IO_VIBRATION_STATE,
    TAHOMA_BINARY_SENSOR_DEVICE_CLASSES,
    TAHOMA_TYPES,
)
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=120)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    controller = data.get("controller")

    entities = [
        TahomaBinarySensor(device, controller)
        for device in data.get("devices")
        if TAHOMA_TYPES[device.uiclass] == "binary_sensor"
    ]

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
        return self._state == STATE_ON

    @property
    def device_class(self):
        """Return the class of the device."""
        return (
            TAHOMA_BINARY_SENSOR_DEVICE_CLASSES.get(self.tahoma_device.widget)
            or TAHOMA_BINARY_SENSOR_DEVICE_CLASSES.get(self.tahoma_device.uiclass)
            or None
        )

    @property
    def icon(self) -> Optional[str]:
        """Return the icon to use in the frontend, if any."""
        if self.device_class == DEVICE_CLASS_WATER:
            if self.is_on:
                return "mdi:water"
            else:
                return "mdi:water-off"

        icons = {
            DEVICE_CLASS_GAS: "mdi:waves",
            DEVICE_CLASS_RAIN: "mdi:weather-rainy",
        }

        return icons.get(self.device_class)

    def update(self):
        """Update the state."""
        if self.should_wait():
            self.schedule_update_ha_state(True)
            return

        self.controller.get_states([self.tahoma_device])

        states = self.tahoma_device.active_states

        if CORE_CONTACT_STATE in states:
            self.current_value = states.get(CORE_CONTACT_STATE) == "open"

        if CORE_OCCUPANCY_STATE in states:
            self.current_value = states.get(CORE_OCCUPANCY_STATE) == "personInside"

        if CORE_SMOKE_STATE in states:
            self.current_value = states.get(CORE_SMOKE_STATE) == "detected"

        if CORE_RAIN_STATE in states:
            self.current_value = states.get(CORE_RAIN_STATE) == "detected"

        if CORE_WATER_DETECTION_STATE in states:
            self.current_value = states.get(CORE_WATER_DETECTION_STATE) == "detected"

        if CORE_GAS_DETECTION_STATE in states:
            self.current_value = states.get(CORE_GAS_DETECTION_STATE) == "detected"

        if IO_VIBRATION_STATE in states:
            self.current_value = states.get(IO_VIBRATION_STATE) == "detected"

        if CORE_BUTTON_STATE in states:
            self.current_value = states.get(CORE_BUTTON_STATE) == "pressed"

        if self.current_value:
            self._state = STATE_ON
        else:
            self._state = STATE_OFF
