"""Support for Atlantic Electrical Heater (With Adjustable Temperature Setpoint)."""
from typing import List, Optional

from homeassistant.components.climate import (
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    ClimateEntity,
)
from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_NONE,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS

from ..tahoma_device import TahomaDevice

COMMAND_SET_HEATING_LEVEL = "setHeatingLevel"
COMMAND_SET_TARGET_TEMPERATURE = "setTargetTemperature"
COMMAND_SET_OPERATING_MODE = "setOperatingMode"

CORE_OPERATING_MODE_STATE = "core:OperatingModeState"
CORE_TARGET_TEMPERATURE_STATE = "core:TargetTemperatureState"
IO_TARGET_HEATING_LEVEL_STATE = "io:TargetHeatingLevelState"

PRESET_BOOST = "boost"
PRESET_COMFORT1 = "comfort 1"
PRESET_COMFORT2 = "comfort 2"
PRESET_FROST_PROTECTION = "Frost Protection"
PRESET_SECURED = "Secured"

PRESET_STATE_FROST_PROTECTION = "frostprotection"
PRESET_STATE_OFF = "off"
PRESET_STATE_ECO = "eco"
PRESET_STATE_BOOST = "boost"
PRESET_STATE_COMFORT = "comfort"
PRESET_STATE_COMFORT1 = "comfort-1"
PRESET_STATE_COMFORT2 = "comfort-2"

# Map Home Assistant presets to TaHoma presets
PRESET_MODE_TO_TAHOMA = {
    PRESET_BOOST: PRESET_STATE_BOOST,
    PRESET_COMFORT1: PRESET_STATE_COMFORT1,
    PRESET_COMFORT2: PRESET_STATE_COMFORT2,
    PRESET_COMFORT: PRESET_STATE_COMFORT,
    PRESET_ECO: PRESET_STATE_ECO,
    PRESET_FROST_PROTECTION: PRESET_STATE_FROST_PROTECTION,
    PRESET_NONE: PRESET_STATE_OFF,
}

TAHOMA_TO_PRESET_MODE = {v: k for k, v in PRESET_MODE_TO_TAHOMA.items()}

# Map TaHoma HVAC modes to Home Assistant HVAC modes
TAHOMA_TO_HVAC_MODE = {
    "auto": HVAC_MODE_AUTO,
    "basic": HVAC_MODE_HEAT,
    "standby": HVAC_MODE_OFF,
    "internal": HVAC_MODE_AUTO,
    "off": HVAC_MODE_OFF,
}

HVAC_MODE_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_HVAC_MODE.items()}


class AtlanticElectricalHeater(TahomaDevice, ClimateEntity):
    """Representation of Atlantic Electrical Heater (With Adjustable Temperature Setpoint)."""

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        supported_features = 0

        if self.has_command(COMMAND_SET_HEATING_LEVEL):
            supported_features |= SUPPORT_PRESET_MODE

        if self.has_command(COMMAND_SET_TARGET_TEMPERATURE):
            supported_features |= SUPPORT_TARGET_TEMPERATURE

        return supported_features

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return [*HVAC_MODE_TO_TAHOMA]

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        return TAHOMA_TO_HVAC_MODE[self.select_state(CORE_OPERATING_MODE_STATE)]

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        await self.async_execute_command(
            COMMAND_SET_OPERATING_MODE, HVAC_MODE_TO_TAHOMA[hvac_mode]
        )

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes."""
        return [*PRESET_MODE_TO_TAHOMA]

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp."""
        return TAHOMA_TO_PRESET_MODE[self.select_state(IO_TARGET_HEATING_LEVEL_STATE)]

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        await self.async_execute_command(
            COMMAND_SET_HEATING_LEVEL, TAHOMA_TO_PRESET_MODE[preset_mode]
        )

    async def async_turn_off(self) -> None:
        """Turn off the device."""
        await self.async_execute_command("setOperatingMode", "off")

    @property
    def target_temperature(self) -> None:
        """Return the temperature."""
        return self.select_state(CORE_TARGET_TEMPERATURE_STATE)

    # @property
    # def current_temperature(self):
    #     """Return current temperature."""
    #     return self.target_temperature  # TODO Retrieve current temperature from sensor

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        await self.async_execute_command(COMMAND_SET_TARGET_TEMPERATURE, temperature)
