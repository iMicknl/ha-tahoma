"""Support for Tahoma climate."""
from datetime import timedelta
import logging
from typing import List, Optional

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ATTR_PRESET_MODE,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    CURRENT_HVAC_OFF,
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    PRESET_AWAY,
    PRESET_BOOST,
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_HOME,
    PRESET_NONE,
    PRESET_SLEEP,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    DEVICE_CLASS_TEMPERATURE,
    EVENT_HOMEASSISTANT_START,
    STATE_OFF,
    STATE_ON,
    STATE_UNKNOWN,
    TEMP_CELSIUS,
)
from homeassistant.core import State, callback
from homeassistant.helpers.event import async_track_state_change

from .const import (
    COMMAND_EXIT_DEROGATION,
    COMMAND_OFF,
    COMMAND_REFRESH_STATE,
    COMMAND_SET_DEROGATION,
    COMMAND_SET_HEATING_LEVEL,
    COMMAND_SET_MODE_TEMPERATURE,
    CORE_DEROGATED_TARGET_TEMPERATURE_STATE,
    CORE_ON_OFF_STATE,
    CORE_TARGET_TEMPERATURE_STATE,
    DOMAIN,
    IO_TARGET_HEATING_LEVEL_STATE,
    ST_DEROGATION_HEATING_MODE_STATE,
    ST_DEROGATION_TYPE_STATE,
    ST_HEATING_MODE_STATE,
    TAHOMA_TYPES,
)
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)

W_ST = "SomfyThermostat"
W_AEH = "AtlanticElectricalHeater"

SUPPORTED_CLIMATE_DEVICES = [W_ST, W_AEH]

PRESET_FREEZE = "freeze"
PRESET_FROST_PROTECTION = "frostprotection"
PRESET_OFF = "off"

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
    STATE_DEROGATION_FURTHER_NOTICE: HVAC_MODE_HEAT,
    STATE_ON: HVAC_MODE_HEAT,
    STATE_OFF: HVAC_MODE_OFF,
}
MAP_PRESET = {
    STATE_PRESET_AT_HOME: PRESET_HOME,
    STATE_PRESET_AWAY: PRESET_AWAY,
    STATE_PRESET_FREEZE: PRESET_FREEZE,
    STATE_PRESET_MANUAL: PRESET_NONE,
    STATE_PRESET_SLEEPING_MODE: PRESET_SLEEP,
    PRESET_OFF: PRESET_NONE,
    PRESET_FROST_PROTECTION: PRESET_FREEZE,
    PRESET_ECO: PRESET_ECO,
    PRESET_COMFORT: PRESET_COMFORT,
}
ST_MAP_PRESET_REVERSE = {
    PRESET_HOME: STATE_PRESET_AT_HOME,
    PRESET_AWAY: STATE_PRESET_AWAY,
    PRESET_FREEZE: STATE_PRESET_FREEZE,
    PRESET_NONE: STATE_PRESET_MANUAL,
    PRESET_SLEEP: STATE_PRESET_SLEEPING_MODE,
}
AEH_MAP_PRESET_REVERSE = {
    PRESET_NONE: PRESET_OFF,
    PRESET_FREEZE: PRESET_FROST_PROTECTION,
    PRESET_ECO: PRESET_ECO,
    PRESET_COMFORT: PRESET_COMFORT,
}
TAHOMA_TYPE_HEATING_SYSTEM = "HeatingSystem"


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Tahoma sensors from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]

    entry.add_update_listener(update_listener)

    entities = []
    controller = data.get("controller")

    for device in data.get("devices"):
        if (
            TAHOMA_TYPES[device.uiclass] == "climate"
            and device.widget in SUPPORTED_CLIMATE_DEVICES
        ):
            options = dict(entry.options)
            preset_temp = {
                PRESET_FREEZE: None,
                PRESET_AWAY: None,
                PRESET_ECO: None,
                PRESET_COMFORT: None,
            }
            if DEVICE_CLASS_TEMPERATURE in options:
                if device.url in options[DEVICE_CLASS_TEMPERATURE]:
                    sensor_id = options[DEVICE_CLASS_TEMPERATURE][device.url]
                    if device.widget == W_ST:
                        entities.append(
                            TahomaClimate(device, controller, sensor_id, preset_temp)
                        )
                    else:
                        for k, v in preset_temp.items():
                            if (
                                k in options[DEVICE_CLASS_TEMPERATURE]
                                and options[DEVICE_CLASS_TEMPERATURE][k] != ""
                            ):
                                preset_temp[k] = float(
                                    options[DEVICE_CLASS_TEMPERATURE][k]
                                )
                        entities.append(
                            TahomaClimate(device, controller, sensor_id, preset_temp)
                        )

            else:
                entities.append(
                    TahomaClimate(device, controller, preset_temp=preset_temp)
                )

    async_add_entities(entities)


