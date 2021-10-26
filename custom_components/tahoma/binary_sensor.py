"""Support for Overkiz binary sensors."""
from __future__ import annotations

from homeassistant.components import binary_sensor
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, OverkizCommandState, OverkizState
from .entity import OverkizBinarySensorDescription, OverkizDescriptiveEntity

BINARY_SENSOR_DESCRIPTIONS = [
    # RainSensor/RainSensor
    OverkizBinarySensorDescription(
        key=OverkizState.CORE_RAIN,
        name="Rain",
        icon="mdi:weather-rainy",
        is_on=lambda state: state == OverkizCommandState.DETECTED,
    ),
    # SmokeSensor/SmokeSensor
    OverkizBinarySensorDescription(
        key=OverkizState.CORE_SMOKE,
        name="Smoke",
        device_class=binary_sensor.DEVICE_CLASS_SMOKE,
        is_on=lambda state: state == OverkizCommandState.DETECTED,
    ),
    # WaterSensor/WaterDetectionSensor
    OverkizBinarySensorDescription(
        key=OverkizState.CORE_WATER_DETECTION,
        name="Water",
        icon="mdi:water",
        is_on=lambda state: state == OverkizCommandState.DETECTED,
    ),
    # AirSensor/AirFlowSensor
    OverkizBinarySensorDescription(
        key=OverkizState.CORE_GAS_DETECTION,
        name="Gas",
        device_class=binary_sensor.DEVICE_CLASS_GAS,
        is_on=lambda state: state == OverkizCommandState.DETECTED,
    ),
    # OccupancySensor/OccupancySensor
    # OccupancySensor/MotionSensor
    OverkizBinarySensorDescription(
        key=OverkizState.CORE_OCCUPANCY,
        name="Occupancy",
        device_class=binary_sensor.DEVICE_CLASS_OCCUPANCY,
        is_on=lambda state: state == OverkizCommandState.PERSON_INSIDE,
    ),
    # ContactSensor/WindowWithTiltSensor
    OverkizBinarySensorDescription(
        key=OverkizState.CORE_VIBRATION,
        name="Vibration",
        device_class=binary_sensor.DEVICE_CLASS_VIBRATION,
        is_on=lambda state: state == OverkizCommandState.DETECTED,
    ),
    # ContactSensor/ContactSensor
    OverkizBinarySensorDescription(
        key=OverkizState.CORE_CONTACT,
        name="Contact",
        device_class=binary_sensor.DEVICE_CLASS_DOOR,
        is_on=lambda state: state == OverkizCommandState.OPEN,
    ),
    # Unknown
    OverkizBinarySensorDescription(
        key=OverkizState.IO_VIBRATION_DETECTED,
        name="Vibration",
        device_class=binary_sensor.DEVICE_CLASS_VIBRATION,
        is_on=lambda state: state == OverkizCommandState.DETECTED,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Overkiz sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    entities = []

    key_supported_states = {
        description.key: description for description in BINARY_SENSOR_DESCRIPTIONS
    }

    for device in coordinator.data.values():
        for state in device.definition.states:
            if description := key_supported_states.get(state.qualified_name):
                entities.append(
                    OverkizBinarySensor(
                        device.deviceurl,
                        coordinator,
                        description,
                    )
                )

    async_add_entities(entities)


class OverkizBinarySensor(OverkizDescriptiveEntity, BinarySensorEntity):
    """Representation of an Overkiz Binary Sensor."""

    @property
    def is_on(self):
        """Return the state of the sensor."""
        state = self.device.states.get(self.entity_description.key)

        if not state:
            return None

        return self.entity_description.is_on(state.value)
