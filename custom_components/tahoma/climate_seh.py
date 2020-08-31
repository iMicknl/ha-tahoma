"""Support for Atlantic Electrical Heater IO controller."""
import logging
from typing import List, Optional

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    PRESET_BOOST,
    PRESET_COMFORT,
    PRESET_ECO,
    SUPPORT_PRESET_MODE,
)

from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

COMMAND_DOWN = "down"
COMMAND_MY = "my"
COMMAND_OFF = "off"
COMMAND_ON = "on"
COMMAND_UP = "up"

HVAC_MODE_UNKNOWN = "Unknown"

PRESET_UNKNOWN = "Unknown"


class StatelessExteriorHeating(TahomaDevice, ClimateEntity):
    """Representation of TaHoma Stateless Exterior Heating device."""

    def __init__(self, tahoma_device, controller):
        """Init method."""
        super().__init__(tahoma_device, controller)

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_PRESET_MODE

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp."""
        return None

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes."""
        return [PRESET_ECO, PRESET_COMFORT, PRESET_BOOST]

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        if preset_mode in PRESET_ECO:
            await self.async_execute_command(COMMAND_DOWN)
            await self.async_execute_command(COMMAND_DOWN)
        elif preset_mode == PRESET_COMFORT:
            await self.async_execute_command(COMMAND_DOWN)
            await self.async_execute_command(COMMAND_DOWN)
            await self.async_execute_command(COMMAND_UP)
        elif preset_mode == PRESET_BOOST:
            await self.async_execute_command(COMMAND_UP)
            await self.async_execute_command(COMMAND_UP)
        else:
            _LOGGER.error(
                "Invalid preset mode %s for device %s", preset_mode, self.name
            )

    @property
    def temperature_unit(self) -> Optional[str]:
        """Return the unit of measurement used by the platform."""
        return None

    @property
    def hvac_mode(self) -> Optional[str]:
        """Return hvac operation ie. heat, cool mode."""
        return None

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return [HVAC_MODE_OFF, HVAC_MODE_HEAT]

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVAC_MODE_HEAT:
            await self.async_execute_command(COMMAND_ON)
        else:
            await self.async_execute_command(COMMAND_OFF)

    async def async_my(self, **_):
        """Set heater to programmed level."""
        await self.async_execute_command(COMMAND_MY)
