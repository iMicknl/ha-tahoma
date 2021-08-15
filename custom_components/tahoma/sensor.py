"""Support for TaHoma sensors."""
from __future__ import annotations

import logging

from homeassistant.components import sensor
from homeassistant.components.sensor import STATE_CLASS_MEASUREMENT, SensorEntity
from homeassistant.config_entries import ConfigEntry
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
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.dt import utc_from_timestamp

from .const import DOMAIN
from .entity import OverkizDescriptiveEntity, OverkizSensorDescription

_LOGGER = logging.getLogger(__name__)


SENSOR_DESCRIPTIONS = [
    OverkizSensorDescription(
        key="core:BatteryLevelState",
        name="Battery Level",
        unit_of_measurement=PERCENTAGE,
        device_class=sensor.DEVICE_CLASS_BATTERY,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key="core:BatteryState",
        name="Battery",
        device_class=sensor.DEVICE_CLASS_BATTERY,
        value=lambda value: str(value).capitalize(),
    ),
    OverkizSensorDescription(
        key="core:RSSILevelState",
        name="RSSI Level",
        unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        device_class=sensor.DEVICE_CLASS_SIGNAL_STRENGTH,
        state_class=STATE_CLASS_MEASUREMENT,
        value=lambda value: round(value),
    ),
    OverkizSensorDescription(
        key="core:ExpectedNumberOfShowerState",
        name="Expected Number Of Shower",
        icon="mdi:shower-head",
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key="core:NumberOfShowerRemainingState",
        name="Number of Shower Remaining",
        icon="mdi:shower-head",
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    # V40 is measured in litres (L) and shows the amount of warm (mixed) water with a temperature of 40 C, which can be drained from a switched off electric water heater.
    OverkizSensorDescription(
        key="core:V40WaterVolumeEstimationState",
        name="Water Volume Estimation at 40 °C",
        icon="mdi:water",
        unit_of_measurement=VOLUME_LITERS,
        entity_registry_enabled_default=False,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key="core:WaterConsumptionState",
        name="Water Consumption",
        icon="mdi:water",
        unit_of_measurement=VOLUME_LITERS,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key="io:OutletEngineState",
        name="Outlet Engine",
        icon="mdi:fan-chevron-down",
        unit_of_measurement=VOLUME_LITERS,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key="io:InletEngineState",
        name="Inlet Engine",
        icon="mdi:fan-chevron-up",
        unit_of_measurement=VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key="hlrrwifi:RoomTemperatureState",
        name="Room Temperature",
        device_class=sensor.DEVICE_CLASS_TEMPERATURE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key="io:MiddleWaterTemperatureState",
        name="Middle Water Temperature",
        device_class=sensor.DEVICE_CLASS_TEMPERATURE,
        state_class=STATE_CLASS_MEASUREMENT,
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
        device_class=sensor.DEVICE_CLASS_ILLUMINANCE,
        unit_of_measurement=LIGHT_LUX,  # core:MeasuredValueType = core:LuminanceInLux
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    # ElectricitySensor/CumulativeElectricPowerConsumptionSensor
    OverkizSensorDescription(
        key="core:ElectricEnergyConsumptionState",
        name="Electric Energy Consumption",
        device_class=sensor.DEVICE_CLASS_ENERGY,
        unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh (not for modbus:YutakiV2DHWElectricalEnergyConsumptionComponent)
        state_class=STATE_CLASS_MEASUREMENT,  # core:MeasurementCategory attribute = electric/overall
        last_reset=utc_from_timestamp(0),
    ),
    OverkizSensorDescription(
        key="core:ElectricPowerConsumptionState",
        name="Electric Power Consumption",
        device_class=sensor.DEVICE_CLASS_POWER,
        unit_of_measurement=POWER_WATT,  # core:MeasuredValueType = core:ElectricalEnergyInWh (not for modbus:YutakiV2DHWElectricalEnergyConsumptionComponent)
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key="core:ConsumptionTariff1State",
        name="Consumption Tariff 1",
        device_class=sensor.DEVICE_CLASS_ENERGY,
        unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key="core:ConsumptionTariff2State",
        name="Consumption Tariff 2",
        device_class=sensor.DEVICE_CLASS_ENERGY,
        unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key="core:ConsumptionTariff3State",
        name="Consumption Tariff 3",
        device_class=sensor.DEVICE_CLASS_ENERGY,
        unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key="core:ConsumptionTariff4State",
        name="Consumption Tariff 4",
        device_class=sensor.DEVICE_CLASS_ENERGY,
        unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key="core:ConsumptionTariff5State",
        name="Consumption Tariff 5",
        device_class=sensor.DEVICE_CLASS_ENERGY,
        unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key="core:ConsumptionTariff6State",
        name="Consumption Tariff 6",
        device_class=sensor.DEVICE_CLASS_ENERGY,
        unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key="core:ConsumptionTariff7State",
        name="Consumption Tariff 7",
        device_class=sensor.DEVICE_CLASS_ENERGY,
        unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key="core:ConsumptionTariff8State",
        name="Consumption Tariff 8",
        device_class=sensor.DEVICE_CLASS_ENERGY,
        unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key="core:ConsumptionTariff9State",
        name="Consumption Tariff 9",
        device_class=sensor.DEVICE_CLASS_ENERGY,
        unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    # HumiditySensor/RelativeHumiditySensor
    OverkizSensorDescription(
        key="core:RelativeHumidityState",
        name="Relative Humidity",
        value=lambda value: round(value, 2),
        device_class=sensor.DEVICE_CLASS_HUMIDITY,
        unit_of_measurement=PERCENTAGE,  # core:MeasuredValueType = core:RelativeValueInPercentage
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    # TemperatureSensor/TemperatureSensor
    OverkizSensorDescription(
        key="core:TemperatureState",
        name="Temperature",
        value=lambda value: round(value, 2),
        device_class=sensor.DEVICE_CLASS_TEMPERATURE,
        unit_of_measurement=TEMP_CELSIUS,  # core:MeasuredValueType = core:TemperatureInCelcius
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    # WeatherSensor/WeatherForecastSensor
    OverkizSensorDescription(
        key="core:WeatherStatusState",
        name="Weather Status",
    ),
    OverkizSensorDescription(
        key="core:MinimumTemperatureState",
        name="Minimum Temperature",
        device_class=sensor.DEVICE_CLASS_TEMPERATURE,
        unit_of_measurement=TEMP_CELSIUS,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key="core:MaximumTemperatureState",
        name="Maximum Temperature",
        device_class=sensor.DEVICE_CLASS_TEMPERATURE,
        unit_of_measurement=TEMP_CELSIUS,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    # AirSensor/COSensor
    OverkizSensorDescription(
        key="core:COConcentrationState",
        name="CO Concentration",
        device_class=sensor.DEVICE_CLASS_CO,
        unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    # AirSensor/CO2Sensor
    OverkizSensorDescription(
        key="core:CO2ConcentrationState",
        name="CO2 Concentration",
        device_class=sensor.DEVICE_CLASS_CO2,
        unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    # SunSensor/SunEnergySensor
    OverkizSensorDescription(
        key="core:SunEnergyState",
        name="Sun Energy",
        value=lambda value: round(value, 2),
        device_class=sensor.DEVICE_CLASS_ENERGY,
        icon="mdi:solar-power",
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    # WindSensor/WindSpeedSensor
    OverkizSensorDescription(
        key="core:WindSpeedState",
        name="Wind Speed",
        value=lambda value: round(value, 2),
        icon="mdi:weather-windy",
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    # SmokeSensor/SmokeSensor
    OverkizSensorDescription(
        key="io:SensorRoomState",
        name="Sensor Room",
        value=lambda value: str(value).capitalize(),
        entity_registry_enabled_default=False,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the TaHoma sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities = []

    key_supported_states = {
        description.key: description for description in SENSOR_DESCRIPTIONS
    }

    for device in coordinator.data.values():
        for state in device.states:
            description = key_supported_states.get(state.name)
            if description:
                entities.append(
                    TahomaStateSensor(
                        device.deviceurl,
                        coordinator,
                        description,
                    )
                )

    async_add_entities(entities)


class TahomaStateSensor(OverkizDescriptiveEntity, SensorEntity):
    """Representation of a TaHoma Sensor."""

    @property
    def state(self):
        """Return the value of the sensor."""
        state = self.device.states[self.entity_description.key]

        # Transform the value with a lambda function
        if hasattr(self.entity_description, "value"):
            return self.entity_description.value(state.value)

        return state.value
