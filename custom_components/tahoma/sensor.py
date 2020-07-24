"""Support for TaHoma sensors."""
from datetime import timedelta
import logging
from typing import Optional

from homeassistant.components.sensor import DOMAIN as SENSOR
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_TEMPERATURE,
    ENERGY_WATT_HOUR,
    POWER_WATT,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    TEMP_KELVIN,
    UNIT_PERCENTAGE,
)
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)

CORE_CO2_CONCENTRATION_STATE = "core:CO2ConcentrationState"
CORE_CO_CONCENTRATION_STATE = "core:COConcentrationState"
CORE_ELECTRIC_ENERGY_CONSUMPTION_STATE = "core:ElectricEnergyConsumptionState"
CORE_ELECTRIC_POWER_CONSUMPTION_STATE = "core:ElectricPowerConsumptionState"
CORE_GAS_CONSUMPTION_STATE = "core:GasConsumptionState"
CORE_LUMINANCE_STATE = "core:LuminanceState"
CORE_MEASURED_VALUE_TYPE = "core:MeasuredValueType"
CORE_RELATIVE_HUMIDITY_STATE = "core:RelativeHumidityState"
CORE_SUN_ENERGY_STATE = "core:SunEnergyState"
CORE_TEMPERATURE_IN_CELCIUS = "core:TemperatureInCelcius"
CORE_TEMPERATURE_IN_CELSIUS = "core:TemperatureInCelsius"
CORE_TEMPERATURE_IN_FAHRENHEIT = "core:TemperatureInFahrenheit"
CORE_TEMPERATURE_IN_KELVIN = "core:TemperatureInKelvin"
CORE_TEMPERATURE_STATE = "core:TemperatureState"
CORE_THERMAL_ENERGY_CONSUMPTION_STATE = "core:ThermalEnergyConsumptionState"
CORE_WINDSPEED_STATE = "core:WindSpeedState"

DEVICE_CLASS_CO = "co"
DEVICE_CLASS_CO2 = "co2"
DEVICE_CLASS_SUN_ENERGY = "sun_energy"
DEVICE_CLASS_WIND_SPEED = "wind_speed"

ICON_AIR_FILTER = "mdi:air-filter"
ICON_PERIODIC_TABLE_CO2 = "mdi:periodic-table-co2"
ICON_SOLAR_POWER = "mdi:solar-power"
ICON_WEATHER_WINDY = "mdi:weather-windy"

UNIT_LX = "lx"

TAHOMA_SENSOR_DEVICE_CLASSES = {
    "TemperatureSensor": DEVICE_CLASS_TEMPERATURE,
    "HumiditySensor": DEVICE_CLASS_HUMIDITY,
    "LightSensor": DEVICE_CLASS_ILLUMINANCE,
    "ElectricitySensor": DEVICE_CLASS_POWER,
    "COSensor": DEVICE_CLASS_CO,
    "CO2Sensor": DEVICE_CLASS_CO2,
    "RelativeHumiditySensor": DEVICE_CLASS_HUMIDITY,
    "WindSensor": DEVICE_CLASS_WIND_SPEED,
    "SunSensor": DEVICE_CLASS_SUN_ENERGY,
}


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    controller = data.get("controller")

    entities = [
        TahomaSensor(device, controller) for device in data.get("devices").get(SENSOR)
    ]

    async_add_entities(entities)


class TahomaSensor(TahomaDevice, Entity):
    """Representation of a TaHoma Sensor."""

    @property
    def state(self):
        """Return the value of the sensor."""
        state = self.select_state(
            CORE_CO2_CONCENTRATION_STATE,
            CORE_CO_CONCENTRATION_STATE,
            CORE_ELECTRIC_ENERGY_CONSUMPTION_STATE,
            CORE_ELECTRIC_POWER_CONSUMPTION_STATE,
            CORE_GAS_CONSUMPTION_STATE,
            CORE_LUMINANCE_STATE,
            CORE_RELATIVE_HUMIDITY_STATE,
            CORE_SUN_ENERGY_STATE,
            CORE_TEMPERATURE_STATE,
            CORE_THERMAL_ENERGY_CONSUMPTION_STATE,
            CORE_WINDSPEED_STATE,
        )
        return round(state, 2)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        TEMPERATURE_UNIT = {
            CORE_TEMPERATURE_IN_CELSIUS: TEMP_CELSIUS,
            CORE_TEMPERATURE_IN_CELCIUS: TEMP_CELSIUS,
            CORE_TEMPERATURE_IN_KELVIN: TEMP_KELVIN,
            CORE_TEMPERATURE_IN_FAHRENHEIT: TEMP_FAHRENHEIT,
        }.get(self.device.attributes.get(CORE_MEASURED_VALUE_TYPE), TEMP_CELSIUS,)
        state = self.select_state(
            CORE_CO2_CONCENTRATION_STATE,
            CORE_CO_CONCENTRATION_STATE,
            CORE_ELECTRIC_ENERGY_CONSUMPTION_STATE,
            CORE_ELECTRIC_POWER_CONSUMPTION_STATE,
            CORE_LUMINANCE_STATE,
            CORE_RELATIVE_HUMIDITY_STATE,
            CORE_TEMPERATURE_STATE,
        )
        return {
            CORE_TEMPERATURE_STATE: TEMPERATURE_UNIT,
            CORE_RELATIVE_HUMIDITY_STATE: UNIT_PERCENTAGE,
            CORE_LUMINANCE_STATE: UNIT_LX,
            CORE_ELECTRIC_POWER_CONSUMPTION_STATE: POWER_WATT,
            CORE_ELECTRIC_ENERGY_CONSUMPTION_STATE: ENERGY_WATT_HOUR,
            CORE_CO_CONCENTRATION_STATE: CONCENTRATION_PARTS_PER_MILLION,
            CORE_CO2_CONCENTRATION_STATE: CONCENTRATION_PARTS_PER_MILLION,
        }.get(state)

    @property
    def icon(self) -> Optional[str]:
        """Return the icon to use in the frontend, if any."""
        icons = {
            DEVICE_CLASS_CO: ICON_AIR_FILTER,
            DEVICE_CLASS_CO2: ICON_PERIODIC_TABLE_CO2,
            DEVICE_CLASS_WIND_SPEED: ICON_WEATHER_WINDY,
            DEVICE_CLASS_SUN_ENERGY: ICON_SOLAR_POWER,
        }

        return icons.get(self.device_class)

    @property
    def device_class(self) -> Optional[str]:
        """Return the device class of this entity if any."""
        return (
            TAHOMA_SENSOR_DEVICE_CLASSES.get(self.device.widget)
            or TAHOMA_SENSOR_DEVICE_CLASSES.get(self.device.ui_class)
            or None
        )
