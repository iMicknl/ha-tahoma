"""Support for AtlanticHeatRecoveryVentilation."""

import logging
from typing import List, Optional

from homeassistant.components.climate import (
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    SUPPORT_FAN_MODE,
    SUPPORT_PRESET_MODE,
    ClimateEntity,
)
from homeassistant.components.climate.const import (
    FAN_AUTO,
    FAN_HIGH,
    PRESET_COMFORT,
    PRESET_ECO,
)
from homeassistant.const import TEMP_CELSIUS

from ..tahoma_device import TahomaDevice

FAN_BOOST = "boost"
FAN_AWAY = "away"

PRESET_PROG = "prog"
PRESET_MANUAL = "manual"

COMMAND_SET_AIR_DEMAND_MODE = "setAirDemandMode"
COMMAND_SET_VENTILATION_CONFIGURATION_MODE = "setVentilationConfigurationMode"
COMMAND_SET_VENTILATION_MODE = "setVentilationMode"

IO_AIR_DEMAND_MODE_STATE = "io:AirDemandModeState"

FAN_MODE_TO_TAHOMA = {
    FAN_AUTO: "auto",
    FAN_BOOST: "boost",
    FAN_HIGH: "high",
    FAN_AWAY: "away",
}

TAHOMA_TO_FAN_MODE = {v: k for k, v in FAN_MODE_TO_TAHOMA.items()}

HVAC_MODES = [HVAC_MODE_COOL, HVAC_MODE_HEAT]
PRESET_MODES = [PRESET_COMFORT, PRESET_ECO, PRESET_PROG, PRESET_MANUAL]
_LOGGER = logging.getLogger(__name__)


class AtlanticHeatRecoveryVentilation(TahomaDevice, ClimateEntity):
    """Representation of a AtlanticHeatRecoveryVentilation device."""

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS  # TODO Investigate why this is required..

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return SUPPORT_PRESET_MODE | SUPPORT_FAN_MODE

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        state = self.select_state("io:VentilationModeState")
        _LOGGER.debug(state)
        cooling = state.get("cooling")

        if cooling == "on":
            return HVAC_MODE_COOL
        else:
            return HVAC_MODE_HEAT

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return [HVAC_MODES]

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVAC_MODE_COOL:
            await self.async_execute_command(
                COMMAND_SET_VENTILATION_MODE, {"cooling": "on"}
            )

        if hvac_mode == HVAC_MODE_HEAT:
            await self.async_execute_command(
                COMMAND_SET_VENTILATION_MODE, {"cooling": "off"}
            )

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., auto, smart, interval, favorite."""
        state_ventilation_configuration = self.select_state(
            "io:VentilationConfigurationModeState"
        )
        state_ventilation_mode = self.select_state("io:VentilationModeState")
        state_prog = state_ventilation_mode.get("prog")

        if state_prog == "on":
            return PRESET_PROG

        if state_ventilation_configuration == "comfort":
            return PRESET_COMFORT

        if state_ventilation_configuration == "manual":
            return PRESET_MANUAL

        if state_ventilation_configuration == "eco":
            return PRESET_ECO

        return None

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes."""
        return PRESET_MODES

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""

        if preset_mode == PRESET_COMFORT:
            await self.async_execute_command(
                COMMAND_SET_VENTILATION_CONFIGURATION_MODE, "comfort"
            )
            await self.async_execute_command(
                COMMAND_SET_VENTILATION_MODE, {"prog": "off"}
            )

        if preset_mode == PRESET_PROG:
            await self.async_execute_command(
                COMMAND_SET_VENTILATION_CONFIGURATION_MODE, "standard"
            )
            await self.async_execute_command(
                COMMAND_SET_VENTILATION_MODE, {"prog": "on"}
            )

        if preset_mode == PRESET_MANUAL:
            await self.async_execute_command(
                COMMAND_SET_VENTILATION_CONFIGURATION_MODE, "standard"
            )
            await self.async_execute_command(
                COMMAND_SET_VENTILATION_MODE, {"prog": "off"}
            )

        if preset_mode == PRESET_ECO:
            await self.async_execute_command(
                COMMAND_SET_VENTILATION_CONFIGURATION_MODE, "eco"
            )
            await self.async_execute_command(
                COMMAND_SET_VENTILATION_MODE, {"prog": "off"}
            )

    @property
    def fan_mode(self) -> Optional[str]:
        """Return the fan setting."""
        return TAHOMA_TO_FAN_MODE[self.select_state(IO_AIR_DEMAND_MODE_STATE)]

    @property
    def fan_modes(self) -> Optional[List[str]]:
        """Return the list of available fan modes."""
        return [*FAN_MODE_TO_TAHOMA]

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        await self.async_execute_command(
            COMMAND_SET_AIR_DEMAND_MODE, FAN_MODE_TO_TAHOMA[fan_mode]
        )
