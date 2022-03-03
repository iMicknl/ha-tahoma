"""Support for Atlantic Pass APC Heating Zone."""
import logging
from typing import List, Optional

from pyoverkiz.enums import OverkizState

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
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS

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
    _attr_max_temp = 30
    _attr_min_temp = 5
    _attr_supported_features = SUPPORT_PRESET_MODE | SUPPORT_TARGET_TEMPERATURE
    _attr_temperature_unit = TEMP_CELSIUS

    def __init__(self, device_url: str, coordinator: OverkizDataUpdateCoordinator):
        """Init method."""
        super().__init__(device_url, coordinator)
        self.temperature_device = self.executor.linked_device(8)

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return preset mode list."""
        presets = [
            PRESET_COMFORT,
            PRESET_ECO,
            CUSTOM_PRESET_AUTO,
            CUSTOM_PRESET_STOP,
            PRESET_AWAY,
        ]

        if (
            self.executor.select_state(IO_PASS_APC_HEATING_PROFILE_STATE)
            == PASS_APC_HEATING_PROFILE_STATE_DEROGATION
        ):
            presets.append(CUSTOM_PRESET_DEROGATION)

        return presets

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

    @property
    def current_temperature(self) -> Optional[float]:
        """Return the current temperature."""
        return float(
            self.temperature_device.states.get(OverkizState.CORE_TEMPERATURE).value
        )

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation."""

        hvac_map = {
          PASS_APC_HEATING_MODE_STATE_STOP: HVAC_MODE_OFF
          PASS_APC_HEATING_MODE_STATE_INTERNAL_SCHEDULING: HVAC_MODE_AUTO
          PASS_APC_HEATING_MODE_STATE_ABSENCE: HVAC_MODE_AUTO
        }

        state = self.executor.select_state(IO_PASS_APC_HEATING_MODE_STATE)

        return hvac_map.get(state, HVAC_MODE_HEAT)

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
            if self.preset_mode == PRESET_COMFORT:
                await self.executor.async_execute_command(
                    COMMAND_SET_COMFORT_HEATING_TARGET_TEMPERATURE, temperature
                )
            elif self.preset_mode == PRESET_ECO:
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
