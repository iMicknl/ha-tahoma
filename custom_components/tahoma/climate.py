"""Support for Tahoma climate."""
from datetime import timedelta
from time import sleep
import logging
from typing import List, Optional

from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_change
from homeassistant.const import TEMP_CELSIUS, ATTR_TEMPERATURE, EVENT_HOMEASSISTANT_START, \
    STATE_UNKNOWN
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT,
    HVAC_MODE_AUTO,
    PRESET_AWAY,
    PRESET_HOME,
    PRESET_NONE,
    PRESET_SLEEP,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)

from .const import DOMAIN, TAHOMA_TYPES
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=120)

PRESET_FROST_GUARD = "Frost Guard"


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Tahoma sensors from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]

    entities = []
    controller = data.get("controller")

    for device in data.get("devices"):
        if TAHOMA_TYPES[device.uiclass] == "climate":
            if device.widget == "SomfyThermostat":
                entities.append(TahomaClimate(device, controller))

    async_add_entities(entities)


class TahomaClimate(TahomaDevice, ClimateEntity):
    """Representation of a Tahoma thermostat."""

    def __init__(self, tahoma_device, controller):
        """Initialize the sensor."""
        super().__init__(tahoma_device, controller)
        device = "sensor." + \
            self.controller.get_device(
                self.tahoma_device.url.replace("#1", "#2")
            ).label.replace("°", "deg").replace(" ", "_").lower()
        _LOGGER.debug("device: %s", device)
        self._temp_sensor_entity_id = device
        self._current_temp = None
        self._target_temp = None
        self._hvac_modes = [HVAC_MODE_HEAT, HVAC_MODE_AUTO]
        self._hvac_mode = None
        self._preset_mode = None
        self._preset_modes = [
            PRESET_NONE, PRESET_FROST_GUARD, PRESET_SLEEP, PRESET_AWAY, PRESET_HOME]
        self.update_temp(None)

    async def async_added_to_hass(self):
        await super().async_added_to_hass()

        async_track_state_change(
            self.hass, self._temp_sensor_entity_id, self._async_sensor_changed
        )

        @callback
        def _async_startup(event):
            """Init on startup."""
            sensor_state = self.hass.states.get(self._temp_sensor_entity_id)
            if sensor_state and sensor_state.state != STATE_UNKNOWN:
                self.update_temp(sensor_state)

        self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, _async_startup)

    async def _async_sensor_changed(self, entity_id, old_state, new_state):
        """Handle temperature changes."""
        if new_state is None:
            return

        self.update_temp(new_state)
        self.schedule_update_ha_state()

    @callback
    def update_temp(self, state):
        """Update thermostat with latest state from sensor."""
        if state is None:
            state = self.hass.states.get(self._temp_sensor_entity_id)

        try:
            self._current_temp = float(state.state)
        except ValueError as ex:
            _LOGGER.error("Unable to update from sensor: %s", ex)

    def update(self):
        """Update the state."""
        self.apply_action("refreshState")
        self.controller.get_states([self.tahoma_device])
        if self.tahoma_device.active_states[
            'somfythermostat:DerogationHeatingModeState'] == "manualMode":
            self._hvac_mode = HVAC_MODE_HEAT
        else:
            self._hvac_mode = HVAC_MODE_AUTO
        self.update_temp(None)

    @property
    def temperature_sensor(self) -> str:
        """Return the id of the temperature sensor"""
        return self._temp_sensor_entity_id

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        return self._hvac_mode

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return self._hvac_modes

    def set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVAC_MODE_AUTO and self._hvac_mode != HVAC_MODE_AUTO:
            self.apply_action("exitDerogation")
        elif hvac_mode == HVAC_MODE_HEAT and self._hvac_mode != HVAC_MODE_HEAT:
            self.apply_action("setDerogation", self.current_temperature, "further_notice")
        sleep(10)
        self.schedule_update_ha_state()

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_PRESET_MODE | SUPPORT_TARGET_TEMPERATURE

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp.

        Requires SUPPORT_PRESET_MODE.
        """
        return self._preset_mode

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes.

        Requires SUPPORT_PRESET_MODE.
        """
        return self._preset_modes

    def set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        raise NotImplementedError()  # TODO implement

    @property
    def current_temperature(self) -> Optional[float]:
        """Return the current temperature"""
        return self._current_temp

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temp

    def set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        self._target_temp = temperature
        self.schedule_update_ha_state()
