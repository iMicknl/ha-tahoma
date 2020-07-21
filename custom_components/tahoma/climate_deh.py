"""Support for Atlantic Electrical Heater IO controller."""
from typing import List, Optional

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import ATTR_TEMPERATURE, UNIT_PERCENTAGE

from .tahoma_device import TahomaDevice

COMMAND_SET_LEVEL = "setLevel"

CORE_LEVEL_STATE = "core:LevelState"


class DimmerExteriorHeating(TahomaDevice, ClimateEntity):
    """Representation of TaHoma IO Atlantic Electrical Heater."""

    def __init__(self, tahoma_device, controller):
        """Init method."""
        super().__init__(tahoma_device, controller)
        self._saved_level = self.select_state(CORE_LEVEL_STATE)

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_TARGET_TEMPERATURE

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return UNIT_PERCENTAGE

    @property
    def min_temp(self) -> float:
        """Return minimum percentage."""
        return 0

    @property
    def max_temp(self) -> float:
        """Return maximum percentage."""
        return 100

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self.select_state(CORE_LEVEL_STATE)

    def set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        level = kwargs.get(ATTR_TEMPERATURE)
        if level is None:
            return
        self.apply_action(COMMAND_SET_LEVEL, level)

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        if self.select_state(CORE_LEVEL_STATE) == 0:
            return HVAC_MODE_OFF
        return HVAC_MODE_HEAT

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return [HVAC_MODE_OFF, HVAC_MODE_HEAT]

    def set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        level = 0
        if hvac_mode == HVAC_MODE_HEAT:
            level = self._saved_level
        else:
            self._saved_level = self.target_temperature
        self.apply_action(COMMAND_SET_LEVEL, level)
