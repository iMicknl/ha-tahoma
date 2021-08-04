"""Support for TaHoma sensors."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components import sensor
from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    ENERGY_WATT_HOUR,
    LIGHT_LUX,
    PERCENTAGE,
    POWER_WATT,
    SIGNAL_STRENGTH_DECIBELS,
    TEMP_CELSIUS,
    VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
    VOLUME_LITERS,
)
from homeassistant.util.dt import utc_from_timestamp

from .coordinator import TahomaDataUpdateCoordinator
from .tahoma_entity import TahomaEntity


@dataclass
class OverkizSensorDescription(SensorEntityDescription):
    """Class to describe a Overkiz sensor."""

    value: Callable[[Any], Any] = lambda val: val


SUPPORTED_STATES = [
    OverkizSensorDescription(
        key="core:BatteryLevelState",
        name="Battery Level",
        unit_of_measurement=PERCENTAGE,
        device_class=sensor.DEVICE_CLASS_BATTERY,
    ),
    OverkizSensorDescription(
        key="core:BatteryState",
        name="Battery",
        unit_of_measurement=PERCENTAGE,
        device_class=sensor.DEVICE_CLASS_BATTERY,
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
        key="io:PriorityLockOriginatorState",
        name="Priority Lock Originator",
        icon="mdi:alert",
    ),
    OverkizSensorDescription(
        key="core:FossilEnergyConsumptionState",
        name="Fossil Energy Consumption",
        device_class=sensor.DEVICE_CLASS_ENERGY,
    ),
    OverkizSensorDescription(
        key="core:GasConsumptionState",
        name="Gas Consumption",
    ),
    OverkizSensorDescription(
        key="core:ThermalEnergyConsumptionState",
        name="Thermal Energy Consumption",
    ),
    # LightSensor/LuminanceSensor
    OverkizSensorDescription(
        key="core:LuminanceState",
        name="Luminance",
        value=lambda value: round(value),
        device_class=sensor.DEVICE_CLASS_ILLUMINANCE,
        unit_of_measurement=LIGHT_LUX,  # core:MeasuredValueType = core:LuminanceInLux
    ),
    # ElectricitySensor/CumulativeElectricPowerConsumptionSensor
    OverkizSensorDescription(
        key="core:ElectricEnergyConsumptionState",
        name="Electric Energy Consumption",
        value=lambda value: round(value),
        device_class=sensor.DEVICE_CLASS_ENERGY,
        unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh (not for modbus:YutakiV2DHWElectricalEnergyConsumptionComponent)
        state_class=STATE_CLASS_MEASUREMENT,  # core:MeasurementCategory attribute = electric/overall
        last_reset=utc_from_timestamp(0),
    ),
    OverkizSensorDescription(
        key="core:ElectricPowerConsumptionState",
        name="Electric Power Consumption",
        value=lambda value: round(value),
        device_class=sensor.DEVICE_CLASS_POWER,
        unit_of_measurement=POWER_WATT,  # core:MeasuredValueType = core:ElectricalEnergyInWh (not for modbus:YutakiV2DHWElectricalEnergyConsumptionComponent)
    ),
    OverkizSensorDescription(
        key="core:ConsumptionTariff1State",
        name="Consumption Tariff 1",
        value=lambda value: round(value),
        device_class=sensor.DEVICE_CLASS_ENERGY,
        unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
    ),
    OverkizSensorDescription(
        key="core:ConsumptionTariff2State",
        name="Consumption Tariff 2",
        value=lambda value: round(value),
        device_class=sensor.DEVICE_CLASS_ENERGY,
        unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
    ),
    OverkizSensorDescription(
        key="core:ConsumptionTariff3State",
        name="Consumption Tariff 3",
        value=lambda value: round(value),
        device_class=sensor.DEVICE_CLASS_ENERGY,
        unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
    ),
    OverkizSensorDescription(
        key="core:ConsumptionTariff4State",
        name="Consumption Tariff 4",
        value=lambda value: round(value),
        device_class=sensor.DEVICE_CLASS_ENERGY,
        unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
    ),
    OverkizSensorDescription(
        key="core:ConsumptionTariff5State",
        name="Consumption Tariff 5",
        value=lambda value: round(value),
        device_class=sensor.DEVICE_CLASS_ENERGY,
        unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
    ),
    OverkizSensorDescription(
        key="core:ConsumptionTariff6State",
        name="Consumption Tariff 6",
        value=lambda value: round(value),
        device_class=sensor.DEVICE_CLASS_ENERGY,
        unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
    ),
    OverkizSensorDescription(
        key="core:ConsumptionTariff7State",
        name="Consumption Tariff 7",
        value=lambda value: round(value),
        device_class=sensor.DEVICE_CLASS_ENERGY,
        unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
    ),
    OverkizSensorDescription(
        key="core:ConsumptionTariff8State",
        name="Consumption Tariff 8",
        value=lambda value: round(value),
        device_class=sensor.DEVICE_CLASS_ENERGY,
        unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
    ),
    OverkizSensorDescription(
        key="core:ConsumptionTariff9State",
        name="Consumption Tariff 9",
        value=lambda value: round(value),
        device_class=sensor.DEVICE_CLASS_ENERGY,
        unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
    ),
    # HumiditySensor/RelativeHumiditySensor
    OverkizSensorDescription(
        key="core:RelativeHumidityState",
        name="Relative Humidity",
        value=lambda value: round(value, 2),
        device_class=sensor.DEVICE_CLASS_HUMIDITY,
        unit_of_measurement=PERCENTAGE,  # core:MeasuredValueType = core:RelativeValueInPercentage
    ),
    # TemperatureSensor/TemperatureSensor
    OverkizSensorDescription(
        key="core:TemperatureState",
        name="Temperature",
        value=lambda value: round(value),
        device_class=sensor.DEVICE_CLASS_TEMPERATURE,
        unit_of_measurement=TEMP_CELSIUS,  # core:MeasuredValueType = core:TemperatureInCelcius
    ),
    # WeatherSensor/WeatherForecastSensor
    OverkizSensorDescription(
        key="core:WeatherStatusState",
        name="Weather Status",
    ),
    OverkizSensorDescription(
        key="core:MinimumTemperatureState",
        name="Minimum Temperature",
    ),
    OverkizSensorDescription(
        key="core:MaximumTemperatureState",
        name="Maximum Temperature",
    ),
    # AirSensor/COSensor
    OverkizSensorDescription(
        key="core:COConcentrationState",
        name="CO Concentration",
        value=lambda value: round(value),
        device_class=sensor.DEVICE_CLASS_CO,
        unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
    ),
    # AirSensor/CO2Sensor
    OverkizSensorDescription(
        key="core:CO2ConcentrationState",
        name="CO2 Concentration",
        value=lambda value: round(value),
        device_class=sensor.DEVICE_CLASS_CO2,
        unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
    ),
    # SunSensor/SunEnergySensor
    OverkizSensorDescription(
        key="core:SunEnergyState",
        name="Sun Energy",
        value=lambda value: round(value, 2),
        device_class=sensor.DEVICE_CLASS_ENERGY,
        icon="mdi:solar-power",
    ),
    # WindSensor/WindSpeedSensor
    OverkizSensorDescription(
        key="core:WindSpeedState",
        name="Wind Speed",
        value=lambda value: round(value, 2),
        icon="mdi:weather-windy",
    ),
    # SmokeSensor/SmokeSensor
    OverkizSensorDescription(
        key="io:SensorRoomState",
        name="Sensor Room",
        value=lambda value: str(value).capitalize(),
        entity_registry_enabled_default=False,
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

        if state:
            # Transform the value with a lambda function
            if hasattr(self.entity_description, "value"):
                return self.entity_description.value(state)
            return state

        return None

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
