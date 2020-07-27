"""Support for TaHoma binary sensors."""
from datetime import timedelta
import logging
from typing import Optional

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_MOTION,
    DEVICE_CLASS_OCCUPANCY,
    DEVICE_CLASS_OPENING,
    DEVICE_CLASS_SMOKE,
    DOMAIN as BINARY_SENSOR,
    BinarySensorEntity,
)

from .const import DOMAIN
from .tahoma_device import TahomaDevice

SCAN_INTERVAL = timedelta(seconds=120)

CORE_ASSEMBLY_STATE = "core:AssemblyState"
CORE_BUTTON_STATE = "core:ButtonState"
CORE_OPEN_CLOSED_TILT_STATE = "core:OpenClosedTiltState"
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

ICON_WATER = "mdi:water"
ICON_WATER_OFF = "mdi:water-off"
ICON_WAVES = "mdi:waves"
ICON_WEATHER_RAINY = "mdi:weather-rainy"

IO_VIBRATION_STATE = "io:VibrationDetectedState"

STATE_OPEN = "open"
STATE_PERSON_INSIDE = "personInside"
STATE_DETECTED = "detected"
STATE_PRESSED = "pressed"

TAHOMA_BINARY_SENSOR_DEVICE_CLASSES = {
    "AirFlowSensor": DEVICE_CLASS_GAS,
    "CarButtonSensor": DEVICE_CLASS_BUTTON,
    "ContactSensor": DEVICE_CLASS_OPENING,
    "MotionSensor": DEVICE_CLASS_MOTION,
    "OccupancySensor": DEVICE_CLASS_OCCUPANCY,
    "RainSensor": DEVICE_CLASS_RAIN,
    "SirenStatus": DEVICE_CLASS_OPENING,
    "SmokeSensor": DEVICE_CLASS_SMOKE,
    "WaterDetectionSensor": DEVICE_CLASS_WATER,
    "WaterSensor": DEVICE_CLASS_WATER,
    "WindowHandle": DEVICE_CLASS_OPENING,
}


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    controller = data.get("controller")

    entities = [
        TahomaBinarySensor(device, controller)
        for device in data.get("entities").get(BINARY_SENSOR)
    ]
    async_add_entities(entities)


class TahomaBinarySensor(TahomaDevice, BinarySensorEntity):
    """Representation of a TaHoma Binary Sensor."""

    @property
    def is_on(self):
        """Return the state of the sensor."""

        return self.select_state(
            CORE_ASSEMBLY_STATE,
            CORE_BUTTON_STATE,
            CORE_CONTACT_STATE,
            CORE_GAS_DETECTION_STATE,
            CORE_OCCUPANCY_STATE,
            CORE_OPEN_CLOSED_TILT_STATE,
            CORE_RAIN_STATE,
            CORE_SMOKE_STATE,
            CORE_WATER_DETECTION_STATE,
            IO_VIBRATION_STATE,
        ) in [STATE_OPEN, STATE_PERSON_INSIDE, STATE_DETECTED, STATE_PRESSED]

    @property
    def device_class(self):
        """Return the class of the device."""
        return (
            TAHOMA_BINARY_SENSOR_DEVICE_CLASSES.get(self.device.widget)
            or TAHOMA_BINARY_SENSOR_DEVICE_CLASSES.get(self.device.ui_class)
            or None
        )

    @property
    def icon(self) -> Optional[str]:
        """Return the icon to use in the frontend, if any."""
        if self.device_class == DEVICE_CLASS_WATER:
            if self.is_on:
                return ICON_WATER
            else:
                return ICON_WATER_OFF

        icons = {DEVICE_CLASS_GAS: ICON_WAVES, DEVICE_CLASS_RAIN: ICON_WEATHER_RAINY}

        return icons.get(self.device_class)
