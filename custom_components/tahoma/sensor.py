"""Support for Overkiz sensors."""
from __future__ import annotations

from typing import Any

from homeassistant.components import sensor
from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    ENERGY_WATT_HOUR,
    LIGHT_LUX,
    PERCENTAGE,
    POWER_WATT,
    SIGNAL_STRENGTH_DECIBELS,
    TEMP_CELSIUS,
    TIME_SECONDS,
    VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
    VOLUME_LITERS,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, OverkizAttribute, OverkizState
from .coordinator import OverkizDataUpdateCoordinator
from .entity import OverkizDescriptiveEntity, OverkizEntity, OverkizSensorDescription

HOMEKIT_STACK = "HomekitStack"

SENSOR_DESCRIPTIONS = [
    OverkizSensorDescription(
        key=OverkizState.CORE_BATTERY_LEVEL,
        name="Battery Level",
        native_unit_of_measurement=PERCENTAGE,
        device_class=sensor.DEVICE_CLASS_BATTERY,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key=OverkizState.CORE_BATTERY,
        name="Battery",
        device_class=sensor.DEVICE_CLASS_BATTERY,
        native_value=lambda value: str(value).capitalize(),
    ),
    OverkizSensorDescription(
        key=OverkizState.CORE_RSSI_LEVEL,
        name="RSSI Level",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        device_class=sensor.DEVICE_CLASS_SIGNAL_STRENGTH,
        state_class=STATE_CLASS_MEASUREMENT,
        native_value=lambda value: round(value),
    ),
    OverkizSensorDescription(
        key=OverkizState.CORE_EXPECTED_NUMBER_OF_SHOWER,
        name="Expected Number Of Shower",
        icon="mdi:shower-head",
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key=OverkizState.CORE_NUMBER_OF_SHOWER_REMAINING,
        name="Number of Shower Remaining",
        icon="mdi:shower-head",
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    # V40 is measured in litres (L) and shows the amount of warm (mixed) water with a temperature of 40 C, which can be drained from a switched off electric water heater.
    OverkizSensorDescription(
        key=OverkizState.CORE_V40_WATER_VOLUME_ESTIMATION,
        name="Water Volume Estimation at 40 °C",
        icon="mdi:water",
        native_unit_of_measurement=VOLUME_LITERS,
        entity_registry_enabled_default=False,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key=OverkizState.CORE_WATER_CONSUMPTION,
        name="Water Consumption",
        icon="mdi:water",
        native_unit_of_measurement=VOLUME_LITERS,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key=OverkizState.IO_OUTLET_ENGINE,
        name="Outlet Engine",
        icon="mdi:fan-chevron-down",
        native_unit_of_measurement=VOLUME_LITERS,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key=OverkizState.IO_INLET_ENGINE,
        name="Inlet Engine",
        icon="mdi:fan-chevron-up",
        native_unit_of_measurement=VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key=OverkizState.HLRRWIFI_ROOM_TEMPERATURE,
        name="Room Temperature",
        device_class=sensor.DEVICE_CLASS_TEMPERATURE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key=OverkizState.IO_MIDDLE_WATER_TEMPERATURE,
        name="Middle Water Temperature",
        device_class=sensor.DEVICE_CLASS_TEMPERATURE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key=OverkizState.CORE_FOSSIL_ENERGY_CONSUMPTION,
        name="Fossil Energy Consumption",
        device_class=sensor.DEVICE_CLASS_ENERGY,
    ),
    OverkizSensorDescription(
        key=OverkizState.CORE_GAS_CONSUMPTION,
        name="Gas Consumption",
    ),
    OverkizSensorDescription(
        key=OverkizState.CORE_THERMAL_ENERGY_CONSUMPTION,
        name="Thermal Energy Consumption",
    ),
    # LightSensor/LuminanceSensor
    OverkizSensorDescription(
        key=OverkizState.CORE_LUMINANCE,
        name="Luminance",
        device_class=sensor.DEVICE_CLASS_ILLUMINANCE,
        native_unit_of_measurement=LIGHT_LUX,  # core:MeasuredValueType = core:LuminanceInLux
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    # ElectricitySensor/CumulativeElectricPowerConsumptionSensor
    OverkizSensorDescription(
        key=OverkizState.CORE_ELECTRICITY_ENERGY_CONSUMPTION,
        name="Electric Energy Consumption",
        device_class=sensor.DEVICE_CLASS_ENERGY,
        native_unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh (not for modbus:YutakiV2DHWElectricalEnergyConsumptionComponent)
        state_class=STATE_CLASS_TOTAL_INCREASING,  # core:MeasurementCategory attribute = electric/overall
    ),
    OverkizSensorDescription(
        key=OverkizState.CORE_ELECTRIC_POWER_CONSUMPTION,
        name="Electric Power Consumption",
        device_class=sensor.DEVICE_CLASS_POWER,
        native_unit_of_measurement=POWER_WATT,  # core:MeasuredValueType = core:ElectricalEnergyInWh (not for modbus:YutakiV2DHWElectricalEnergyConsumptionComponent)
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key=OverkizState.CORE_CONSUMPTION_TARIFF1,
        name="Consumption Tariff 1",
        device_class=sensor.DEVICE_CLASS_ENERGY,
        native_unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key=OverkizState.CORE_CONSUMPTION_TARIFF2,
        name="Consumption Tariff 2",
        device_class=sensor.DEVICE_CLASS_ENERGY,
        native_unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key=OverkizState.CORE_CONSUMPTION_TARIFF3,
        name="Consumption Tariff 3",
        device_class=sensor.DEVICE_CLASS_ENERGY,
        native_unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key=OverkizState.CORE_CONSUMPTION_TARIFF4,
        name="Consumption Tariff 4",
        device_class=sensor.DEVICE_CLASS_ENERGY,
        native_unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key=OverkizState.CORE_CONSUMPTION_TARIFF5,
        name="Consumption Tariff 5",
        device_class=sensor.DEVICE_CLASS_ENERGY,
        native_unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key=OverkizState.CORE_CONSUMPTION_TARIFF6,
        name="Consumption Tariff 6",
        device_class=sensor.DEVICE_CLASS_ENERGY,
        native_unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key=OverkizState.CORE_CONSUMPTION_TARIFF7,
        name="Consumption Tariff 7",
        device_class=sensor.DEVICE_CLASS_ENERGY,
        native_unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key=OverkizState.CORE_CONSUMPTION_TARIFF8,
        name="Consumption Tariff 8",
        device_class=sensor.DEVICE_CLASS_ENERGY,
        native_unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key=OverkizState.CORE_CONSUMPTION_TARIFF9,
        name="Consumption Tariff 9",
        device_class=sensor.DEVICE_CLASS_ENERGY,
        native_unit_of_measurement=ENERGY_WATT_HOUR,  # core:MeasuredValueType = core:ElectricalEnergyInWh
        entity_registry_enabled_default=False,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    # HumiditySensor/RelativeHumiditySensor
    OverkizSensorDescription(
        key=OverkizState.CORE_RELATIVE_HUMIDITY,
        name="Relative Humidity",
        native_value=lambda value: round(value, 2),
        device_class=sensor.DEVICE_CLASS_HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,  # core:MeasuredValueType = core:RelativeValueInPercentage
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    # TemperatureSensor/TemperatureSensor
    OverkizSensorDescription(
        key=OverkizState.CORE_TEMPERATURE,
        name="Temperature",
        native_value=lambda value: round(value, 2),
        device_class=sensor.DEVICE_CLASS_TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,  # core:MeasuredValueType = core:TemperatureInCelcius
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    # WeatherSensor/WeatherForecastSensor
    OverkizSensorDescription(
        key=OverkizState.CORE_WEATHER_STATUS,
        name="Weather Status",
        device_class=sensor.DEVICE_CLASS_TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key=OverkizState.CORE_MINIMUM_TEMPERATURE,
        name="Minimum Temperature",
        device_class=sensor.DEVICE_CLASS_TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    OverkizSensorDescription(
        key=OverkizState.CORE_MAXIMUM_TEMPERATURE,
        name="Maximum Temperature",
        device_class=sensor.DEVICE_CLASS_TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    # AirSensor/COSensor
    OverkizSensorDescription(
        key=OverkizState.CORE_CO_CONCENTRATION,
        name="CO Concentration",
        device_class=sensor.DEVICE_CLASS_CO,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    # AirSensor/CO2Sensor
    OverkizSensorDescription(
        key=OverkizState.CORE_CO2_CONCENTRATION,
        name="CO2 Concentration",
        device_class=sensor.DEVICE_CLASS_CO2,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    # SunSensor/SunEnergySensor
    OverkizSensorDescription(
        key=OverkizState.CORE_SUN_ENERGY,
        name="Sun Energy",
        native_value=lambda value: round(value, 2),
        device_class=sensor.DEVICE_CLASS_ENERGY,
        icon="mdi:solar-power",
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    # WindSensor/WindSpeedSensor
    OverkizSensorDescription(
        key=OverkizState.CORE_WIND_SPEED,
        name="Wind Speed",
        native_value=lambda value: round(value, 2),
        icon="mdi:weather-windy",
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    # SmokeSensor/SmokeSensor
    OverkizSensorDescription(
        key=OverkizState.IO_SENSOR_ROOM,
        name="Sensor Room",
        native_value=lambda value: str(value).capitalize(),
        entity_registry_enabled_default=False,
    ),
    OverkizSensorDescription(
        key=OverkizState.IO_PRIORITY_LOCK_ORIGINATOR,
        name="Priority Lock Originator",
        native_value=lambda value: str(value).capitalize(),
        icon="mdi:lock",
        entity_registry_enabled_default=False,
    ),
    OverkizSensorDescription(
        key=OverkizState.CORE_PRIORITY_LOCK_TIMER,
        name="Priority Lock Timer",
        icon="mdi:lock-clock",
        native_unit_of_measurement=TIME_SECONDS,
        entity_registry_enabled_default=False,
    ),
    OverkizSensorDescription(
        key=OverkizState.CORE_DISCRETE_RSSI_LEVEL,
        name="Discrete RSSI Level",
        entity_registry_enabled_default=False,
        native_value=lambda value: str(value).capitalize(),
        device_class=sensor.DEVICE_CLASS_SIGNAL_STRENGTH,
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
        description.key: description for description in SENSOR_DESCRIPTIONS
    }

    for device in coordinator.data.values():
        for state in device.definition.states:
            if description := key_supported_states.get(state.qualified_name):
                entities.append(
                    OverkizStateSensor(
                        device.device_url,
                        coordinator,
                        description,
                    )
                )

        if device.widget == HOMEKIT_STACK:
            entities.append(
                OverkizHomeKitSetupCodeSensor(
                    device.device_url,
                    coordinator,
                )
            )

    async_add_entities(entities)


class OverkizStateSensor(OverkizDescriptiveEntity, SensorEntity):
    """Representation of an Overkiz Sensor."""

    @property
    def state(self):
        """Return the value of the sensor."""
        state = self.device.states.get(self.entity_description.key)

        if not state:
            return None

        # Transform the value with a lambda function
        if hasattr(self.entity_description, "native_value"):
            return self.entity_description.native_value(state.value)

        return state.value


class OverkizHomeKitSetupCodeSensor(OverkizEntity, SensorEntity):
    """Representation of an Overkiz HomeKit Setup Code."""

    def __init__(self, device_url: str, coordinator: OverkizDataUpdateCoordinator):
        """Initialize the device."""
        super().__init__(device_url, coordinator)
        self._attr_name = "HomeKit Setup Code"
        self._attr_icon = "mdi:shield-home"

    @property
    def state(self):
        """Return the value of the sensor."""
        return self.device.attributes.get(OverkizAttribute.HOMEKIT_SETUP_CODE).value

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""
        # By default this sensor will be listed at a virtual HomekitStack device,
        # but it makes more sense to show this at the gateway device in the entity registry.
        return {
            "identifiers": {(DOMAIN, self.executor.get_gateway_id())},
        }
