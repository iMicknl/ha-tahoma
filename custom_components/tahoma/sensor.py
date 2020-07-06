"""Support for TaHoma sensors."""
from datetime import timedelta
import logging
from typing import Optional

from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    CONCENTRATION_PARTS_PER_MILLION,
    ENERGY_KILO_WATT_HOUR,
    POWER_WATT,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    TEMP_KELVIN,
    UNIT_PERCENTAGE,
)
from homeassistant.helpers.entity import Entity

from .const import (
    CORE_CO2_CONCENTRATION_STATE,
    CORE_CO_CONCENTRATION_STATE,
    CORE_ELECTRIC_ENERGY_CONSUMPTION_STATE,
    CORE_ELECTRIC_POWER_CONSUMPTION_STATE,
    CORE_LUMINANCE_STATE,
    CORE_MEASURED_VALUE_TYPE,
    CORE_RELATIVE_HUMIDITY_STATE,
    CORE_SUN_ENERGY_STATE,
    CORE_TEMPERATURE_STATE,
    CORE_WINDSPEED_STATE,
    DEVICE_CLASS_CO,
    DEVICE_CLASS_CO2,
    DEVICE_CLASS_SUN_ENERGY,
    DEVICE_CLASS_WIND_SPEED,
    DOMAIN,
    TAHOMA_SENSOR_DEVICE_CLASSES,
    TAHOMA_TYPES,
)
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)


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

    def __init__(self, tahoma_device, controller):
        """Initialize the sensor."""
        self.current_value = None

        super().__init__(tahoma_device, controller)

    @property
    def state(self):
        """Return the name of the sensor."""
        return self.current_value

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""

        states = self.tahoma_device.active_states

        if CORE_TEMPERATURE_STATE in states:
            return {
                "core:TemperatureInCelcius": TEMP_CELSIUS,
                "core:TemperatureInKelvin": TEMP_KELVIN,
                "core:TemperatureInFahrenheit": TEMP_FAHRENHEIT,
            }.get(
                self.tahoma_device.attributes.get(CORE_MEASURED_VALUE_TYPE),
                TEMP_CELSIUS,
            )

        if CORE_RELATIVE_HUMIDITY_STATE in states:
            return UNIT_PERCENTAGE

        if CORE_LUMINANCE_STATE in states:
            return "lx"

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
            DEVICE_CLASS_CO: "mdi:air-filter",
            DEVICE_CLASS_CO2: "mdi:periodic-table-co2",
            DEVICE_CLASS_WIND_SPEED: "mdi:weather-windy",
            DEVICE_CLASS_SUN_ENERGY: "mdi:solar-power",
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

    def update(self):
        """Update the state."""
        if self.should_wait():
            self.schedule_update_ha_state(True)
            return

        self.controller.get_states([self.tahoma_device])

        states = self.tahoma_device.active_states

        if CORE_LUMINANCE_STATE in states:
            self.current_value = states.get(CORE_LUMINANCE_STATE)

        if CORE_RELATIVE_HUMIDITY_STATE in states:
            self.current_value = float(
                "{:.2f}".format(states.get(CORE_RELATIVE_HUMIDITY_STATE))
            )

        if CORE_TEMPERATURE_STATE in states:
            self.current_value = float(
                "{:.2f}".format(states.get(CORE_TEMPERATURE_STATE))
            )

        if CORE_ELECTRIC_POWER_CONSUMPTION_STATE in states:
            self.current_value = float(
                "{:.2f}".format(states.get(CORE_ELECTRIC_POWER_CONSUMPTION_STATE))
            )

        if CORE_ELECTRIC_ENERGY_CONSUMPTION_STATE in states:
            self.current_value = (
                float(
                    "{:.2f}".format(states.get(CORE_ELECTRIC_ENERGY_CONSUMPTION_STATE))
                )
                / 1000
            )

        if CORE_CO_CONCENTRATION_STATE in states:
            self.current_value = int(states.get(CORE_CO_CONCENTRATION_STATE))

        if CORE_CO2_CONCENTRATION_STATE in states:
            self.current_value = int(states.get(CORE_CO2_CONCENTRATION_STATE))

        if CORE_WINDSPEED_STATE in states:
            self.current_value = float(
                "{:.2f}".format(states.get(CORE_WINDSPEED_STATE))
            )

        if CORE_SUN_ENERGY_STATE in states:
            self.current_value = float(
                "{:.2f}".format(states.get(CORE_SUN_ENERGY_STATE))
            )
