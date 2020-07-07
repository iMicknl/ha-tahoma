"""Support for TaHoma binary sensors."""
from datetime import timedelta
import logging
from typing import Optional

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_MOTION,
    DEVICE_CLASS_OCCUPANCY,
    DEVICE_CLASS_OPENING,
    DEVICE_CLASS_SMOKE,
    BinarySensorEntity,
)
from homeassistant.const import STATE_OFF, STATE_ON

from .const import DOMAIN, TAHOMA_TYPES
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=120)

CORE_BUTTON_STATE = "core:ButtonState"
CORE_CONTACT_STATE = "core:ContactState"
CORE_GAS_DETECTION_STATE = "core:GasDetectionState"
CORE_OCCUPANCY_STATE = "core:OccupancyState"
CORE_RAIN_STATE = "core:RainState"
CORE_SMOKE_STATE = "core:SmokeState"
CORE_WATER_DETECTION_STATE = "core:WaterDetectionState"

DEVICE_CLASS_BUTTON = "button"
DEVICE_CLASS_GAS = "gas"
DEVICE_CLASS_RAIN = "rain"
DEVICE_CLASS_WATER = "water"

IO_VIBRATION_STATE = "io:VibrationDetectedState"

TAHOMA_BINARY_SENSOR_DEVICE_CLASSES = {
    "AirFlowSensor": DEVICE_CLASS_GAS,
    "CarButtonSensor": DEVICE_CLASS_BUTTON,
    "SmokeSensor": DEVICE_CLASS_SMOKE,
    "OccupancySensor": DEVICE_CLASS_OCCUPANCY,
    "MotionSensor": DEVICE_CLASS_MOTION,
    "ContactSensor": DEVICE_CLASS_OPENING,
    "WindowHandle": DEVICE_CLASS_OPENING,
    "RainSensor": DEVICE_CLASS_RAIN,
    "WaterDetectionSensor": DEVICE_CLASS_WATER,
}


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
