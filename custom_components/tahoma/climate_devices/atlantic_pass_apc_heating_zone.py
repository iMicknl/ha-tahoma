"""Support for Atlantic Pass APC Heating Zone."""
import logging
from typing import List, Optional

from homeassistant.components.climate import (
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    ClimateEntity,
)
from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    PRESET_AWAY,
    PRESET_COMFORT,
    PRESET_ECO,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    EVENT_HOMEASSISTANT_START,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    TEMP_CELSIUS,
)
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_change

from ..coordinator import OverkizDataUpdateCoordinator
from ..entity import OverkizEntity

_LOGGER = logging.getLogger(__name__)

CUSTOM_PRESET_DEROGATION = "Derogation"
CUSTOM_PRESET_AUTO = "Auto"
CUSTOM_PRESET_STOP = "Stop"

COMMAND_REFRESH_COMFORT_HEATING_TARGET_TEMPERATURE = (
    "refreshComfortHeatingTargetTemperature"
)
COMMAND_REFRESH_DEROGATION_REMAINING_TIME = "refreshDerogationRemainingTime"
COMMAND_REFRESH_ECO_HEATING_TARGET_TEMPERATURE = "refreshEcoHeatingTargetTemperature"
COMMAND_REFRESH_PASS_APC_HEATING_MODE = "refreshPassAPCHeatingMode"
COMMAND_REFRESH_PASS_APC_HEATING_PROFILE = "refreshPassAPCHeatingProfile"
COMMAND_REFRESH_TARGET_TEMPERATURE = "refreshTargetTemperature"
COMMAND_SET_COMFORT_HEATING_TARGET_TEMPERATURE = "setComfortHeatingTargetTemperature"
COMMAND_SET_DEROGATION_ON_OFF_STATE = "setDerogationOnOffState"
COMMAND_SET_DEROGATED_TARGET_TEMPERATURE = "setDerogatedTargetTemperature"
COMMAND_SET_DEROGATION_TIME = "setDerogationTime"
COMMAND_SET_ECO_HEATING_TARGET_TEMPERATURE = "setEcoHeatingTargetTemperature"
COMMAND_SET_OPERATING_MODE = "setOperatingMode"
COMMAND_SET_PASS_APC_HEATING_MODE = "setPassAPCHeatingMode"
COMMAND_SET_TARGET_TEMPERATURE = "setTargetTemperature"

CORE_COMFORT_HEATING_TARGET_TEMPERATURE_STATE = (
    "core:ComfortHeatingTargetTemperatureState"
)
CORE_DEROGATED_TARGET_TEMPERATURE_STATE = "core:DerogatedTargetTemperatureState"
CORE_DEROGATION_ON_OFF_STATE = "core:DerogationOnOffState"
CORE_ECO_HEATING_TARGET_TEMPERATURE_STATE = "core:EcoHeatingTargetTemperatureState"
CORE_HEATING_ON_OFF_STATE = "core:HeatingOnOffState"
CORE_TARGET_TEMPERATURE_STATE = "core:TargetTemperatureState"

IO_DEROGATION_REMAINING_TIME_STATE = "io:DerogationRemainingTimeState"
IO_PASS_APC_HEATING_MODE_STATE = "io:PassAPCHeatingModeState"
IO_PASS_APC_HEATING_PROFILE_STATE = "io:PassAPCHeatingProfileState"
IO_TARGET_HEATING_LEVEL_STATE = "io:TargetHeatingLevelState"

PASS_APC_HEATING_MODE_STATE_ABSENCE = "absence"
PASS_APC_HEATING_MODE_STATE_COMFORT = "comfort"
PASS_APC_HEATING_MODE_STATE_DEROGATION = "derogation"
PASS_APC_HEATING_MODE_STATE_INTERNAL_SCHEDULING = "internalScheduling"
PASS_APC_HEATING_MODE_STATE_STOP = "stop"
PASS_APC_HEATING_PROFILE_STATE_ABSENCE = "absence"
PASS_APC_HEATING_PROFILE_STATE_COMFORT = "comfort"
PASS_APC_HEATING_PROFILE_STATE_DEROGATION = "derogation"
PASS_APC_HEATING_PROFILE_STATE_ECO = "eco"
PASS_APC_HEATING_PROFILE_STATE_INTERNAL_SCHEDULING = "internalScheduling"
PASS_APC_HEATING_PROFILE_STATE_STOP = "stop"

