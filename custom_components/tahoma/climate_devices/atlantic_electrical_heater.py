"""Support for Atlantic Electrical Heater."""
from typing import List, Optional

from homeassistant.components.climate import (
    HVAC_MODE_OFF,
    SUPPORT_PRESET_MODE,
    ClimateEntity,
)
from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT,
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_NONE,
)
from homeassistant.const import TEMP_CELSIUS

from ..tahoma_entity import TahomaEntity

COMMAND_SET_HEATING_LEVEL = "setHeatingLevel"

CORE_ON_OFF_STATE = "core:OnOffState"
IO_TARGET_HEATING_LEVEL_STATE = "io:TargetHeatingLevelState"

PRESET_COMFORT1 = "comfort-1"
PRESET_COMFORT2 = "comfort-2"
PRESET_FROST_PROTECTION = "frost_protection"

TAHOMA_TO_PRESET_MODES = {
    "off": PRESET_NONE,
    "frostprotection": PRESET_FROST_PROTECTION,
    "eco": PRESET_ECO,
    "comfort": PRESET_COMFORT,
    "comfort-1": PRESET_COMFORT1,
    "comfort-2": PRESET_COMFORT2,
}

PRESET_MODES_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_PRESET_MODES.items()}

TAHOMA_TO_HVAC_MODES = {
    "on": HVAC_MODE_HEAT,
    "comfort": HVAC_MODE_HEAT,
    "off": HVAC_MODE_OFF,
}
HVAC_MODES_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_HVAC_MODES.items()}


class AtlanticElectricalHeater(TahomaEntity, ClimateEntity):
    """Representation of Atlantic Electrical Heater."""

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
        return TAHOMA_TO_HVAC_MODES[self.select_state(*CORE_ON_OFF_STATE)]

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return [*HVAC_MODES_TO_TAHOMA]

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        await self.async_execute_command(
            COMMAND_SET_HEATING_LEVEL, HVAC_MODES_TO_TAHOMA[hvac_mode]
        )

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp."""
        return TAHOMA_TO_PRESET_MODES[self.select_state(IO_TARGET_HEATING_LEVEL_STATE)]

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes."""
        return [*PRESET_MODES_TO_TAHOMA]

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        await self.async_execute_command(
            COMMAND_SET_HEATING_LEVEL, PRESET_MODES_TO_TAHOMA[preset_mode]
        )
