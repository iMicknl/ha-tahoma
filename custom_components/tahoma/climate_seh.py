"""Support for Atlantic Electrical Heater IO controller."""
import logging
from typing import List

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVAC_MODE_HEAT, HVAC_MODE_OFF
from homeassistant.const import TEMP_CELSIUS

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
    """Representation of TaHoma IO Atlantic Electrical Heater."""

    def __init__(self, tahoma_device, controller):
        """Init method."""
        super().__init__(tahoma_device, controller)

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return 0

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        return HVAC_MODE_UNKNOWN

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return [HVAC_MODE_OFF, HVAC_MODE_HEAT]

    async def async_down(self, **_):
        """Move heater level down."""
        await self.async_execute_command(COMMAND_DOWN)

    async def async_my(self, **_):
        """Set heater to programmed level."""
        await self.async_execute_command(COMMAND_MY)

    async def async_up(self, **_):
        """Move heater level up."""
        await self.async_execute_command(COMMAND_UP)

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVAC_MODE_HEAT:
            await self.async_execute_command(COMMAND_ON)
        else:
            await self.async_execute_command(COMMAND_OFF)
