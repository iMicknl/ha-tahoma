"""Support for HitachiAirToAirHeatPump."""
import logging
from typing import Any, Dict, List, Optional

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    FAN_AUTO,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    PRESET_NONE,
    SUPPORT_FAN_MODE,
    SUPPORT_PRESET_MODE,
    SUPPORT_SWING_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    SWING_BOTH,
    SWING_HORIZONTAL,
    SWING_OFF,
    SWING_VERTICAL,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS

from ..tahoma_entity import TahomaEntity

_LOGGER = logging.getLogger(__name__)

COMMAND_GLOBAL_CONTROL = "globalControl"

CORE_TARGET_TEMPERATURE_STATE = "core:TargetTemperatureState"

FAN_SPEED_STATE = ["ovp:FanSpeedState", "hlrrwifi:FanSpeedState"]
LEAVE_HOME_STATE = ["ovp::LeaveHomeState", "hlrrwifi:LeaveHomeState"]
MAIN_OPERATION_STATE = ["ovp:MainOperationState", "hlrrwifi:MainOperationState"]
MODE_CHANGE_STATE = ["ovp:ModeChangeState", "hlrrwifi:ModeChangeState"]
ROOM_TEMPERATURE_STATE = ["ovp:RoomTemperatureState", "hlrrwifi:RoomTemperatureState"]
SWING_STATE = ["ovp:SwingState", "hlrrwifi:SwingState"]

STATE_ON = "on"
STATE_OFF = "off"

TAHOMA_TO_HVAC_MODES = {
    "off": HVAC_MODE_OFF,
    "heating": HVAC_MODE_HEAT,
    "fan": HVAC_MODE_FAN_ONLY,
    "dehumidify": HVAC_MODE_DRY,
    "cooling": HVAC_MODE_COOL,
    "auto": HVAC_MODE_AUTO,
    "autoCooling": HVAC_MODE_AUTO,
    "autoHeating": HVAC_MODE_AUTO,
}

HVAC_MODES_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_HVAC_MODES.items()}

TAHOMA_TO_SWING_MODES = {
    "both": SWING_BOTH,
    "horizontal": SWING_HORIZONTAL,
    "stop": SWING_OFF,
    "vertical": SWING_VERTICAL,
}

SWING_MODES_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_SWING_MODES.items()}

TAHOMA_TO_FAN_MODES = {
    "auto": FAN_AUTO,
    "high": FAN_HIGH,
    "low": FAN_LOW,
    "medium": FAN_MEDIUM,
    "silent": "silent",
}

FAN_MODES_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_FAN_MODES.items()}


class HitachiAirToAirHeatPump(TahomaEntity, ClimateEntity):
    """Representation of HitachiAirToAirHeatPump."""

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return (
            SUPPORT_TARGET_TEMPERATURE
            | SUPPORT_FAN_MODE
            | SUPPORT_SWING_MODE
            | SUPPORT_PRESET_MODE
        )

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return [*HVAC_MODES_TO_TAHOMA]

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        if self.select_state(*MAIN_OPERATION_STATE) == STATE_OFF:
            return HVAC_MODE_OFF

        return TAHOMA_TO_HVAC_MODES[self.select_state(*MODE_CHANGE_STATE)]

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVAC_MODE_OFF:
            await self._global_control(main_operation=STATE_OFF)
        else:
            await self._global_control(
                main_operation=STATE_ON, hvac_mode=HVAC_MODES_TO_TAHOMA[hvac_mode]
            )

    @property
    def fan_mode(self) -> Optional[str]:
        """Return the fan setting."""
        return self.select_state(*FAN_SPEED_STATE)

    @property
    def fan_modes(self) -> Optional[List[str]]:
        """Return the list of available fan modes."""
        return [*FAN_MODES_TO_TAHOMA]

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        await self._global_control(fan_mode=fan_mode)

    @property
    def swing_mode(self) -> Optional[str]:
        """Return the swing setting."""
        return TAHOMA_TO_SWING_MODES[self.select_state(*SWING_STATE)]

    @property
    def swing_modes(self) -> Optional[List[str]]:
        """Return the list of available swing modes."""
        return [*SWING_MODES_TO_TAHOMA]

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        """Set new target swing operation."""
        await self._global_control(swing_mode=SWING_MODES_TO_TAHOMA[swing_mode])

    @property
    def target_temperature(self) -> None:
        """Return the temperature."""
        return self.select_state(CORE_TARGET_TEMPERATURE_STATE)

    @property
    def current_temperature(self) -> None:
        """Return current temperature."""
        return self.select_state(*ROOM_TEMPERATURE_STATE)

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        await self._global_control(target_temperature=temperature)

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp."""
        if self.select_state(*LEAVE_HOME_STATE) == STATE_ON:
            return "holiday_mode"

        if self.select_state(*LEAVE_HOME_STATE) == STATE_OFF:
            return PRESET_NONE

        return None

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes."""
        return [PRESET_NONE, "holiday_mode"]

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        if preset_mode == "holiday_mode":
            await self._global_control(leave_home=STATE_ON)

        if preset_mode == PRESET_NONE:
            await self._global_control(leave_home=STATE_OFF)

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return the device state attributes."""
        device_info = super().device_info or {}
        device_info["manufacturer"] = "Hitachi"

        return device_info

    async def _global_control(
        self,
        main_operation=None,
        target_temperature=None,
        fan_mode=None,
        hvac_mode=None,
        swing_mode=None,
        leave_home=None,
    ):
        """Execute globalControl command with all parameters."""
        await self.async_execute_command(
            COMMAND_GLOBAL_CONTROL,
            main_operation
            or self.select_state(*MAIN_OPERATION_STATE),  # Main Operation
            target_temperature
            or self.select_state(CORE_TARGET_TEMPERATURE_STATE),  # Target Temperature
            fan_mode or self.select_state(*FAN_SPEED_STATE),  # Fan Mode
            hvac_mode or self.select_state(*MODE_CHANGE_STATE),  # Mode
            swing_mode or self.select_state(*SWING_STATE),  # Swing Mode
            leave_home or self.select_state(*LEAVE_HOME_STATE),  # Leave Home
        )
