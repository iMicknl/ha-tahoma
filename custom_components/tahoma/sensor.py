"""Support for TaHoma sensors."""
import logging
from typing import Optional

from homeassistant.components.sensor import DOMAIN as SENSOR
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    DEVICE_CLASS_CO,
    DEVICE_CLASS_CO2,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_TEMPERATURE,
    ENERGY_KILO_WATT_HOUR,
    ENERGY_WATT_HOUR,
    PERCENTAGE,
    POWER_KILO_WATT,
    POWER_WATT,
    SPEED_METERS_PER_SECOND,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    TEMP_KELVIN,
    VOLUME_CUBIC_METERS,
    VOLUME_LITERS,
)

try:  # Breaking change in 2021.8
    from homeassistant.const import ELECTRIC_CURRENT_AMPERE
except ImportError:
    from homeassistant.const import ELECTRICAL_CURRENT_AMPERE as ELECTRIC_CURRENT_AMPERE

try:  # Breaking change in 2021.8
    from homeassistant.const import ELECTRIC_POTENTIAL_VOLT
except ImportError:
    from homeassistant.const import VOLT as ELECTRIC_POTENTIAL_VOLT

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .state_sensor import TahomaStateSensor, SUPPORTED_STATES
from .tahoma_entity import TahomaEntity

_LOGGER = logging.getLogger(__name__)

CORE_CO2_CONCENTRATION_STATE = "core:CO2ConcentrationState"
CORE_CO_CONCENTRATION_STATE = "core:COConcentrationState"
CORE_ELECTRIC_ENERGY_CONSUMPTION_STATE = "core:ElectricEnergyConsumptionState"
CORE_ELECTRIC_POWER_CONSUMPTION_STATE = "core:ElectricPowerConsumptionState"
CORE_FOSSIL_ENERGY_CONSUMPTION_STATE = "core:FossilEnergyConsumptionState"
CORE_GAS_CONSUMPTION_STATE = "core:GasConsumptionState"
CORE_MEASURED_VALUE_TYPE = "core:MeasuredValueType"
CORE_RELATIVE_HUMIDITY_STATE = "core:RelativeHumidityState"
CORE_SUN_ENERGY_STATE = "core:SunEnergyState"
CORE_TEMPERATURE_STATE = "core:TemperatureState"
CORE_THERMAL_ENERGY_CONSUMPTION_STATE = "core:ThermalEnergyConsumptionState"
CORE_WATER_CONSUMPTION_STATE = "core:WaterConsumptionState"
CORE_WINDSPEED_STATE = "core:WindSpeedState"


DEVICE_CLASS_SUN_ENERGY = "sun_energy"
DEVICE_CLASS_WIND_SPEED = "wind_speed"

ICON_MOLECULE_CO = "mdi:molecule-co"
ICON_MOLECULE_CO2 = "mdi:molecule-co2"
ICON_SOLAR_POWER = "mdi:solar-power"
ICON_WEATHER_WINDY = "mdi:weather-windy"

UNIT_LX = "lx"

