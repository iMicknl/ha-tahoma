"""Support for AtlanticPassAPCDHWComponement."""
import logging
from typing import List, Optional

from homeassistant.components.climate import (
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    ClimateEntity,
)
from homeassistant.components.climate.const import (
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_NONE,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS

from ..coordinator import TahomaDataUpdateCoordinator
from ..tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

COMMAND_REFRESH_ECO_TARGET_DWH_TEMPERATURE = "refreshEcoTargetDHWTemperature"
COMMAND_REFRESH_COMFORT_TARGET_DWH_TEMPERATURE = "refreshComfortTargetDHWTemperature"
COMMAND_REFRESH_TARGET_DWH_TEMPERATURE = "refreshTargetDHWTemperature"
COMMAND_SET_DWH_ON_OFF_STATE = "setDHWOnOffState"
COMMAND_SET_ECO_TARGET_DWH_TEMPERATURE = "setEcoTargetDHWTemperature"
COMMAND_SET_COMFORT_TARGET_DWH_TEMPERATURE = "setComfortTargetDHWTemperature"
COMMAND_SET_PASS_APCDHW_MODE = "setPassAPCDHWMode"

CORE_BOOST_ON_OFF_STATE = "core:BoostOnOffState"
CORE_COMFORT_TARGET_DWH_TEMPERATURE_STATE = "core:ComfortTargetDHWTemperatureState"
CORE_DHW_DEROGATION_AVAILABILITY_STATE = "core:DHWDerogationAvailabilityState"
CORE_DWH_ON_OFF_STATE = "core:DHWOnOffState"
CORE_ECO_TARGET_DWH_TEMPERATURE_STATE = "core:EcoTargetDHWTemperatureState"
CORE_STATUS_STATE = "core:StatusState"
CORE_TARGET_DWH_TEMPERATURE_STATE = "core:TargetDHWTemperatureState"

DWH_OFF_STATE = "off"
DHW_ON_STATE = "on"

IO_PASS_APCDHW_CONFIGURATION_STATE = "io:PassAPCDHWConfigurationState"
IO_PASS_APCDWH_MODE_STATE = "io:PassAPCDHWModeState"
IO_PASS_APCDHW_PROFILE_STATE = "io:PassAPCDHWProfileState"

PASS_APCDHW_MODE_COMFORT = "comfort"
PASS_APCDHW_MODE_ECO = "eco"
PASS_APCDWH_MODE_INTERNAL_SCHEDULING = "internalScheduling"
PASS_APCDHW_MODE_STOP = "stop"

MAP_HVAC_MODES = {
    DHW_ON_STATE: HVAC_MODE_HEAT,
    DWH_OFF_STATE: HVAC_MODE_OFF,
}
MAP_REVERSE_HVAC_MODES = dict(map(reversed, MAP_HVAC_MODES.items()))

MAP_PRESET_MODES = {
    PASS_APCDHW_MODE_COMFORT: PRESET_COMFORT,
    PASS_APCDHW_MODE_ECO: PRESET_ECO,
    PASS_APCDWH_MODE_INTERNAL_SCHEDULING: PASS_APCDWH_MODE_INTERNAL_SCHEDULING,
    PASS_APCDHW_MODE_STOP: PASS_APCDHW_MODE_STOP,
}
MAP_REVERSE_PRESET_MODES = dict(map(reversed, MAP_PRESET_MODES.items()))


class AtlanticPassAPCDHW(TahomaDevice, ClimateEntity):
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
    def min_temp(self) -> float:
        """Return minimum temperature."""
        # FIXME: only for naia micro ?
        return 30

    @property
    def max_temp(self) -> float:
        """Return maximum temperature."""
        # FIXME: only for naia micro ?
        return 65

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp."""
        return MAP_PRESET_MODES[self.select_state(IO_PASS_APCDWH_MODE_STATE)]

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes."""
        return [*MAP_REVERSE_PRESET_MODES]

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        await self.async_execute_command(
            COMMAND_SET_DWH_ON_OFF_STATE, MAP_REVERSE_HVAC_MODES[hvac_mode]
        )

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        return MAP_HVAC_MODES[self.select_state(CORE_DWH_ON_OFF_STATE)]

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return [*MAP_REVERSE_HVAC_MODES]

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        await self.async_execute_command(
            COMMAND_SET_PASS_APCDHW_MODE, MAP_REVERSE_PRESET_MODES[preset_mode]
        )
        await self.async_execute_command("refreshTargetDHWTemperature")

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new temperature for current preset."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if self.preset_mode == PRESET_ECO:
            await self.async_execute_command(
                COMMAND_SET_ECO_TARGET_DWH_TEMPERATURE, temperature
            )
        elif self.preset_mode == PRESET_COMFORT:
            await self.async_execute_command(
                COMMAND_SET_COMFORT_TARGET_DWH_TEMPERATURE, temperature
            )

        await self.async_execute_command("refreshTargetDHWTemperature")

    @property
    def target_temperature(self):
        """Return the temperature corresponding to the PRESET."""
        if self.preset_mode == PRESET_ECO:
            return self.select_state(CORE_ECO_TARGET_DWH_TEMPERATURE_STATE)
        elif self.preset_mode == PRESET_COMFORT:
            return self.select_state(CORE_COMFORT_TARGET_DWH_TEMPERATURE_STATE)
        else:
            return self.select_state(CORE_TARGET_DWH_TEMPERATURE_STATE)

    @property
    def current_temperature(self):
        """Return current temperature."""
        return self.target_temperature
