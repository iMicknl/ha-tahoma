"""Support for TaHoma climate devices."""
import logging
from typing import List, Optional

from homeassistant.components.climate import (
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_PRESET_MODE,
    ClimateEntity,
)
from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    PRESET_AWAY,
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_HOME,
    PRESET_NONE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    EVENT_HOMEASSISTANT_START,
    STATE_UNKNOWN,
    TEMP_CELSIUS,
)
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_change

from .const import DOMAIN, TAHOMA_TYPES
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

PRESET_FREEZE = "Freeze"

AEH = "AtlanticElectricalHeater"
ST = "SomfyThermostat"
SUPPORTED_CLIMATE_DEVICES = [AEH, ST]


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma climate from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]
    controller = data.get("controller")

    climate_devices = [
        d for d in data.get("devices") if TAHOMA_TYPES[d.uiclass] == "climate"
    ]

    entities = []
    for device in climate_devices:
        if device.widget == AEH:
            entities.append(AtlanticElectricalHeater(device, controller))
        elif device.widget == ST:
            base_url = device.url.split("#", 1)[0]
            sensor = None
            for k, v in hass.data["entity_registry"].entities.items():
                if v.unique_id == base_url + "#2":
                    sensor = k
                    break
            entities.append(SomfyThermostat(device, controller, sensor))
    async_add_entities(entities)


class BaseClimateEntity(TahomaDevice, ClimateEntity):
    """Base class for Tahoma climate entity."""

    def __init__(self, device, controller):
        """Init method."""
        super().__init__(device, controller)
        self._preset_modes = None
        self._preset_mode = None
        self._hvac_modes = None
        self._hvac_mode = None
        self._supported_features = None

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return self._supported_features

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        return self._hvac_mode

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return self._hvac_modes

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp."""
        return self._preset_mode

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes."""
        return self._preset_modes


COMMAND_SET_HEATING_LEVEL = "setHeatingLevel"

IO_TARGET_HEATING_LEVEL_STATE = "io:TargetHeatingLevelState"

PRESET_FROST_PROTECTION = "frostprotection"
PRESET_OFF = "off"


class AtlanticElectricalHeater(BaseClimateEntity):
    """Representation of TaHoma IO Atlantic Electrical Heater."""

    def __init__(self, device, controller):
        """Init method."""
        super().__init__(device, controller)
        self._supported_features = SUPPORT_PRESET_MODE
        self._hvac_modes = [HVAC_MODE_OFF, HVAC_MODE_HEAT]
        self._hvac_mode = None
        self._preset_modes = [PRESET_NONE, PRESET_FREEZE, PRESET_ECO, PRESET_COMFORT]
        self._preset_mode = None

    def set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        modes = {HVAC_MODE_HEAT: PRESET_COMFORT, HVAC_MODE_OFF: PRESET_OFF}
        self.apply_action(COMMAND_SET_HEATING_LEVEL, modes[hvac_mode])
        self._hvac_mode = hvac_mode
        self._preset_mode = (
            PRESET_NONE if hvac_mode == HVAC_MODE_OFF else PRESET_COMFORT
        )

    def set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        modes = {
            PRESET_NONE: PRESET_OFF,
            PRESET_FREEZE: PRESET_FROST_PROTECTION,
            PRESET_ECO: PRESET_ECO,
            PRESET_COMFORT: PRESET_COMFORT,
        }
        self.apply_action(COMMAND_SET_HEATING_LEVEL, modes[preset_mode])
        self._hvac_mode = (
            HVAC_MODE_OFF if preset_mode == PRESET_NONE else HVAC_MODE_HEAT
        )
        self._preset_mode = preset_mode

    def turn_off(self) -> None:
        """Turn off the device."""
        self.apply_action(COMMAND_SET_HEATING_LEVEL, PRESET_OFF)
        self._hvac_mode = HVAC_MODE_OFF
        self._preset_mode = PRESET_NONE


