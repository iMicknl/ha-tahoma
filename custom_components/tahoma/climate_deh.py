"""Support for Atlantic Electrical Heater IO controller."""
import logging
from typing import Any, Dict, List, Optional

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ATTR_CURRENT_TEMPERATURE,
    ATTR_HVAC_MODES,
    ATTR_MAX_TEMP,
    ATTR_MIN_TEMP,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import ATTR_TEMPERATURE, UNIT_PERCENTAGE
from homeassistant.helpers.typing import ServiceDataType

from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

COMMAND_GET_LEVEL = "getLevel"
COMMAND_SET_LEVEL = "setLevel"

CORE_LEVEL_STATE = "core:LevelState"


async def async_service_temperature_set(
    entity: ClimateEntity, service: ServiceDataType
) -> None:
    """Handle set temperature service."""
    kwargs = {}

    for value, temp in service.data.items():
        kwargs[value] = temp

    await entity.async_set_temperature(**kwargs)


class DimmerExteriorHeating(TahomaDevice, ClimateEntity):
    """Representation of TaHoma IO Atlantic Electrical Heater."""

    def __init__(self, tahoma_device, controller):
        """Init method."""
        super().__init__(tahoma_device, controller)
        self._saved_level = 100 - self.select_state(CORE_LEVEL_STATE)

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
        return 100 - self.select_state(CORE_LEVEL_STATE)

    @property
    def capability_attributes(self) -> Optional[Dict[str, Any]]:
        """Return the capability attributes."""
        return {
            ATTR_HVAC_MODES: self.hvac_modes,
            ATTR_MIN_TEMP: self.min_temp,
            ATTR_MAX_TEMP: self.max_temp,
        }

    @property
    def state_attributes(self) -> Dict[str, Any]:
        """Return the optional state attributes."""
        return {
            ATTR_CURRENT_TEMPERATURE: None,
            ATTR_TEMPERATURE: self.target_temperature,
        }

    def set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        level = kwargs.get(ATTR_TEMPERATURE)
        if level is None:
            return
        self.apply_action(COMMAND_SET_LEVEL, 100 - int(level))
        self.apply_action(COMMAND_GET_LEVEL)

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        if self.select_state(CORE_LEVEL_STATE) == 100:
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
        self.apply_action(COMMAND_SET_LEVEL, 100 - int(level))
        self.apply_action(COMMAND_GET_LEVEL)
