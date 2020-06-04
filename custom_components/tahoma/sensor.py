"""Support for Tahoma sensors."""
from datetime import timedelta
import logging

from homeassistant.const import ATTR_BATTERY_LEVEL, TEMP_CELSIUS, UNIT_PERCENTAGE
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, TAHOMA_TYPES
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Tahoma sensors from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]

    entities = []
    controller = data.get("controller")

    for device in data.get("devices"):
        if TAHOMA_TYPES[device.uiclass] == "sensor":
            entities.append(TahomaSensor(device, controller))

    async_add_entities(entities)


class TahomaSensor(TahomaDevice, Entity):
    """Representation of a Tahoma Sensor."""

    def __init__(self, tahoma_device, controller):
        """Initialize the sensor."""
        self.current_value = None
        self._available = False
        super().__init__(tahoma_device, controller)

    @property
    def state(self):
        """Return the name of the sensor."""
        return self.current_value

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""

        if self.tahoma_device.uiclass == "TemperatureSensor":
            return TEMP_CELSIUS

        if self.tahoma_device.uiclass == "HumiditySensor":
            return UNIT_PERCENTAGE

        if self.tahoma_device.uiclass == "LightSensor":
            return "lx"

        return None

    def update(self):
        """Update the state."""
        self.controller.get_states([self.tahoma_device])
        if self.tahoma_device.type == "io:LightIOSystemSensor":
            self.current_value = self.tahoma_device.active_states["core:LuminanceState"]
            self._available = bool(
                self.tahoma_device.active_states.get("core:StatusState") == "available"
            )
        if self.tahoma_device.type == "io:SomfyContactIOSystemSensor":
            self.current_value = self.tahoma_device.active_states["core:ContactState"]
            self._available = bool(
                self.tahoma_device.active_states.get("core:StatusState") == "available"
            )
        if self.tahoma_device.type == "io:SomfyBasicContactIOSystemSensor":
            self.current_value = self.tahoma_device.active_states["core:ContactState"]
            self._available = bool(
                self.tahoma_device.active_states.get("core:StatusState") == "available"
            )
        if self.tahoma_device.type == "rtds:RTDSContactSensor":
            self.current_value = self.tahoma_device.active_states["core:ContactState"]
            self._available = True
        if self.tahoma_device.type == "rtds:RTDSMotionSensor":
            self.current_value = self.tahoma_device.active_states["core:OccupancyState"]
            self._available = True
        if self.tahoma_device.type == "io:TemperatureIOSystemSensor":
            self.current_value = round(
                float(self.tahoma_device.active_states["core:TemperatureState"]), 1
            )
            self._available = True

        _LOGGER.debug("Update %s, value: %d", self._name, self.current_value)
