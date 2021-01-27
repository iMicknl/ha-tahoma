"""Support for HitachiAirToAirHeatPump."""
from typing import List, Optional

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_FAN_MODE,
    SUPPORT_SWING_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS

from ..coordinator import TahomaDataUpdateCoordinator
from ..tahoma_entity import TahomaEntity

CORE_TARGET_TEMPERATURE_STATE = "core:TargetTemperatureState"

MAIN_OPERATION_STATE = ["ovp:MainOperationState", "hlrrwifi:MainOperationState"]
FAN_SPEED_STATE = ["ovp:FanSpeedState", "hlrrwifi:FanSpeedState"]
MODE_CHANGE_STATE = ["ovp:ModeChangeState", "hlrrwifi:ModeChangeState"]
SWING_STATE = ["ovp:SwingState", "hlrrwifi:SwingState"]
ROOM_TEMPERATURE_STATE = ["ovp:RoomTemperatureState", "hlrrwifi:RoomTemperatureState"]

# Map Home Assistant presets to TaHoma presets
TAHOMA_TO_PRESET_MODE = {
    "auto": "auto",  # core:AutoManuModeState
    "manu": "manu",  # core:AutoManuModeState
    "holiday": "holiday",  # core:HolidaysModeState
}

PRESET_MODE_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_PRESET_MODE.items()}


TAHOMA_TO_HVAC_MODES = {
    "heating": HVAC_MODE_HEAT,
    "off": HVAC_MODE_OFF,
    "fan": HVAC_MODE_FAN_ONLY,
    "dehumidify": HVAC_MODE_DRY,
    "cooling": HVAC_MODE_COOL,
    "auto": HVAC_MODE_AUTO,
}

HVAC_MODES_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_HVAC_MODES.items()}


class HitachiAirToAirHeatPump(TahomaEntity, ClimateEntity):
    """Representation of HitachiAirToAirHeatPump."""

    def __init__(self, device_url: str, coordinator: TahomaDataUpdateCoordinator):
        """Init method."""
        super().__init__(device_url, coordinator)

        self._fan_modes = self.select_state_definition(FAN_SPEED_STATE)
        self._swing_modes = self.select_state_definition(SWING_STATE)

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_TARGET_TEMPERATURE | SUPPORT_FAN_MODE | SUPPORT_SWING_MODE

    async def async_turn_on(self) -> None:
        """Turn on the device."""
        await self.async_execute_command("setMainOperation", "on")

    async def async_turn_off(self) -> None:
        """Turn off the device."""
        await self.async_execute_command("setMainOperation", "off")

    @property
    def fan_mode(self) -> Optional[str]:
        """Return the fan setting."""
        return self.select_state(FAN_SPEED_STATE)

    @property
    def fan_modes(self) -> Optional[List[str]]:
        """Return the list of available fan modes."""
        return self._fan_modes

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        await self.async_execute_command(
            "globalControl",
            None,  # Power State
            None,  # Target Temperature
            fan_mode,  # Fan Mode
            None,  # Mode
            None,  # Swing Mode
            None,
        )

    @property
    def swing_mode(self) -> Optional[str]:
        """Return the swing setting."""
        return self.select_state(SWING_STATE)

    @property
    def swing_modes(self) -> Optional[List[str]]:
        """Return the list of available swing modes."""
        return self._swing_modes

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        """Set new target swing operation."""
        await self.async_execute_command(
            "globalControl",
            None,  # Power State
            None,  # Target Temperature
            None,  # Fan Mode
            None,  # Mode
            swing_mode,  # Swing Mode
            None,
        )

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        return TAHOMA_TO_HVAC_MODES[self.select_state(MODE_CHANGE_STATE)]

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return [*HVAC_MODES_TO_TAHOMA]

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        await self.async_execute_command(
            "globalControl",
            None,  # Power State
            None,  # Target Temperature
            None,  # Fan Mode
            HVAC_MODES_TO_TAHOMA[hvac_mode],  # Mode
            None,  # Swing Mode
            None,
        )

    @property
    def target_temperature(self) -> None:
        """Return the temperature."""
        return self.select_state(CORE_TARGET_TEMPERATURE_STATE)

    @property
    def current_temperature(self) -> None:
        """Return current temperature."""
        return self.select_state(ROOM_TEMPERATURE_STATE)

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        await self.async_execute_command(
            "globalControl",
            None,  # Power State
            temperature,  # Target Temperature
            None,  # Fan Mode
            None,  # Mode
            None,  # Swing Mode
            None,
        )