COMMAND_EXIT_DEROGATION = "exitDerogation"
COMMAND_REFRESH_STATE = "refreshState"
COMMAND_SET_DEROGATION = "setDerogation"
COMMAND_SET_MODE_TEMPERATURE = "setModeTemperature"

CORE_DEROGATED_TARGET_TEMPERATURE_STATE = "core:DerogatedTargetTemperatureState"
CORE_TARGET_TEMPERATURE_STATE = "core:TargetTemperatureState"

PRESET_NIGHT = "Night"

ST_DEROGATION_TYPE_STATE = "somfythermostat:DerogationTypeState"
ST_HEATING_MODE_STATE = "somfythermostat:HeatingModeState"
ST_DEROGATION_HEATING_MODE_STATE = "somfythermostat:DerogationHeatingModeState"

STATE_DEROGATION_FURTHER_NOTICE = "further_notice"
STATE_DEROGATION_NEXT_MODE = "next_mode"
STATE_DEROGATION_DATE = "date"
STATE_PRESET_AT_HOME = "atHomeMode"
STATE_PRESET_AWAY = "awayMode"
STATE_PRESET_FREEZE = "freezeMode"
STATE_PRESET_MANUAL = "manualMode"
STATE_PRESET_SLEEPING_MODE = "sleepingMode"

MAP_HVAC_MODES = {
    STATE_DEROGATION_DATE: HVAC_MODE_AUTO,
    STATE_DEROGATION_NEXT_MODE: HVAC_MODE_HEAT,
    STATE_DEROGATION_FURTHER_NOTICE: HVAC_MODE_HEAT,
}

MAP_PRESET_MODES = {
    STATE_PRESET_AT_HOME: PRESET_HOME,
    STATE_PRESET_AWAY: PRESET_AWAY,
    STATE_PRESET_FREEZE: PRESET_FREEZE,
    STATE_PRESET_MANUAL: PRESET_NONE,
    STATE_PRESET_SLEEPING_MODE: PRESET_NIGHT,
}
PRESET_TEMPERATURES = {
    PRESET_HOME: "somfythermostat:AtHomeTargetTemperatureState",
    PRESET_AWAY: "somfythermostat:AwayModeTargetTemperatureState",
    PRESET_FREEZE: "somfythermostat:FreezeModeTargetTemperatureState",
    PRESET_NIGHT: "somfythermostat:SleepingModeTargetTemperatureState",
}


