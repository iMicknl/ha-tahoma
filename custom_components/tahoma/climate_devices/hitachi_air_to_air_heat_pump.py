"""Support for HitachiAirToAirHeatPump."""
import logging
from typing import Any, Dict, List, Optional

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_HEAT,
    SUPPORT_FAN_MODE,
    SUPPORT_SWING_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    SWING_BOTH,
    SWING_HORIZONTAL,
    SWING_OFF,
    SWING_VERTICAL,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS

from ..coordinator import TahomaDataUpdateCoordinator
from ..tahoma_entity import TahomaEntity

_LOGGER = logging.getLogger(__name__)

CORE_TARGET_TEMPERATURE_STATE = "core:TargetTemperatureState"

MAIN_OPERATION_STATE = ["ovp:MainOperationState", "hlrrwifi:MainOperationState"]
FAN_SPEED_STATE = ["ovp:FanSpeedState", "hlrrwifi:FanSpeedState"]
MODE_CHANGE_STATE = ["ovp:ModeChangeState", "hlrrwifi:ModeChangeState"]
SWING_STATE = ["ovp:SwingState", "hlrrwifi:SwingState"]
ROOM_TEMPERATURE_STATE = ["ovp:RoomTemperatureState", "hlrrwifi:RoomTemperatureState"]
VIRTUAL_OPERATING_MODE_STATE = [
    "ovp:HLinkVirtualOperatingModeState",
    "hlrrwifi:HLinkVirtualOperatingModeState",
]
LEAVE_HOME_STATE = ["ovp::LeaveHomeState", "hlrrwifi:LeaveHomeState"]

TAHOMA_TO_HVAC_MODES = {
    "heating": HVAC_MODE_HEAT,
    "fan": HVAC_MODE_FAN_ONLY,
    "dehumidify": HVAC_MODE_DRY,
    "cooling": HVAC_MODE_COOL,
    "auto": HVAC_MODE_AUTO,
    "auto cooling": HVAC_MODE_AUTO,
    "auto heating": HVAC_MODE_AUTO,
}

HVAC_MODES_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_HVAC_MODES.items()}

TAHOMA_TO_SWING_MODES = {
    "both": SWING_BOTH,
    "horizontal": SWING_HORIZONTAL,
    "stop": SWING_OFF,
    "vertical": SWING_VERTICAL,
}

SWING_MODES_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_SWING_MODES.items()}

# TODO it seems that the same widget has different fan names
TAHOMA_TO_FAN_MODES = {
    "auto": SWING_BOTH,
    "high": SWING_BOTH,
    "low": SWING_BOTH,
    "medium": SWING_BOTH,
    "silent": SWING_BOTH,
}

FAN_MODES_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_FAN_MODES.items()}


class HitachiAirToAirHeatPump(TahomaEntity, ClimateEntity):
    """Representation of HitachiAirToAirHeatPump."""

    def __init__(self, device_url: str, coordinator: TahomaDataUpdateCoordinator):
        """Init method."""
        super().__init__(device_url, coordinator)

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
            # | SUPPORT_PRESET_MODE
        )

    async def async_turn_on(self) -> None:
        """Turn on the device."""
        await self._global_control(main_operation="on")

    async def async_turn_off(self) -> None:
        """Turn off the device."""
        await self._global_control(main_operation="off")

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        return TAHOMA_TO_HVAC_MODES[self.select_state(*MODE_CHANGE_STATE)]

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return [*HVAC_MODES_TO_TAHOMA]

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        await self._global_control(hvac_mode=HVAC_MODES_TO_TAHOMA[hvac_mode])

    @property
    def fan_mode(self) -> Optional[str]:
        """Return the fan setting."""
        return self.select_state(*FAN_SPEED_STATE)

    @property
    def fan_modes(self) -> Optional[List[str]]:
        """Return the list of available fan modes."""
        return ["auto", "high", "low", "medium", "silent"]

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

    # @property
    # def preset_mode(self) -> Optional[str]:
    #     """Return the current preset mode, e.g., home, away, temp."""
    #     if self.select_state("core:AutoManuModeState") == "on":
    #         return "auto"

    #     if self.select_state("core:AutoManuModeState") == "manu":
    #         return "manu"

    #     return None

    # @property
    # def preset_modes(self) -> Optional[List[str]]:
    #     """Return a list of available preset modes."""
    #     return ["auto", "manu"]

    # async def async_set_preset_mode(self, preset_mode: str) -> None:
    #     """Set new preset mode."""

    #     if preset_mode == "auto":
    #         await self.async_execute_command("setAutoManu", "auto")

    #     if preset_mode == "manu":
    #         await self.async_execute_command("setAutoManu", "manu")

    #     if preset_mode == "holidays":
    #         await self.async_execute_command("setHolidays", "on")

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
        await self.async_execute_command(
            "globalControl",
            main_operation
            or self.select_state(*MAIN_OPERATION_STATE),  # Main Operation
            target_temperature
            or self.select_state(CORE_TARGET_TEMPERATURE_STATE),  # Target Temperature
            fan_mode or self.select_state(*FAN_SPEED_STATE),  # Fan Mode
            hvac_mode or self.select_state(*MODE_CHANGE_STATE),  # Mode
            swing_mode or self.select_state(*SWING_STATE),  # Swing Mode
            leave_home or self.select_state(*LEAVE_HOME_STATE),  # Leave Home
        )
