"""Support for ValveHeatingTemperatureInterface."""
import logging

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS

from ..entity import OverkizEntity

_LOGGER = logging.getLogger(__name__)

# Map Overkiz HVAC modes to Home Assistant HVAC modes
OVERKIZ_TO_HVAC_MODE = {
    None: HVAC_MODE_HEAT,
}
HVAC_MODE_TO_OVERKIZ = {v: k for k, v in OVERKIZ_TO_HVAC_MODE.items()}

# Map Home Assistant presets to TaHoma presets
PRESET_MODE_TO_OVERKIZ = {
    "comfort": "comfort",
    "eco": "eco",
    "away": "away",
    "frostprotection": "frostprotection",
    "geofencing_mode": "geofencingMode",
}

OVERKIZ_TO_PRESET_MODE = {v: k for k, v in PRESET_MODE_TO_OVERKIZ.items()}


class ValveHeatingTemperatureInterface(OverkizEntity, ClimateEntity):
    """Representation of Valve Heating Temperature Interface device."""

    _attr_hvac_mode = HVAC_MODE_HEAT
    _attr_hvac_modes = [HVAC_MODE_HEAT]
    _attr_preset_modes = [*PRESET_MODE_TO_OVERKIZ]
    _attr_supported_features = SUPPORT_PRESET_MODE | SUPPORT_TARGET_TEMPERATURE
    _attr_temperature_unit = TEMP_CELSIUS

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

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""

        # TODO

        return

    @property
    def preset_mode(self) -> str:
        """Return the current preset mode, e.g., home, away, temp."""
        return OVERKIZ_TO_PRESET_MODE[
            self.executor.select_state("io:DerogationHeatingModeState")
        ]

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        await self.executor.async_execute_command(
            "setDerogation", PRESET_MODE_TO_OVERKIZ[preset_mode]
        )
