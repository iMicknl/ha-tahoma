"""Support for TaHoma sensors."""
from datetime import timedelta
import logging
from typing import Optional

from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_TEMPERATURE,
    ENERGY_KILO_WATT_HOUR,
    POWER_WATT,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    TEMP_KELVIN,
    UNIT_PERCENTAGE,
)
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, TAHOMA_TYPES
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)

CORE_CO_CONCENTRATION_STATE = "core:COConcentrationState"
CORE_CO2_CONCENTRATION_STATE = "core:CO2ConcentrationState"
CORE_ELECTRIC_ENERGY_CONSUMPTION_STATE = "core:ElectricEnergyConsumptionState"
CORE_ELECTRIC_POWER_CONSUMPTION_STATE = "core:ElectricPowerConsumptionState"
CORE_LUMINANCE_STATE = "core:LuminanceState"
CORE_MEASURED_VALUE_TYPE = "core:MeasuredValueType"
CORE_RELATIVE_HUMIDITY_STATE = "core:RelativeHumidityState"
CORE_SUN_ENERGY_STATE = "core:SunEnergyState"
CORE_TEMPERATURE_IN_CELCIUS = "core:TemperatureInCelcius"
CORE_TEMPERATURE_IN_CELSIUS = "core:TemperatureInCelsius"
CORE_TEMPERATURE_IN_FAHRENHEIT = "core:TemperatureInFahrenheit"
CORE_TEMPERATURE_IN_KELVIN = "core:TemperatureInKelvin"
CORE_TEMPERATURE_STATE = "core:TemperatureState"
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
        TahomaSensor(device, controller)
        for device in data.get("devices")
        if TAHOMA_TYPES[device.uiclass] == "sensor"
    ]

    async_add_entities(entities)


class TahomaSensor(TahomaDevice, Entity):
    """Representation of a TaHoma Sensor."""

    @property
    def state(self):
        """Return the name of the sensor."""

        states = self.tahoma_device.active_states

        if CORE_LUMINANCE_STATE in states:
            return states.get(CORE_LUMINANCE_STATE)

        if CORE_RELATIVE_HUMIDITY_STATE in states:
            return float(states.get(CORE_RELATIVE_HUMIDITY_STATE))

        if CORE_TEMPERATURE_STATE in states:
            return float(states.get(CORE_TEMPERATURE_STATE))

        if CORE_ELECTRIC_POWER_CONSUMPTION_STATE in states:
            return float(states.get(CORE_ELECTRIC_POWER_CONSUMPTION_STATE))

        if CORE_ELECTRIC_ENERGY_CONSUMPTION_STATE in states:
            return float(states.get(CORE_ELECTRIC_ENERGY_CONSUMPTION_STATE)) / 1000

        if CORE_CO_CONCENTRATION_STATE in states:
            return int(states.get(CORE_CO_CONCENTRATION_STATE))

        if CORE_CO2_CONCENTRATION_STATE in states:
            return int(states.get(CORE_CO2_CONCENTRATION_STATE))

        if CORE_WINDSPEED_STATE in states:
            return float("{:.2f}".format(states.get(CORE_WINDSPEED_STATE)))

        if CORE_SUN_ENERGY_STATE in states:
            return float("{:.2f}".format(states.get(CORE_SUN_ENERGY_STATE)))

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        states = self.tahoma_device.active_states

        if CORE_TEMPERATURE_STATE in states:
            return {
                CORE_TEMPERATURE_IN_CELSIUS: TEMP_CELSIUS,
                CORE_TEMPERATURE_IN_CELCIUS: TEMP_CELSIUS,
                CORE_TEMPERATURE_IN_KELVIN: TEMP_KELVIN,
                CORE_TEMPERATURE_IN_FAHRENHEIT: TEMP_FAHRENHEIT,
            }.get(
                self.tahoma_device.attributes.get(CORE_MEASURED_VALUE_TYPE),
                TEMP_CELSIUS,
            )

        if CORE_RELATIVE_HUMIDITY_STATE in states:
            return UNIT_PERCENTAGE

        if CORE_LUMINANCE_STATE in states:
            return UNIT_LX

        if CORE_ELECTRIC_POWER_CONSUMPTION_STATE in states:
            return POWER_WATT

        if CORE_ELECTRIC_ENERGY_CONSUMPTION_STATE in states:
            return ENERGY_KILO_WATT_HOUR

        if (
            CORE_CO_CONCENTRATION_STATE in states
            or CORE_CO2_CONCENTRATION_STATE in states
        ):
            return CONCENTRATION_PARTS_PER_MILLION

        return None

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
            TAHOMA_SENSOR_DEVICE_CLASSES.get(self.tahoma_device.widget)
            or TAHOMA_SENSOR_DEVICE_CLASSES.get(self.tahoma_device.uiclass)
            or None
        )
