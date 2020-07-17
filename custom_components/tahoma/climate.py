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
    PRESET_SLEEP,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import EVENT_HOMEASSISTANT_START, STATE_UNKNOWN, TEMP_CELSIUS
from homeassistant.core import State, callback
from homeassistant.helpers.event import async_track_state_change

from .const import DOMAIN, TAHOMA_TYPES
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

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


COMMAND_SET_HEATING_LEVEL = "setHeatingLevel"

IO_TARGET_HEATING_LEVEL_STATE = "io:TargetHeatingLevelState"

PRESET_FREEZE = "freeze"
PRESET_FROST_PROTECTION = "frostprotection"
PRESET_OFF = "off"


class AtlanticElectricalHeater(TahomaDevice, ClimateEntity):
    """Representation of TaHoma IO Atlantic Electrical Heater."""

    def __init__(self, device, controller):
        """Init method."""
        super().__init__(device, controller)
        self._preset_mode = None
        self._hvac_mode = None

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_PRESET_MODE

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
        return [HVAC_MODE_OFF, HVAC_MODE_HEAT]

    def set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        modes = {HVAC_MODE_HEAT: PRESET_COMFORT, HVAC_MODE_OFF: PRESET_OFF}
        self.apply_action(COMMAND_SET_HEATING_LEVEL, modes[hvac_mode])
        self._hvac_mode = hvac_mode
        self._preset_mode = (
            PRESET_NONE if hvac_mode == HVAC_MODE_OFF else PRESET_COMFORT
        )

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp."""
        return self._preset_mode

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes."""
        return [PRESET_NONE, PRESET_FREEZE, PRESET_ECO, PRESET_COMFORT]

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


ST_DEROGATION_TYPE_STATE = "somfythermostat:DerogationTypeState"
ST_HEATING_MODE_STATE = "somfythermostat:HeatingModeState"
ST_DEROGATION_HEATING_MODE_STATE = "somfythermostat:DerogationHeatingModeState"

STATE_DEROGATION_FURTHER_NOTICE = "further_notice"
STATE_DEROGATION_NEXT_MODE = "next_mode"
STATE_DEROGATION_DATE = "date"

ST_MAP_HVAC_MODE = {
    STATE_DEROGATION_DATE: HVAC_MODE_AUTO,
    STATE_DEROGATION_NEXT_MODE: HVAC_MODE_HEAT,
    STATE_DEROGATION_FURTHER_NOTICE: HVAC_MODE_HEAT,
}


class SomfyThermostat(TahomaDevice, ClimateEntity):
    """Representation of Somfy Smart Thermostat."""

    def __init__(self, device, controller, sensor):
        """Init method."""
        super().__init__(device, controller)
        self._target_temp = None
        self._preset_mode = None
        self._hvac_mode = ST_MAP_HVAC_MODE[self.select_state(ST_DEROGATION_TYPE_STATE)]
        self._temp_sensor_entity_id = sensor
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
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self) -> Optional[float]:
        """Return the current temperature."""
        return self._current_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temp

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_PRESET_MODE | SUPPORT_TARGET_TEMPERATURE

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        return self._hvac_mode

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return [HVAC_MODE_AUTO, HVAC_MODE_HEAT]

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp."""
        return self._preset_mode

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes."""
        return [PRESET_NONE, PRESET_FREEZE, PRESET_SLEEP, PRESET_AWAY, PRESET_HOME]
