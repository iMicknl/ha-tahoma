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
    UNIT_PERCENTAGE,
)
from homeassistant.helpers.entity import Entity

from .const import (
    CORE_CO2_CONCENTRATION_STATE,
    CORE_ELECTRIC_ENERGY_CONSUMPTION_STATE,
    CORE_ELECTRIC_POWER_CONSUMPTION_STATE,
    CORE_LUMINANCE_STATE,
    CORE_RELATIVE_HUMIDITY_STATE,
    CORE_TEMPERATURE_STATE,
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

    entities = []
    controller = data.get("controller")

    for device in data.get("devices"):
        if TAHOMA_TYPES[device.uiclass] == "sensor":
            entities.append(TahomaSensor(device, controller))

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

        if self.tahoma_device.uiclass == "TemperatureSensor":
            # TODO Retrieve core:MeasuredValueType to understand if it is Celsius or Kelvin
            return TEMP_CELSIUS

        if self.tahoma_device.uiclass == "HumiditySensor":
            return UNIT_PERCENTAGE

        if self.tahoma_device.uiclass == "LightSensor":
            return "lx"

        if CORE_ELECTRIC_POWER_CONSUMPTION_STATE in self.tahoma_device.active_states:
            return POWER_WATT

        if CORE_ELECTRIC_ENERGY_CONSUMPTION_STATE in self.tahoma_device.active_states:
            return ENERGY_KILO_WATT_HOUR

        if self.tahoma_device.uiclass == "AirSensor":
            return CONCENTRATION_PARTS_PER_MILLION

        return None

    @property
    def icon(self) -> Optional[str]:
        """Return the icon to use in the frontend, if any."""

        if self.tahoma_device.uiclass == "AirSensor":
            return "mdi:periodic-table-co2"

        return None

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
        self.controller.get_states([self.tahoma_device])

        if CORE_LUMINANCE_STATE in self.tahoma_device.active_states:
            self.current_value = self.tahoma_device.active_states.get(
                CORE_LUMINANCE_STATE
            )

        if CORE_RELATIVE_HUMIDITY_STATE in self.tahoma_device.active_states:
            self.current_value = float(
                "{:.2f}".format(
                    self.tahoma_device.active_states.get(CORE_RELATIVE_HUMIDITY_STATE)
                )
            )

        if CORE_TEMPERATURE_STATE in self.tahoma_device.active_states:
            self.current_value = float(
                "{:.2f}".format(
                    self.tahoma_device.active_states.get(CORE_TEMPERATURE_STATE)
                )
            )

        if CORE_ELECTRIC_POWER_CONSUMPTION_STATE in self.tahoma_device.active_states:
            self.current_value = float(
                "{:.2f}".format(
                    self.tahoma_device.active_states.get(
                        CORE_ELECTRIC_POWER_CONSUMPTION_STATE
                    )
                )
            )

        if CORE_ELECTRIC_ENERGY_CONSUMPTION_STATE in self.tahoma_device.active_states:
            self.current_value = (
                float(
                    "{:.2f}".format(
                        self.tahoma_device.active_states.get(
                            CORE_ELECTRIC_ENERGY_CONSUMPTION_STATE
                        )
                    )
                )
                / 1000
            )

        if CORE_CO2_CONCENTRATION_STATE in self.tahoma_device.active_states:
            self.current_value = int(
                self.tahoma_device.active_states.get(CORE_CO2_CONCENTRATION_STATE)
            )