MAP_PRESET_MODES = {
    PASS_APC_HEATING_PROFILE_STATE_ECO: PRESET_ECO,
    PASS_APC_HEATING_PROFILE_STATE_COMFORT: PRESET_COMFORT,
    PASS_APC_HEATING_PROFILE_STATE_INTERNAL_SCHEDULING: CUSTOM_PRESET_AUTO,
    PASS_APC_HEATING_PROFILE_STATE_DEROGATION: CUSTOM_PRESET_DEROGATION,
    PASS_APC_HEATING_PROFILE_STATE_STOP: CUSTOM_PRESET_STOP,
    PASS_APC_HEATING_PROFILE_STATE_ABSENCE: PRESET_AWAY,
}
MAP_REVERSE_PRESET_MODES = {v: k for k, v in MAP_PRESET_MODES.items()}


class AtlanticPassAPCHeatingZone(OverkizEntity, ClimateEntity):
    """Representation of Atlantic Pass APC Heating and Cooling Zone."""

    _attr_hvac_modes = [HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_AUTO]
    _attr_supported_features = SUPPORT_PRESET_MODE | SUPPORT_TARGET_TEMPERATURE
    _attr_temperature_unit = TEMP_CELSIUS

    def __init__(self, device_url: str, coordinator: OverkizDataUpdateCoordinator):
        """Init method."""
        super().__init__(device_url, coordinator)

        self._temp_sensor_entity_id = None
        self._current_temperature = None

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return preset mode list."""

        if (
            self.executor.select_state(IO_PASS_APC_HEATING_PROFILE_STATE)
            == PASS_APC_HEATING_PROFILE_STATE_DEROGATION
        ):
            return [
                PRESET_COMFORT,
                PRESET_ECO,
                CUSTOM_PRESET_AUTO,
                CUSTOM_PRESET_DEROGATION,
                CUSTOM_PRESET_STOP,
                PRESET_AWAY,
            ]
        else:
            return [
                PRESET_COMFORT,
                PRESET_ECO,
                CUSTOM_PRESET_AUTO,
                CUSTOM_PRESET_STOP,
                PRESET_AWAY,
            ]

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp."""

        if (
            self.executor.select_state(IO_PASS_APC_HEATING_MODE_STATE)
            == PASS_APC_HEATING_MODE_STATE_ABSENCE
        ):
            return PRESET_AWAY

        if (
            self.executor.select_state(IO_PASS_APC_HEATING_PROFILE_STATE)
            == PASS_APC_HEATING_PROFILE_STATE_DEROGATION
        ):
            return CUSTOM_PRESET_DEROGATION

        if (
            self.executor.select_state(IO_PASS_APC_HEATING_MODE_STATE)
            == PASS_APC_HEATING_MODE_STATE_INTERNAL_SCHEDULING
        ):
            return MAP_PRESET_MODES[
                self.executor.select_state(IO_PASS_APC_HEATING_PROFILE_STATE)
            ]

        return MAP_PRESET_MODES[
            self.executor.select_state(IO_PASS_APC_HEATING_MODE_STATE)
        ]

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""

        if self.preset_mode == CUSTOM_PRESET_DEROGATION:
            # revert derogation
            await self.executor.async_execute_command(
                COMMAND_SET_DEROGATION_ON_OFF_STATE, "off"
            )
        await self.executor.async_execute_command(
            COMMAND_SET_PASS_APC_HEATING_MODE, MAP_REVERSE_PRESET_MODES[preset_mode]
        )
        await self.refresh_values()

    async def async_added_to_hass(self):
        """Register temperature sensor after added to hass."""

        await super().async_added_to_hass()
        entity_registry = await self.hass.helpers.entity_registry.async_get_registry()

        # The linked temperature sensor uses subsystem_id + 1
        new_subsystem_id = int(self.device_url.split("#", 1)[1]) + 1
        self._temp_sensor_entity_id = next(
            (
                entity_id
                for entity_id, entry in entity_registry.entities.items()
                if entry.unique_id
                == f"{self.base_device_url}#{str(new_subsystem_id)}-core:TemperatureState"
            ),
            None,
        )

        if self._temp_sensor_entity_id:
            async_track_state_change(
                self.hass, self._temp_sensor_entity_id, self._async_temp_sensor_changed
            )
        else:
            _LOGGER.warning(
                "Temperature sensor could not be found for entity %s %s %s",
                self.name,
                self.device_url,
                new_subsystem_id,
            )

        @callback
        def _async_startup(event):
            """Init on startup."""
            if self._temp_sensor_entity_id:
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
        if state is None or state.state in [STATE_UNKNOWN, STATE_UNAVAILABLE]:
            return

        try:
            self._current_temperature = float(state.state)
        except ValueError as ex:
            _LOGGER.error("Unable to update from sensor: %s", ex)

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return 5

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return 30

    @property
    def current_temperature(self) -> Optional[float]:
        """Return the current temperature."""
        return self._current_temperature

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation."""

        if (
            self.executor.select_state(IO_PASS_APC_HEATING_MODE_STATE)
            == PASS_APC_HEATING_MODE_STATE_STOP
        ):
            return HVAC_MODE_OFF

        if self.executor.select_state(IO_PASS_APC_HEATING_MODE_STATE) in [
            PASS_APC_HEATING_MODE_STATE_INTERNAL_SCHEDULING,
            PASS_APC_HEATING_MODE_STATE_ABSENCE,
        ]:
            return HVAC_MODE_AUTO

        return HVAC_MODE_HEAT

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""

        if hvac_mode == HVAC_MODE_OFF:
            await self.executor.async_execute_command(
                COMMAND_SET_PASS_APC_HEATING_MODE, PASS_APC_HEATING_MODE_STATE_STOP
            )
        else:
            if self.hvac_mode == HVAC_MODE_OFF:
                await self.executor.async_execute_command(
                    COMMAND_SET_PASS_APC_HEATING_MODE, "on"
                )
            if hvac_mode == HVAC_MODE_AUTO:
                await self.executor.async_execute_command(
                    COMMAND_SET_PASS_APC_HEATING_MODE,
                    PASS_APC_HEATING_MODE_STATE_INTERNAL_SCHEDULING,
                )
            elif hvac_mode == HVAC_MODE_HEAT:
                await self.executor.async_execute_command(
                    COMMAND_SET_PASS_APC_HEATING_MODE,
                    PASS_APC_HEATING_MODE_STATE_COMFORT,
                )
        self.refresh_values()

    @property
    def target_temperature(self) -> None:
        """Return the temperature."""

        if self.preset_mode == PRESET_COMFORT:
            return self.executor.select_state(
                CORE_COMFORT_HEATING_TARGET_TEMPERATURE_STATE
            )
        if self.preset_mode == PRESET_ECO:
            return self.executor.select_state(CORE_ECO_HEATING_TARGET_TEMPERATURE_STATE)
        if self.preset_mode == CUSTOM_PRESET_DEROGATION:
            return self.executor.select_state(CORE_DEROGATED_TARGET_TEMPERATURE_STATE)

        return self.executor.select_state(CORE_TARGET_TEMPERATURE_STATE)

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)

        if self.hvac_mode == HVAC_MODE_AUTO:
            await self.executor.async_execute_command(
                COMMAND_SET_DEROGATION_ON_OFF_STATE, "on"
            )
            await self.executor.async_execute_command(COMMAND_SET_DEROGATION_TIME, 24)
            await self.executor.async_execute_command(
                COMMAND_SET_DEROGATED_TARGET_TEMPERATURE, temperature
            )
        else:
            if self.preset_mode == "comfort":
                await self.executor.async_execute_command(
                    COMMAND_SET_COMFORT_HEATING_TARGET_TEMPERATURE, temperature
                )
            elif self.preset_mode == "eco":
                await self.executor.async_execute_command(
                    COMMAND_SET_ECO_HEATING_TARGET_TEMPERATURE, temperature
                )

        await self.refresh_values()

    async def refresh_values(self) -> None:
        """Refresh some values not always updated."""

        await self.executor.async_execute_command(
            COMMAND_REFRESH_PASS_APC_HEATING_PROFILE
        )
        await self.executor.async_execute_command(COMMAND_REFRESH_PASS_APC_HEATING_MODE)
        await self.executor.async_execute_command(COMMAND_REFRESH_TARGET_TEMPERATURE)