class SomfyThermostat(BaseClimateEntity):
    """Representation of Somfy Smart Thermostat."""

    def __init__(self, device, controller, sensor):
        """Init method."""
        super().__init__(device, controller)
        self._supported_features = SUPPORT_PRESET_MODE | SUPPORT_TARGET_TEMPERATURE
        self._hvac_modes = [HVAC_MODE_AUTO, HVAC_MODE_HEAT]
        self._hvac_mode = MAP_HVAC_MODES[self.select_state(ST_DEROGATION_TYPE_STATE)]
        self._preset_modes = [
            PRESET_NONE,
            PRESET_FREEZE,
            PRESET_NIGHT,
            PRESET_AWAY,
            PRESET_HOME,
        ]
        self._preset_mode = MAP_PRESET_MODES[
            self.select_state(ST_HEATING_MODE_STATE)
            if self._hvac_mode == HVAC_MODE_AUTO
            else self.select_state(ST_DEROGATION_HEATING_MODE_STATE)
        ]
        self._temp_sensor_entity_id = sensor
        self._target_temp = (
            self.select_state(PRESET_TEMPERATURES[self._preset_mode])
            if self._hvac_mode == HVAC_MODE_AUTO
            else self.select_state(CORE_DEROGATED_TARGET_TEMPERATURE_STATE)
        )
        self._saved_target_temp = self._target_temp
        self._current_temperature = None

    async def async_added_to_hass(self):
        """Register temperature sensor after added to hass."""
        await super().async_added_to_hass()
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

        self.schedule_update_ha_state(True)

    async def _async_temp_sensor_changed(self, entity_id, old_state, new_state) -> None:
        """Handle temperature changes."""
        if new_state is None or old_state == new_state:
            return
        self.update_temp(new_state)
        self.schedule_update_ha_state()

    @callback
    def update_temp(self, state):
        """Update thermostat with latest state from sensor."""
        if state is None or state.state == STATE_UNKNOWN:
            return

        try:
            self._current_temperature = float(state.state)
        except ValueError as ex:
            _LOGGER.error("Unable to update from sensor: %s", ex)

    @property
    def current_temperature(self) -> Optional[float]:
        """Return the current temperature."""
        return self._current_temperature

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return 15.0

    @property
    def max_temp(self) -> float:
        """Return the minimum temperature."""
        return 26.0

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temp

    def set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        #  In Somfy Smart Thermostat temperature is ranged between 15 and 26°C.
        if temperature < 15:
            self.apply_action(
                COMMAND_SET_DEROGATION,
                STATE_PRESET_FREEZE,
                STATE_DEROGATION_FURTHER_NOTICE,
            )
        if temperature > 26:
            temperature = 26
        self._target_temp = temperature
        self.apply_action(
            COMMAND_SET_DEROGATION, temperature, STATE_DEROGATION_FURTHER_NOTICE
        )
        self.apply_action(
            COMMAND_SET_MODE_TEMPERATURE, STATE_PRESET_MANUAL, temperature
        )

    def set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        if hvac_mode == self._hvac_mode:
            return
        if hvac_mode == HVAC_MODE_AUTO:
            self._saved_target_temp = self._target_temp
            self.apply_action(COMMAND_EXIT_DEROGATION)
        elif hvac_mode == HVAC_MODE_HEAT:
            self._target_temp = self._saved_target_temp
            self._preset_mode = PRESET_NONE
            self.apply_action(
                COMMAND_SET_DEROGATION,
                self._target_temp,
                STATE_DEROGATION_FURTHER_NOTICE,
            )

    def set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        if preset_mode not in self.preset_modes:
            _LOGGER.error(
                "Preset " + preset_mode + " is not available for " + self.name
            )
            return
        if self.preset_mode == preset_mode:
            return
        self._preset_mode = preset_mode
        modes = {
            PRESET_HOME: STATE_PRESET_AT_HOME,
            PRESET_AWAY: STATE_PRESET_AWAY,
            PRESET_FREEZE: STATE_PRESET_FREEZE,
            PRESET_NONE: STATE_PRESET_MANUAL,
            PRESET_NIGHT: STATE_PRESET_SLEEPING_MODE,
        }
        if preset_mode in [PRESET_FREEZE, PRESET_NIGHT, PRESET_AWAY, PRESET_HOME]:
            self._saved_target_temp = self._target_temp
            self.apply_action(
                COMMAND_SET_DEROGATION,
                modes[preset_mode],
                STATE_DEROGATION_FURTHER_NOTICE,
            )
        elif preset_mode == PRESET_NONE:
            self._target_temp = self._saved_target_temp
            self.apply_action(
                COMMAND_SET_DEROGATION,
                self._target_temp,
                STATE_DEROGATION_FURTHER_NOTICE,
            )
            self.apply_action(
                COMMAND_SET_MODE_TEMPERATURE, STATE_PRESET_MANUAL, self._target_temp
            )

    def update(self):
        """Update method."""
        self.apply_action(COMMAND_REFRESH_STATE)
        super().update()
        self._hvac_mode = MAP_HVAC_MODES[self.select_state(ST_DEROGATION_TYPE_STATE)]
        self._preset_mode = MAP_PRESET_MODES[
            self.select_state(ST_HEATING_MODE_STATE)
            if self._hvac_mode == HVAC_MODE_AUTO
            else self.select_state(ST_DEROGATION_HEATING_MODE_STATE)
        ]
        self._target_temp = (
            self.select_state(PRESET_TEMPERATURES[self._preset_mode])
            if self._hvac_mode == HVAC_MODE_AUTO
            else self.select_state(CORE_DEROGATED_TARGET_TEMPERATURE_STATE)
        )
