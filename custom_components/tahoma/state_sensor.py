"""Support for TaHoma sensors."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components import sensor
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import (
    DEVICE_CLASS_ILLUMINANCE,
    LIGHT_LUX,
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS,
    VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
    VOLUME_LITERS,
)

from .coordinator import TahomaDataUpdateCoordinator
from .tahoma_entity import TahomaEntity


@dataclass
class OverkizSensorDescription(SensorEntityDescription):
    """Class to describe a Overkiz sensor."""

    value: Callable[[Any], Any] = lambda val: val


SUPPORTED_STATES = [
    OverkizSensorDescription(
        key="core:BatteryState",
        name="Battery",
        unit_of_measurement=PERCENTAGE,
        device_class=sensor.DEVICE_CLASS_BATTERY,
        value=lambda value: value,
    ),
    OverkizSensorDescription(
        key="core:RSSILevelState",
        name="RSSI Level",
        value=lambda value: round(value),
        unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        device_class=sensor.DEVICE_CLASS_SIGNAL_STRENGTH,
    ),
    OverkizSensorDescription(
        key="core:ExpectedNumberOfShowerState",
        name="Expected Number Of Shower",
        icon="mdi:shower-head",
        value=lambda value: round(value),
    ),
    OverkizSensorDescription(
        key="core:NumberOfShowerRemainingState",
        name="Number of Shower Remaining",
        icon="mdi:shower-head",
        value=lambda value: round(value),
    ),
    # V40 is measured in litres (L) and shows the amount of warm (mixed) water with a temperature of 40 C, which can be drained from a switched off electric water heater.
    OverkizSensorDescription(
        key="core:V40WaterVolumeEstimationState",
        name="Water Volume Estimation at 40 °C",
        icon="mdi:water",
        value=lambda value: round(value),
        unit_of_measurement=VOLUME_LITERS,
        entity_registry_enabled_default=False,
    ),
    OverkizSensorDescription(
        key="core:WaterConsumptionState",
        name="Water Consumption",
        icon="mdi:water",
        value=lambda value: round(value),
        unit_of_measurement=VOLUME_LITERS,
    ),
    OverkizSensorDescription(
        key="io:OutletEngineState",
        name="Outlet Engine",
        icon="mdi:fan-chevron-down",
        value=lambda value: round(value),
        unit_of_measurement=VOLUME_LITERS,
    ),
    OverkizSensorDescription(
        key="io:InletEngineState",
        name="Inlet Engine",
        icon="mdi:fan-chevron-up",
        value=lambda value: round(value),
        unit_of_measurement=VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
    ),
    OverkizSensorDescription(
        key="hlrrwifi:RoomTemperatureState",
        name="Room Temperature",
        value=lambda value: round(value),
        device_class=sensor.DEVICE_CLASS_TEMPERATURE,
    ),
    OverkizSensorDescription(
        key="io:MiddleWaterTemperatureState",
        name="Middle Water Temperature",
        value=lambda value: round(value),
        device_class=sensor.DEVICE_CLASS_TEMPERATURE,
    ),
    OverkizSensorDescription(
        key="core:LuminanceState",
        name="Luminance",
        value=lambda value: round(value),
        device_class=DEVICE_CLASS_ILLUMINANCE,
        unit_of_measurement=LIGHT_LUX,
    ),
    OverkizSensorDescription(
        key="io:PriorityLockOriginatorState",
        name="Priority Lock Originator",
        value=lambda value: value,
    ),
]


class TahomaStateSensor(TahomaEntity, SensorEntity):
    """Representation of a TaHoma Sensor, based on a secondary device."""

    def __init__(
        self,
        device_url: str,
        coordinator: TahomaDataUpdateCoordinator,
        description: OverkizSensorDescription,
    ):
        """Initialize the device."""
        super().__init__(device_url, coordinator)
        self.entity_description = description

    @property
    def state(self):
        """Return the value of the sensor."""
        state = self.select_state(self.entity_description.key)

        return self.entity_description.value(state) if state is not None else None

    @property
    def name(self) -> str:
        """Return the name of the device."""
        if self.index:
            return f"{self.entity_description.name} {self.index}"
        return self.entity_description.name

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{super().unique_id}-{self.entity_description.key}"
