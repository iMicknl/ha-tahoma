"""Support for Tahoma climate."""
from datetime import timedelta
import logging
from typing import List, Optional

from homeassistant.core import callback, State
from homeassistant.helpers.event import async_track_state_change
from homeassistant.const import (
    ATTR_TEMPERATURE,
    DEVICE_CLASS_TEMPERATURE,
    EVENT_HOMEASSISTANT_START,
    STATE_UNKNOWN,
    TEMP_CELSIUS,
)
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
    ATTR_PRESET_MODE,
)

from .const import (
    DOMAIN,
    TAHOMA_TYPES,
)
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=120)

SUPPORTED_CLIMATE_DEVICES = [
    "SomfyThermostat"
]

COMMAND_REFRESH = "refreshState"
COMMAND_EXIT_DEROGATION = "exitDerogation"
COMMAND_SET_DEROGATION = "setDerogation"

KEY_HVAC_MODE = 'somfythermostat:DerogationTypeState'
KEY_HEATING_MODE = 'somfythermostat:HeatingModeState'
KEY_DEROGATION_HEATING_MODE = 'somfythermostat:DerogationHeatingModeState'
KEY_TARGET_TEMPERATURE = 'core:TargetTemperatureState'
KEY_DEROGATION_TARGET_TEMPERATURE = 'core:DerogatedTargetTemperatureState'

PRESET_FREEZE = "freeze"

STATE_DEROGATION_FURTHER_NOTICE = "further_notice"
STATE_DEROGATION_NEXT_MODE = "next_mode"
STATE_DEROGATION_DATE = "date"
STATE_PRESET_AT_HOME = "atHomeMode"
STATE_PRESET_AWAY = "awayMode"
STATE_PRESET_FREEZE = "freezeMode"
STATE_PRESET_MANUAL = "manualMode"
STATE_PRESET_SLEEPING_MODE = "sleepingMode"

MAP_HVAC_MODE = {
    STATE_DEROGATION_DATE: HVAC_MODE_AUTO,
    STATE_DEROGATION_NEXT_MODE: HVAC_MODE_HEAT,
    STATE_DEROGATION_FURTHER_NOTICE: HVAC_MODE_HEAT
}
MAP_PRESET_KEY = {
    HVAC_MODE_AUTO: KEY_HEATING_MODE,
    HVAC_MODE_HEAT: KEY_DEROGATION_HEATING_MODE
}
MAP_PRESET = {
    STATE_PRESET_AT_HOME: PRESET_HOME,
    STATE_PRESET_AWAY: PRESET_AWAY,
    STATE_PRESET_FREEZE: PRESET_FREEZE,
    STATE_PRESET_MANUAL: PRESET_NONE,
    STATE_PRESET_SLEEPING_MODE: PRESET_SLEEP,
}
MAP_TARGET_TEMP_KEY = {
    HVAC_MODE_AUTO: KEY_TARGET_TEMPERATURE,
    HVAC_MODE_HEAT: KEY_DEROGATION_TARGET_TEMPERATURE
}
TAHOMA_TYPE_HEATING_SYSTEM = "HeatingSystem"


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Tahoma sensors from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]

    entry.add_update_listener(update_listener)

    entities = []
    controller = data.get("controller")

    for device in data.get("devices"):
        if TAHOMA_TYPES[device.uiclass] == "climate":
            options = dict(entry.options)
            if device.url in options[TAHOMA_TYPE_HEATING_SYSTEM] and device.widget == "SomfyThermostat":
                sensor_id = options[DEVICE_CLASS_TEMPERATURE][device.url]
                entities.append(TahomaClimate(device, controller, sensor_id))
            elif device.widget in SUPPORTED_CLIMATE_DEVICES:
                entities.append(TahomaClimate(device, controller))

    async_add_entities(entities)

async def update_listener(hass, entry):
    """Handle options update."""
    options = dict(entry.options)
    for entity in hass.data["climate"].entities:
        if entity.unique_id in options[TAHOMA_TYPE_HEATING_SYSTEM]:
            entity.set_temperature_sensor(options[DEVICE_CLASS_TEMPERATURE][entity.unique_id])
            entity.schedule_update_ha_state()


class TahomaClimate(TahomaDevice, ClimateEntity):
    """Representation of a Tahoma thermostat."""

    def __init__(self, tahoma_device, controller, sensor_id=None):
        """Initialize the sensor."""
        super().__init__(tahoma_device, controller)
        self._uiclass = tahoma_device.uiclass
        self._unique_id = tahoma_device.url
        self._widget = tahoma_device.widget
        self._temp_sensor_entity_id = sensor_id
        self._current_temp = None
        self._hvac_modes = [HVAC_MODE_HEAT, HVAC_MODE_AUTO]
        self._hvac_mode = MAP_HVAC_MODE[self.tahoma_device.active_states[KEY_HVAC_MODE]]
        self._preset_mode = MAP_PRESET[
            self.tahoma_device.active_states[MAP_PRESET_KEY[self._hvac_mode]]]
        self._preset_modes = [
            PRESET_NONE, PRESET_FREEZE, PRESET_SLEEP, PRESET_AWAY, PRESET_HOME]
        self._target_temp = self.tahoma_device.active_states[MAP_TARGET_TEMP_KEY[self._hvac_mode]]
        self._is_away = None

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        if self._temp_sensor_entity_id is not None:
            async_track_state_change(
                self.hass, self._temp_sensor_entity_id, self._async_temp_sensor_changed
            )

        @callback
        def _async_startup(event):
            """Init on startup."""
            if self._temp_sensor_entity_id is not None:
                temp_sensor_state = self.hass.states.get(self._temp_sensor_entity_id)
                if temp_sensor_state and temp_sensor_state.state != STATE_UNKNOWN:
                    self.update_temp(temp_sensor_state)

        self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, _async_startup)

        self.schedule_update_ha_state()

    async def _async_temp_sensor_changed(self, entity_id: str, old_state: State,
                                         new_state: State) -> None:
        """Handle temperature changes."""
        if new_state is None:
            return

        self.update_temp(new_state)
        self.schedule_update_ha_state()

    @callback
    def update_temp(self, state=None):
        """Update thermostat with latest state from sensor."""
        if state is None:
            state = self.hass.states.get(self._temp_sensor_entity_id)

        try:
            self._current_temp = float(state.state)
        except ValueError as ex:
            _LOGGER.error("Unable to update from sensor: %s", ex)

    def update(self):
        """Update the state."""
        if COMMAND_REFRESH in self.tahoma_device.command_definitions:
            self.apply_action(COMMAND_REFRESH)
        self.controller.get_states([self.tahoma_device])
        self._hvac_mode = MAP_HVAC_MODE[self.tahoma_device.active_states[KEY_HVAC_MODE]]
        self._preset_mode = MAP_PRESET[
            self.tahoma_device.active_states[MAP_PRESET_KEY[self._hvac_mode]]]
        self._target_temp = self.tahoma_device.active_states[MAP_TARGET_TEMP_KEY[self._hvac_mode]]
        self.update_temp(None)

    @property
    def device_info(self):
        """Return the device info for the thermostat/valve."""
        return {
            "url": self._unique_id,
            "uiClass": self._uiclass,
            "widget": self._widget,
        }

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

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
            self.apply_action(COMMAND_SET_DEROGATION, self.current_temperature,
                              STATE_DEROGATION_FURTHER_NOTICE)
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
    def temperature_sensor(self) -> str:
        """Return the id of the temperature sensor"""
        return self._temp_sensor_entity_id

    def set_temperature_sensor(self, sensor_id: str):
        self._temp_sensor_entity_id = sensor_id

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
