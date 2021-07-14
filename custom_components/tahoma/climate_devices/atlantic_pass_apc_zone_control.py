"""Support for Atlantic Pass APC Zone Control."""
import logging
from typing import List

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_COOL,
    HVAC_MODE_DRY,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
)
from homeassistant.const import TEMP_CELSIUS

from ..tahoma_entity import TahomaEntity

_LOGGER = logging.getLogger(__name__)

COMMAND_SET_PASS_APC_OPERATING_MODE = "setPassAPCOperatingMode"

IO_PASS_APC_OPERATING_MODE_STATE = "io:PassAPCOperatingModeState"

# Map TaHoma HVAC modes to Home Assistant HVAC modes
TAHOMA_TO_HVAC_MODE = {
    "heating": HVAC_MODE_HEAT,
    "drying": HVAC_MODE_DRY,
    "cooling": HVAC_MODE_COOL,
    "stop": HVAC_MODE_OFF,
}

HVAC_MODE_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_HVAC_MODE.items()}


class AtlanticPassAPCZoneControl(TahomaEntity, ClimateEntity):
    """Representation of Atlantic Pass APC Zone Control."""

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        supported_features = 0

        return supported_features

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return [*HVAC_MODE_TO_TAHOMA]

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        return TAHOMA_TO_HVAC_MODE[self.select_state(IO_PASS_APC_OPERATING_MODE_STATE)]

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        await self.async_execute_command(
            COMMAND_SET_PASS_APC_OPERATING_MODE, HVAC_MODE_TO_TAHOMA[hvac_mode]
        )
