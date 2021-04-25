"""Support for AtlanticPassAPCHeatingAndCoolingZone."""
from typing import List, Optional

from homeassistant.components.climate import (
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    ClimateEntity,
)
from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    PRESET_COMFORT,
    PRESET_ECO,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS

from ..tahoma_entity import TahomaEntity

PRESET_PROG = "prog"
PRESET_MANUAL = "manual"

HVAC_MODES = [HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_AUTO]
PRESET_MODES = [PRESET_COMFORT, PRESET_ECO, PRESET_PROG, PRESET_MANUAL]

# AtlanticPassAPCHeatingAndCoolingZone comes in minimal two flavours with slightly different commands.
# (io:AtlanticPassAPCZoneControlZoneComponent and io:AtlanticPassAPCHeatingAndCoolingZoneComponent)


class AtlanticPassAPCHeatingAndCoolingZone(TahomaEntity, ClimateEntity):
    """Representation of TaHoma IO Atlantic Electrical Heater."""

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_PRESET_MODE | SUPPORT_TARGET_TEMPERATURE

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        if self.select_state("core:DerogationOnOffState") == "on":
            return HVAC_MODE_HEAT
        else:
            return HVAC_MODE_OFF

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return [HVAC_MODES]

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVAC_MODE_HEAT:
            await self.async_execute_command("setDerogationOnOffState", "on")

        if hvac_mode == HVAC_MODE_OFF:
            await self.async_execute_command("setPassAPCHeatingMode", "stop")
            await self.async_execute_command("setDerogationOnOffState", "off")

    @property
    def current_temperature(self):
        """Return current temperature."""
        return None

    @property
    def target_temperature(self) -> None:
        """Return the temperature corresponding to the PRESET."""
        return self.select_state("core:DerogatedTargetTemperatureState")

        # if self.preset_mode in [PRESET_COMFORT, PRESET_BOOST]:
        #     return self.select_state(CORE_COMFORT_TARGET_DWH_TEMPERATURE_STATE)

        # return self.select_state(CORE_TARGET_DWH_TEMPERATURE_STATE)

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new temperature for current preset."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        # if self.preset_mode == PRESET_ECO:
        #     await self.async_execute_command(
        #         COMMAND_SET_ECO_TARGET_DWH_TEMPERATURE, temperature
        #     )

        # if self.preset_mode in [PRESET_COMFORT, PRESET_BOOST]:
        #     await self.async_execute_command(
        #         COMMAND_SET_COMFORT_TARGET_DWH_TEMPERATURE, temperature
        #     )

        await self.async_execute_command("setDerogatedTargetTemperature", temperature)

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., auto, smart, interval, favorite."""
        state_pass_apc_heating_mode = self.select_state("io:PassAPCHeatingModeState")

        if state_pass_apc_heating_mode == "internalScheduling":
            return PRESET_PROG

        return None

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes."""
        return PRESET_MODES

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode."""
        if preset_mode == PRESET_PROG:
            await self.async_execute_command(
                "setPassAPCHeatingMode", "internalScheduling"
            )
            await self.async_execute_command("setDerogationOnOffState", "off")
