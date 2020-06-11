"""Support for TaHoma sensors."""
from datetime import timedelta
import logging

from homeassistant.const import ATTR_BATTERY_LEVEL, TEMP_CELSIUS, UNIT_PERCENTAGE
from homeassistant.helpers.entity import Entity

from .const import (
    DOMAIN,
    TAHOMA_TYPES,
    CORE_RELATIVE_HUMIDITY_STATE,
    CORE_LUMINANCE_STATE,
    CORE_TEMPERATURE_STATE,
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
            return TEMP_CELSIUS  # TODO Retrieve core:MeasuredValueType to understand if it is Celsius or Kelvin

        if self.tahoma_device.uiclass == "HumiditySensor":
            return UNIT_PERCENTAGE

        if self.tahoma_device.uiclass == "LightSensor":
            return "lx"

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

        _LOGGER.debug("Update %s, value: %d", self._name, self.current_value)
