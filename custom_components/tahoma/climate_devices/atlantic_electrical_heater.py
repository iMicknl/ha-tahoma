"""Support for Atlantic Electrical Heater IO controller."""
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

from ..tahoma_device import TahomaEntity

COMMAND_SET_HEATING_LEVEL = "setHeatingLevel"

IO_TARGET_HEATING_LEVEL_STATE = "io:TargetHeatingLevelState"

PRESET_FREEZE = "Freeze"
PRESET_FROST_PROTECTION = "frostprotection"
PRESET_OFF = "off"

MAP_PRESET_MODES = {
    PRESET_OFF: PRESET_NONE,
    PRESET_FROST_PROTECTION: PRESET_FREEZE,
    PRESET_ECO: PRESET_ECO,
    PRESET_COMFORT: PRESET_COMFORT,
}

MAP_REVERSE_PRESET_MODES = {v: k for k, v in MAP_PRESET_MODES.items()}

MAP_HVAC_MODES = {HVAC_MODE_HEAT: PRESET_COMFORT, HVAC_MODE_OFF: PRESET_OFF}


class AtlanticElectricalHeater(TahomaEntity, ClimateEntity):
    """Representation of TaHoma IO Atlantic Electrical Heater."""

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
        return HVAC_MODE_OFF if self.preset_mode == PRESET_NONE else HVAC_MODE_HEAT

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return [*MAP_HVAC_MODES]

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp."""
        return MAP_PRESET_MODES[self.select_state(IO_TARGET_HEATING_LEVEL_STATE)]

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes."""
        return [PRESET_NONE, PRESET_FREEZE, PRESET_ECO, PRESET_COMFORT]

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        await self.async_execute_command(
            COMMAND_SET_HEATING_LEVEL, MAP_HVAC_MODES[hvac_mode]
        )

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        await self.async_execute_command(
            COMMAND_SET_HEATING_LEVEL, MAP_REVERSE_PRESET_MODES[preset_mode]
        )

    async def async_turn_off(self) -> None:
        """Turn off the device."""
        await self.async_execute_command(COMMAND_SET_HEATING_LEVEL, PRESET_OFF)
