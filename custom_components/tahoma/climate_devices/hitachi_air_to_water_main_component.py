"""Support for HitachiAirToWaterMainComponent."""
import logging
from typing import Any, Dict, List

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
)
from homeassistant.const import TEMP_CELSIUS

from ..tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)


TAHOMA_TO_HVAC_MODES = {
    "heating": HVAC_MODE_HEAT,
    "off": HVAC_MODE_OFF,
    "fan": HVAC_MODE_FAN_ONLY,
    "dehumidify": HVAC_MODE_DRY,
    "cooling": HVAC_MODE_COOL,
    "auto": HVAC_MODE_AUTO,
}

HVAC_MODES_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_HVAC_MODES.items()}


class HitachiAirToWaterMainComponent(TahomaDevice, ClimateEntity):
    """Representation of HitachiAirToWaterMainComponent."""

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return 0

    async def async_turn_on(self) -> None:
        """Turn on the device."""
        await self.async_execute_command("setMainOperation", "on")

    async def async_turn_off(self) -> None:
        """Turn off the device."""
        await self.async_execute_command("setMainOperation", "off")

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        return None

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
    def device_info(self) -> Dict[str, Any]:
        """Return the device state attributes."""
        device_info = super().device_info or {}
        device_info["manufacturer"] = "Hitachi"

        return device_info
