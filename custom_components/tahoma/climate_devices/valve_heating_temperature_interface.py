"""Support for ValveHeatingTemperatureInterface."""
import logging

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS

from ..entity import OverkizEntity

_LOGGER = logging.getLogger(__name__)


class ValveHeatingTemperatureInterface(OverkizEntity, ClimateEntity):
    """Representation of Valve Heating Temperature Interface device."""

    _attr_hvac_mode = None
    _attr_hvac_modes = [HVAC_MODE_HEAT]
    _attr_preset_mode = None
    _attr_supported_features = SUPPORT_TARGET_TEMPERATURE
    _attr_temperature_unit = TEMP_CELSIUS

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        return

    @property
    def target_temperature(self) -> None:
        """Return the temperature."""
        return self.executor.select_state("core:TargetTemperatureState")

    @property
    def current_temperature(self):
        """Return current temperature."""
        return self.executor.select_state("core:ComfortRoomTemperatureState")

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        await self.executor.async_execute_command("", temperature)