TAHOMA_SENSOR_DEVICE_CLASSES = {
    "CO2Sensor": DEVICE_CLASS_CO2,
    "COSensor": DEVICE_CLASS_CO,
    "ElectricitySensor": DEVICE_CLASS_POWER,
    "HumiditySensor": DEVICE_CLASS_HUMIDITY,
    "RelativeHumiditySensor": DEVICE_CLASS_HUMIDITY,
    "SunSensor": DEVICE_CLASS_SUN_ENERGY,
    "TemperatureSensor": DEVICE_CLASS_TEMPERATURE,
    "WindSensor": DEVICE_CLASS_WIND_SPEED,
}
# From https://www.tahomalink.com/enduser-mobile-web/steer-html5-client/tahoma/bootstrap.js
UNITS = {
    "core:TemperatureInCelcius": TEMP_CELSIUS,
    "core:TemperatureInCelsius": TEMP_CELSIUS,
    "core:TemperatureInKelvin": TEMP_KELVIN,
    "core:TemperatureInFahrenheit": TEMP_FAHRENHEIT,
    "core:LuminanceInLux": UNIT_LX,
    "core:ElectricCurrentInAmpere": ELECTRIC_CURRENT_AMPERE,
    "core:VoltageInVolt": ELECTRIC_POTENTIAL_VOLT,
    "core:ElectricalEnergyInWh": ENERGY_WATT_HOUR,
    "core:ElectricalEnergyInKWh": ENERGY_KILO_WATT_HOUR,
    "core:ElectricalEnergyInMWh": f"M{ENERGY_WATT_HOUR}",
    "core:ElectricalPowerInW": POWER_WATT,
    "core:ElectricalPowerInKW": POWER_KILO_WATT,
    "core:ElectricalPowerInMW": f"M{POWER_WATT}",
    "core:FlowInMeterCubePerHour": VOLUME_CUBIC_METERS,
    "core:LinearSpeedInMeterPerSecond": SPEED_METERS_PER_SECOND,
    "core:RelativeValueInPercentage": PERCENTAGE,
    "core:VolumeInCubicMeter": VOLUME_CUBIC_METERS,
    "core:VolumeInLiter": VOLUME_LITERS,
    "core:FossilEnergyInWh": ENERGY_WATT_HOUR,
    "core:FossilEnergyInKWh": ENERGY_KILO_WATT_HOUR,
    "core:FossilEnergyInMWh": f"M{ENERGY_WATT_HOUR}",
    "meters_seconds": SPEED_METERS_PER_SECOND,
}

UNITS_BY_DEVICE_CLASS = {
    DEVICE_CLASS_CO2: CONCENTRATION_PARTS_PER_MILLION,
    DEVICE_CLASS_CO: CONCENTRATION_PARTS_PER_MILLION,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the TaHoma sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities = [
        TahomaSensor(device.deviceurl, coordinator)
        for device in data["platforms"][SENSOR]
        if device.states
    ]

    key_supported_states = {
        description.key: description for description in SUPPORTED_STATES
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


class TahomaSensor(TahomaEntity, Entity):
    """Representation of a TaHoma Sensor."""

    @property
    def state(self):
        """Return the value of the sensor."""
        state = self.select_state(
            CORE_CO2_CONCENTRATION_STATE,
            CORE_CO_CONCENTRATION_STATE,
            CORE_ELECTRIC_ENERGY_CONSUMPTION_STATE,
            CORE_ELECTRIC_POWER_CONSUMPTION_STATE,
            CORE_FOSSIL_ENERGY_CONSUMPTION_STATE,
            CORE_GAS_CONSUMPTION_STATE,
            CORE_RELATIVE_HUMIDITY_STATE,
            CORE_SUN_ENERGY_STATE,
            CORE_TEMPERATURE_STATE,
            CORE_THERMAL_ENERGY_CONSUMPTION_STATE,
            CORE_WINDSPEED_STATE,
            CORE_WATER_CONSUMPTION_STATE,
        )
        return round(state, 2) if state is not None else None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        if (
            self.device.attributes
            and CORE_MEASURED_VALUE_TYPE in self.device.attributes
        ):
            attribute = self.device.attributes[CORE_MEASURED_VALUE_TYPE]
            return UNITS.get(attribute.value)

        if self.device_class in UNITS_BY_DEVICE_CLASS:
            return UNITS_BY_DEVICE_CLASS.get(self.device_class)

        return None

    @property
    def icon(self) -> Optional[str]:
        """Return the icon to use in the frontend, if any."""
        icons = {
            DEVICE_CLASS_CO: ICON_MOLECULE_CO,
            DEVICE_CLASS_CO2: ICON_MOLECULE_CO2,
            DEVICE_CLASS_WIND_SPEED: ICON_WEATHER_WINDY,
            DEVICE_CLASS_SUN_ENERGY: ICON_SOLAR_POWER,
        }

        return icons.get(self.device_class)

    @property
    def device_class(self) -> Optional[str]:
        """Return the device class of this entity if any."""
        return TAHOMA_SENSOR_DEVICE_CLASSES.get(
            self.device.widget
        ) or TAHOMA_SENSOR_DEVICE_CLASSES.get(self.device.ui_class)
