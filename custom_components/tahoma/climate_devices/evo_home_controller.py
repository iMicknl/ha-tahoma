"""Support for EvoHomeController."""
from datetime import timedelta
from typing import Any, Dict, List, Optional

from homeassistant.components.climate import SUPPORT_PRESET_MODE, ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    PRESET_NONE,
)
from homeassistant.const import TEMP_CELSIUS
import homeassistant.util.dt as dt_util

from ..tahoma_entity import TahomaEntity

PRESET_DAY_OFF = "day-off"
PRESET_HOLIDAYS = "holidays"

COMMAND_SET_OPERATING_MODE = "setOperatingMode"

RAMSES_RAMSES_OPERATING_MODE_STATE = "ramses:RAMSESOperatingModeState"

TAHOMA_TO_HVAC_MODES = {"auto": HVAC_MODE_AUTO, "off": HVAC_MODE_OFF}
HVAC_MODES_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_HVAC_MODES.items()}

TAHOMA_TO_PRESET_MODES = {
    "day-off": PRESET_DAY_OFF,
    "holidays": PRESET_HOLIDAYS,
}
PRESET_MODES_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_PRESET_MODES.items()}


class EvoHomeController(TahomaEntity, ClimateEntity):
    """Representation of EvoHomeController device."""

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_PRESET_MODE

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        operating_mode = self.select_state(RAMSES_RAMSES_OPERATING_MODE_STATE)

        if operating_mode in TAHOMA_TO_HVAC_MODES:
            return TAHOMA_TO_HVAC_MODES[operating_mode]

        if operating_mode in TAHOMA_TO_PRESET_MODES:
            return HVAC_MODE_HEAT

        return None

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return [*HVAC_MODES_TO_TAHOMA]

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        await self.async_execute_command(
            COMMAND_SET_OPERATING_MODE, HVAC_MODES_TO_TAHOMA[hvac_mode]
        )

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp."""
        operating_mode = self.select_state(RAMSES_RAMSES_OPERATING_MODE_STATE)

        if operating_mode in TAHOMA_TO_PRESET_MODES:
            return TAHOMA_TO_PRESET_MODES[operating_mode]

        return PRESET_NONE

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes."""
        return [*PRESET_MODES_TO_TAHOMA]

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        if preset_mode == PRESET_DAY_OFF:
            today_end_of_day = dt_util.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            ) + timedelta(days=1)
            time_interval = today_end_of_day

        if preset_mode == PRESET_HOLIDAYS:
            one_week_from_now = dt_util.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            ) + timedelta(days=7)
            time_interval = one_week_from_now

        await self.async_execute_command(
            COMMAND_SET_OPERATING_MODE,
            PRESET_MODES_TO_TAHOMA[preset_mode],
            time_interval.strftime("%Y/%m/%d %H:%M"),
        )

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return the device state attributes."""
        device_info = super().device_info or {}
        device_info["manufacturer"] = "EvoHome"

        return device_info