async def update_listener(hass, entry):
    """Handle options update."""
    options = dict(entry.options)
    for entity in hass.data["climate"].entities:
        if entity.unique_id in options[DEVICE_CLASS_TEMPERATURE]:
            entity.set_temperature_sensor(
                options[DEVICE_CLASS_TEMPERATURE][entity.unique_id]
            )
            if entity.widget != W_ST:
                preset_temp = {
                    PRESET_FREEZE: None,
                    PRESET_AWAY: None,
                    PRESET_ECO: None,
                    PRESET_COMFORT: None,
                }
                for k, v in preset_temp.items():
                    if (
                        k in options[DEVICE_CLASS_TEMPERATURE]
                        and options[DEVICE_CLASS_TEMPERATURE][k] != ""
                    ):
                        preset_temp[k] = float(options[DEVICE_CLASS_TEMPERATURE][k])
                entity.set_preset_temperatures(preset_temp)
            entity.schedule_update_ha_state()


class TahomaClimate(TahomaDevice, ClimateEntity):
    """Representation of a Tahoma thermostat."""

    def __init__(self, tahoma_device, controller, sensor_id=None, preset_temp=None):
        """Initialize the sensor."""
        super().__init__(tahoma_device, controller)
        if preset_temp is None:
            preset_temp = {}
        self._temperature_unit = TEMP_CELSIUS
        self._cold_tolerance = 0.3
        self._hot_tolerance = 0.3
        self._supported_features = SUPPORT_PRESET_MODE | SUPPORT_TARGET_TEMPERATURE
        self._uiclass = tahoma_device.uiclass
        self._unique_id = tahoma_device.url
        self._widget = tahoma_device.widget
        self._temp_sensor_entity_id = sensor_id
        self._current_temperature = 0
        self._current_hvac_modes = CURRENT_HVAC_IDLE
        self._target_temp = None
        self._saved_target_temp = self._target_temp
        self._preset_temperatures = preset_temp
        if self._widget == W_ST:
            self._hvac_modes = [HVAC_MODE_AUTO, HVAC_MODE_HEAT]
            self._hvac_mode = MAP_HVAC_MODE[
                self.tahoma_device.active_states[ST_DEROGATION_TYPE_STATE]
            ]
            self._preset_mode = MAP_PRESET[
                self.tahoma_device.active_states[ST_HEATING_MODE_STATE]
                if self._hvac_mode == HVAC_MODE_AUTO
                else self.tahoma_device.active_states[ST_DEROGATION_HEATING_MODE_STATE]
            ]
            self._preset_modes = [
                PRESET_NONE,
                PRESET_FREEZE,
                PRESET_SLEEP,
                PRESET_AWAY,
                PRESET_HOME,
            ]
            self._target_temp = (
                self.tahoma_device.active_states[CORE_TARGET_TEMPERATURE_STATE]
                if self._hvac_mode == HVAC_MODE_AUTO
                else self.tahoma_device.active_states[
                    CORE_DEROGATED_TARGET_TEMPERATURE_STATE
                ]
            )
        elif self._widget == W_AEH:
            self._hvac_modes = [HVAC_MODE_HEAT, HVAC_MODE_OFF]
            self._hvac_mode = MAP_HVAC_MODE[
                self.tahoma_device.active_states[CORE_ON_OFF_STATE]
            ]
            self._preset_mode = MAP_PRESET[
                self.tahoma_device.active_states[IO_TARGET_HEATING_LEVEL_STATE]
            ]
            self._target_temp = 19
            self._preset_modes = [PRESET_NONE]
            for k, v in self._preset_temperatures.items():
                if v:
                    self._preset_modes.append(k)
        self._stored_target_temp = self._target_temp

    async def async_added_to_hass(self):
        """Register temperature sensor after added to hass."""
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

        self.schedule_update_ha_state(True)

    async def _async_temp_sensor_changed(
        self, entity_id: str, old_state: State, new_state: State
    ) -> None:
        """Handle temperature changes."""
        if new_state is None:
            return
        if old_state == new_state:
            return

        self.update_temp(new_state)
        if self._widget == W_AEH:
            await self.hass.async_add_executor_job(self._control_heating)
        self.schedule_update_ha_state()

    @callback
    def update_temp(self, state=None):
        """Update thermostat with latest state from sensor."""
        if self._temp_sensor_entity_id is None:
            return

        if state is None:
            state = self.hass.states.get(self._temp_sensor_entity_id)

        if state.state is None:
            return

        try:
            self._current_temperature = (
                0 if state.state == STATE_UNKNOWN else float(state.state)
            )
        except ValueError as ex:
            _LOGGER.error("Unable to update from sensor: %s", ex)

    def update(self):
        """Update the state."""
        self.controller.get_states([self.tahoma_device])
        self.update_temp(None)
        if self._widget == W_ST:
            self._hvac_mode = MAP_HVAC_MODE[
                self.tahoma_device.active_states[ST_DEROGATION_TYPE_STATE]
            ]
            self._target_temp = (
                self.tahoma_device.active_states[CORE_TARGET_TEMPERATURE_STATE]
                if self._hvac_mode == HVAC_MODE_AUTO
                else self.tahoma_device.active_states[
                    CORE_DEROGATED_TARGET_TEMPERATURE_STATE
                ]
            )
            self._preset_mode = MAP_PRESET[
                self.tahoma_device.active_states[ST_HEATING_MODE_STATE]
                if self._hvac_mode == HVAC_MODE_AUTO
                else self.tahoma_device.active_states[ST_DEROGATION_HEATING_MODE_STATE]
            ]
        self._current_hvac_modes = (
            CURRENT_HVAC_OFF
            if self._hvac_mode == HVAC_MODE_OFF
            else CURRENT_HVAC_IDLE
            if self._current_temperature == 0
            or self._current_temperature > self._target_temp
            else CURRENT_HVAC_HEAT
        )

    @property
    def available(self) -> bool:
        """If the device hasn't been able to connect, mark as unavailable."""
        return (
            bool(self._current_temperature != 0)
            and self.hass.states.get(self._temp_sensor_entity_id) is not None
        )

    @property
    def widget(self) -> str:
        """Return the widget attached to this device."""
        return self._widget

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        return self._hvac_mode

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return self._hvac_modes

    @property
    def hvac_action(self) -> Optional[str]:
        """Return the current running hvac operation if supported."""
        return self._current_hvac_modes

    def set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        if hvac_mode == self._hvac_mode:
            return
        if self._widget == W_ST:
            if hvac_mode == HVAC_MODE_AUTO:
                self._stored_target_temp = self._target_temp
                self.apply_action(COMMAND_EXIT_DEROGATION)
            elif hvac_mode == HVAC_MODE_HEAT:
                self._target_temp = self._stored_target_temp
                self._preset_mode = PRESET_NONE
                self.apply_action(
                    COMMAND_SET_DEROGATION,
                    self._target_temp,
                    STATE_DEROGATION_FURTHER_NOTICE,
                )
            self.apply_action(COMMAND_REFRESH_STATE)
        if self._widget == W_AEH:
            self._hvac_mode = hvac_mode
            self._control_heating()
            return

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return self._supported_features

    @property
    def temperature_sensor(self) -> str:
        """Return the id of the temperature sensor."""
        return self._temp_sensor_entity_id

    def set_temperature_sensor(self, sensor_id: str):
        """Set the temperature sensor."""
        self._temp_sensor_entity_id = sensor_id
        self.schedule_update_ha_state()

    def set_preset_temperatures(self, preset_temp):
        """Set the preset temperatures if supported."""
        self._preset_temperatures = preset_temp
        self._preset_modes = [PRESET_NONE]
        for k, v in self._preset_temperatures.items():
            if v:
                self._preset_modes.append(k)

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return self._temperature_unit

    @property
    def current_temperature(self) -> Optional[float]:
        """Return the current temperature."""
        return self._current_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temp

    def set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        if self._widget == W_ST:
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
            self.apply_action(COMMAND_REFRESH_STATE)
        if self._widget == W_AEH:
            self._target_temp = temperature
            self._control_heating()

    def _control_heating(self) -> None:
        """Control whether heater should be turned on or off."""
        if self._current_temperature == 0 or self._hvac_mode == HVAC_MODE_OFF:
            self.turn_off()
            return

        too_cold = self._target_temp - self._current_temperature >= self._cold_tolerance
        too_hot = self._current_temperature - self._target_temp >= self._hot_tolerance
        if too_hot:
            self.turn_off()
        if too_cold:
            self.turn_on()

    def turn_off(self):
        """Turn the entity off."""
        if self._widget == W_AEH:
            self.apply_action(COMMAND_OFF)

    def turn_on(self):
        """Turn the entity on."""
        if self._widget == W_AEH:
            self.apply_action(
                COMMAND_SET_HEATING_LEVEL, AEH_MAP_PRESET_REVERSE[PRESET_COMFORT]
            )

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
        if preset_mode not in self.preset_modes:
            _LOGGER.error(
                "Preset " + preset_mode + " is not available for " + self._name
            )
            return
        if self._preset_mode == preset_mode:
            return
        self._preset_mode = preset_mode
        if self._widget == W_ST:
            if preset_mode in [PRESET_FREEZE, PRESET_SLEEP, PRESET_AWAY, PRESET_HOME]:
                self._stored_target_temp = self._target_temp
                self.apply_action(
                    COMMAND_SET_DEROGATION,
                    ST_MAP_PRESET_REVERSE[preset_mode],
                    STATE_DEROGATION_FURTHER_NOTICE,
                )
            elif preset_mode == PRESET_NONE:
                self._target_temp = self._stored_target_temp
                self.apply_action(
                    COMMAND_SET_DEROGATION,
                    self._target_temp,
                    STATE_DEROGATION_FURTHER_NOTICE,
                )
                self.apply_action(
                    COMMAND_SET_MODE_TEMPERATURE, STATE_PRESET_MANUAL, self._target_temp
                )
            self.apply_action(COMMAND_REFRESH_STATE)
        elif self._widget == W_AEH:
            if preset_mode == PRESET_NONE:
                self._preset_mode = PRESET_NONE
                self._target_temp = self._saved_target_temp
            else:
                if self._preset_mode == PRESET_NONE:
                    self._saved_target_temp = self._target_temp
                self._preset_mode = preset_mode
                self._target_temp = self._preset_temperatures[preset_mode]
            self._control_heating()
