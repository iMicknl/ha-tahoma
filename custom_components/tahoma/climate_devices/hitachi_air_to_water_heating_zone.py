"""Support for HitachiAirToWaterHeatingZone."""
import logging
from typing import Any, Dict, List, Optional

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    PRESET_COMFORT,
    PRESET_ECO,
    SUPPORT_PRESET_MODE,
)
from homeassistant.const import TEMP_CELSIUS

from ..tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

COMMAND_SET_TARGET_MODE = "setTargetMode"

MODBUS_YUTAKI_TARGET_MODE_STATE = "modbus:YutakiTargetModeState"

PRESET_STATE_ECO = "eco"
PRESET_STATE_COMFORT = "comfort"

TAHOMA_TO_HVAC_MODE = {
    "heating": HVAC_MODE_HEAT,
    "off": HVAC_MODE_OFF,
    "fan": HVAC_MODE_FAN_ONLY,
    "dehumidify": HVAC_MODE_DRY,
    "cooling": HVAC_MODE_COOL,
    "auto": HVAC_MODE_AUTO,
}

HVAC_MODE_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_HVAC_MODE.items()}

TAHOMA_TO_PRESET_MODE = {
    PRESET_STATE_COMFORT: PRESET_COMFORT,
    PRESET_STATE_ECO: PRESET_ECO,
}

PRESET_MODE_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_PRESET_MODE.items()}


class HitachiAirToWaterHeatingZone(TahomaDevice, ClimateEntity):
    """Representation of HitachiAirToWaterHeatingZone."""

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return the device state attributes."""
        device_info = super().device_info or {}
        device_info["manufacturer"] = "Hitachi"

        return device_info

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
        return None

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return []

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        # TODO implement

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes."""
        return [*PRESET_MODE_TO_TAHOMA]

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp."""
        return TAHOMA_TO_PRESET_MODE[self.select_state(MODBUS_YUTAKI_TARGET_MODE_STATE)]

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        await self.async_execute_command(
            COMMAND_SET_TARGET_MODE, TAHOMA_TO_PRESET_MODE[preset_mode]
        )
