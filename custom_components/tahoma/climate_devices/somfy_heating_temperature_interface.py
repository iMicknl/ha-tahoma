"""Support for Atlantic Electrical Heater."""
from typing import Optional

from homeassistant.components.climate import SUPPORT_PRESET_MODE, ClimateEntity
from homeassistant.components.climate.const import (
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_HEAT,
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT_COOL,
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_NONE,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS

from ..entity import OverkizEntity

COMMAND_SET_HEATING_LEVEL = "setHeatingLevel"

CORE_TARGET_TEMPERATURE_STATE = "core:TargetTemperatureState"
CORE_ON_OFF_STATE = "core:OnOffState"
IO_TARGET_HEATING_LEVEL_STATE = "io:TargetHeatingLevelState"

PRESET_COMFORT1 = "comfort-1"
PRESET_COMFORT2 = "comfort-2"
PRESET_FROST_PROTECTION = "frost_protection"

TAHOMA_TO_PRESET_MODES = {
    "secured": PRESET_FROST_PROTECTION,
    "eco": PRESET_ECO,
    "comfort": PRESET_COMFORT,
    "free": PRESET_NONE,
}

PRESET_MODES_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_PRESET_MODES.items()}

TAHOMA_TO_HVAC_MODES = {
    "auto": HVAC_MODE_AUTO,
    "manu": HVAC_MODE_HEAT_COOL,
}

HVAC_MODES_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_HVAC_MODES.items()}

TAHOMA_TO_HVAC_ACTION = {"cooling": CURRENT_HVAC_COOL, "heating": CURRENT_HVAC_HEAT}


class SomfyHeatingTemperatureInterface(OverkizEntity, ClimateEntity):
    """Representation of Somfy Heating Temperature Interface."""

    _attr_hvac_modes = [*HVAC_MODES_TO_TAHOMA]
    _attr_preset_modes = [*PRESET_MODES_TO_TAHOMA]
    _attr_supported_features = SUPPORT_PRESET_MODE
    _attr_temperature_unit = TEMP_CELSIUS

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        return TAHOMA_TO_HVAC_MODES[
            self.executor.select_state("ovp:HeatingTemperatureInterfaceActiveModeState")
        ]

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        await self.executor.async_execute_command(
            "setActiveMode", HVAC_MODES_TO_TAHOMA[hvac_mode]
        )

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp."""
        return TAHOMA_TO_PRESET_MODES[
            self.executor.select_state(
                "ovp:HeatingTemperatureInterfaceSetPointModeState"
            )
        ]

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        await self.executor.async_execute_command(
            "setManuAndSetPointModes", PRESET_MODES_TO_TAHOMA[preset_mode]
        )

    @property
    def hvac_action(self) -> str:
        """Return the current running hvac operation if supported."""
        current_operation = self.executor.select_state(
            "ovp:HeatingTemperatureInterfaceOperatingModeState"
        )

        if current_operation in TAHOMA_TO_HVAC_ACTION:
            return TAHOMA_TO_HVAC_ACTION[current_operation]

    @property
    def target_temperature(self) -> float:
        """Return the temperature."""
        return self.executor.select_state(CORE_TARGET_TEMPERATURE_STATE)

    @property
    def current_temperature(self):
        """Return current temperature."""
        mode = self.executor.select_state(
            "ovp:HeatingTemperatureInterfaceSetPointModeState"
        )

        if mode == "comfort":
            return self.executor.select_state("core:ComfortRoomTemperatureState")

        if mode == "eco":
            return self.executor.select_state("core:EcoRoomTemperatureState")

        if mode == "secured":
            return self.executor.select_state("core:SecuredPositionTemperatureState")

        return None

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new temperature."""

        mode = self.executor.select_state(
            "ovp:HeatingTemperatureInterfaceSetPointModeState"
        )
        temperature = kwargs.get(ATTR_TEMPERATURE)

        if mode == "comfort":
            return await self.executor.async_execute_command(
                "setComfortTemperature", temperature
            )

        if mode == "eco":
            return await self.executor.async_execute_command(
                "setEcoTemperature", temperature
            )
        if mode == "secured":
            return await self.executor.async_execute_command(
                "setSecuredPositionTemperature", temperature
            )
        return None
