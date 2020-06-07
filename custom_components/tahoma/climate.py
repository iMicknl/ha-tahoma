"""Support for Tahoma climate."""
from datetime import timedelta
import logging
from typing import List, Optional
import unicodedata

from homeassistant.core import callback, State
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.restore_state import RestoreEntity
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
    SUPPORT_TARGET_TEMPERATURE, ATTR_PRESET_MODE,
)

from .const import DOMAIN, TAHOMA_TYPES
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=120)

HVAC_MODE_KEY = 'somfythermostat:DerogationTypeState'
MAP_HVAC_MODE = {
    "date": HVAC_MODE_AUTO,
    "next_mode": HVAC_MODE_HEAT,
    "further_notice": HVAC_MODE_HEAT
}
PRESET_FREEZE = "freeze"
MAP_PRESET_KEY = {
    HVAC_MODE_AUTO: 'somfythermostat:HeatingModeState',
    HVAC_MODE_HEAT: 'somfythermostat:DerogationHeatingModeState'
}
MAP_PRESET = {
    "sleepingMode": PRESET_SLEEP,
    "atHomeMode": PRESET_HOME,
    "awayMode": PRESET_AWAY,
    "freezeMode": PRESET_FREEZE,
    "manualMode": PRESET_NONE
}
MAP_TARGET_TEMP_KEY = {
    HVAC_MODE_AUTO: 'core:TargetTemperatureState',
    HVAC_MODE_HEAT: 'core:DerogatedTargetTemperatureState'
}
COMMAND_REFRESH = "refreshState"
COMMAND_EXIT_DEROGATION = "exitDerogation"
COMMAND_SET_DEROGATION = "setDerogation"
COMMAND_OPTION_FURTHER_NOTICE = "further_notice"


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


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


class TahomaClimate(TahomaDevice, ClimateEntity, RestoreEntity):
    """Representation of a Tahoma thermostat."""

    def __init__(self, tahoma_device, controller):
        """Initialize the sensor."""
        super().__init__(tahoma_device, controller)
        device1 = "sensor." + \
                  self.controller.get_device(
                      self.tahoma_device.url.replace("#1", "#2")
                  ).label.replace("°", "deg").replace(" ", "_").lower()
        self._temp_sensor_entity_id = remove_accents(device1)
        self._current_temp = None
        self._target_temp = self.tahoma_device.active_states[MAP_TARGET_TEMP_KEY[self._hvac_mode]]
        device2 = "sensor." + \
                  self.controller.get_device(
                      self.tahoma_device.url.replace("#1", "#3")
                  ).label.replace(" ", "_").lower()
        self._humidity_sensor_entity_id = remove_accents(device2)
        _LOGGER.debug("humidity sensor: %s", self._humidity_sensor_entity_id)
        self._current_humidity = None
        self._hvac_modes = [HVAC_MODE_HEAT, HVAC_MODE_AUTO]
        self._hvac_mode = MAP_HVAC_MODE[self.tahoma_device.active_states[HVAC_MODE_KEY]]
        self._preset_mode = MAP_PRESET[self.tahoma_device.active_states[MAP_PRESET_KEY[self._hvac_mode]]]
        self._preset_modes = [
            PRESET_NONE, PRESET_FREEZE, PRESET_SLEEP, PRESET_AWAY, PRESET_HOME]
        self._is_away = None

    async def async_added_to_hass(self):
        await super().async_added_to_hass()

        async_track_state_change(
            self.hass, self._temp_sensor_entity_id, self._async_temp_sensor_changed
        )
        async_track_state_change(
            self.hass, self._humidity_sensor_entity_id, self._async_humidity_sensor_changed
        )

        @callback
        def _async_startup(event):
            """Init on startup."""
            temp_sensor_state = self.hass.states.get(self._temp_sensor_entity_id)
            if temp_sensor_state and temp_sensor_state.state != STATE_UNKNOWN:
                self.update_temp(temp_sensor_state)

            humidity_sensor_state = self.hass.states.get(self._humidity_sensor_entity_id)
            if humidity_sensor_state and humidity_sensor_state.state != STATE_UNKNOWN:
                self.update_humidity(humidity_sensor_state)

        self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, _async_startup)

        old_state = await self.async_get_last_state()
        if old_state is not None:
            if self._target_temp is None:
                if old_state.attributes.get(ATTR_TEMPERATURE) is None:
                    self._target_temp = self.min_temp
                    _LOGGER.warning(
                        "Undefined target temperature, falling back to %s",
                        self._target_temp,
                    )
                else:
                    self._target_temp = float(old_state.attributes[ATTR_TEMPERATURE])
            if old_state.attributes.get(ATTR_PRESET_MODE) == PRESET_AWAY:
                self._is_away = True
            if not self._hvac_mode and old_state.state:
                self._hvac_mode = old_state.state

        else:
            if self._target_temp is None:
                self._target_temp = self.min_temp
            _LOGGER.warning(
                "No previously saved temperature, setting to %s", self._target_temp
            )

        if not self._hvac_mode:
            self._hvac_mode = HVAC_MODE_HEAT
        self.schedule_update_ha_state()

    async def _async_temp_sensor_changed(self, entity_id: str, old_state: State, new_state: State) -> None:
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

    async def _async_humidity_sensor_changed(self, entity_id: str, old_state: State, new_state: State) -> None:
        """Handle temperature changes."""
        if new_state is None:
            return

        self.update_humidity(new_state)
        self.schedule_update_ha_state()

    @callback
    def update_humidity(self, state):
        """Update thermostat with latest state from sensor."""
        if state is None:
            state = self.hass.states.get(self._humidity_sensor_entity_id)
        try:
            self._current_humidity = float(state.state)
        except ValueError as ex:
            _LOGGER.error("Unable to update from sensor: %s", ex)

    def update(self):
        """Update the state."""
        self.apply_action(COMMAND_REFRESH)
        self.controller.get_states([self.tahoma_device])
        self._hvac_mode = MAP_HVAC_MODE[self.tahoma_device.active_states[HVAC_MODE_KEY]]
        self._preset_mode = MAP_PRESET[self.tahoma_device.active_states[MAP_PRESET_KEY[self._hvac_mode]]]
        self._target_temp = self.tahoma_device.active_states[MAP_TARGET_TEMP_KEY[self._hvac_mode]]
        self.update_temp(None)
        self.update_humidity(None)

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
            self.apply_action(COMMAND_EXIT_DEROGATION)
        elif hvac_mode == HVAC_MODE_HEAT and self._hvac_mode != HVAC_MODE_HEAT:
            self.apply_action(COMMAND_SET_DEROGATION, self.current_temperature, COMMAND_OPTION_FURTHER_NOTICE)
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
    def humidity_sensor(self) -> str:
        """Return the id of the temperature sensor"""
        return self._humidity_sensor_entity_id

    @property
    def current_humidity(self) -> Optional[float]:
        """Return the current humidity"""
        return self._current_humidity

    @property
    def temperature_sensor(self) -> str:
        """Return the id of the temperature sensor"""
        return self._temp_sensor_entity_id

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

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
