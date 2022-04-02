"""Support for AtlanticHeatRecoveryVentilation."""
from typing import List, Optional

from pyoverkiz.enums import OverkizCommand, OverkizCommandParam, OverkizState

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    FAN_AUTO,
    HVAC_MODE_FAN_ONLY,
    SUPPORT_FAN_MODE,
    SUPPORT_PRESET_MODE,
)
from homeassistant.const import TEMP_CELSIUS

from ..coordinator import OverkizDataUpdateCoordinator
from ..entity import OverkizEntity

FAN_BOOST = "home_boost"
FAN_KITCHEN = "kitchen_boost"
FAN_AWAY = "away"
FAN_BYPASS = "bypass_boost"

PRESET_AUTO = "auto"
PRESET_PROG = "prog"
PRESET_MANUAL = "manual"

OVERKIZ_TO_FAN_MODES = {
    OverkizCommandParam.AUTO: FAN_AUTO,
    OverkizCommandParam.AWAY: FAN_AWAY,
    OverkizCommandParam.BOOST: FAN_BOOST,
    OverkizCommandParam.HIGH: FAN_KITCHEN,
    None: FAN_BYPASS,
}

FAN_MODES_TO_OVERKIZ = {v: k for k, v in OVERKIZ_TO_FAN_MODES.items()}

PRESET_MODES = [PRESET_AUTO, PRESET_PROG, PRESET_MANUAL]


class AtlanticHeatRecoveryVentilation(OverkizEntity, ClimateEntity):
    """Representation of a AtlanticHeatRecoveryVentilation device."""

    def __init__(self, device_url: str, coordinator: OverkizDataUpdateCoordinator):
        """Init method."""
        super().__init__(device_url, coordinator)
        self.temperature_device = self.executor.linked_device(4)

    @property
    def current_temperature(self) -> Optional[float]:
        """Return the current temperature."""
        return self.temperature_device.states.get(OverkizState.CORE_TEMPERATURE).value

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return SUPPORT_PRESET_MODE | SUPPORT_FAN_MODE

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        return HVAC_MODE_FAN_ONLY

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return [HVAC_MODE_FAN_ONLY]

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Not implemented since there is only one hvac_mode."""

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., auto, smart, interval, favorite."""
        ventilation_configuration = self.executor.select_state(
            OverkizState.IO_VENTILATION_CONFIGURATION_MODE
        )

        ventilation_mode = self.executor.select_state(OverkizState.IO_VENTILATION_MODE)
        prog = ventilation_mode.get(OverkizCommandParam.PROG)

        if prog == OverkizCommandParam.ON:
            return PRESET_PROG

        if ventilation_configuration == OverkizCommandParam.COMFORT:
            return PRESET_AUTO

        if ventilation_configuration == OverkizCommandParam.STANDARD:
            return PRESET_MANUAL

        return None

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes."""
        return PRESET_MODES

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        if preset_mode == PRESET_AUTO:
            await self.executor.async_execute_command(
                OverkizCommand.SET_VENTILATION_CONFIGURATION_MODE,
                OverkizCommandParam.COMFORT,
            )
            await self._set_ventilation_mode(prog=OverkizCommandParam.OFF)

        if preset_mode == PRESET_PROG:
            await self.executor.async_execute_command(
                OverkizCommand.SET_VENTILATION_CONFIGURATION_MODE,
                OverkizCommandParam.STANDARD,
            )
            await self._set_ventilation_mode(prog=OverkizCommandParam.ON)

        if preset_mode == PRESET_MANUAL:
            await self.executor.async_execute_command(
                OverkizCommand.SET_VENTILATION_CONFIGURATION_MODE,
                OverkizCommandParam.STANDARD,
            )
            await self._set_ventilation_mode(prog=OverkizCommandParam.OFF)

        await self.executor.async_execute_command(
            OverkizCommand.REFRESH_VENTILATION_STATE,
        )
        await self.executor.async_execute_command(
            OverkizCommand.REFRESH_VENTILATION_CONFIGURATION_MODE,
        )

    @property
    def fan_mode(self) -> Optional[str]:
        """Return the fan setting."""
        ventilation_mode = self.executor.select_state(OverkizState.IO_VENTILATION_MODE)
        cooling = ventilation_mode.get(OverkizCommandParam.COOLING)

        if cooling == OverkizCommandParam.ON:
            return FAN_BYPASS
        else:
            return OVERKIZ_TO_FAN_MODES[
                self.executor.select_state(OverkizState.IO_AIR_DEMAND_MODE)
            ]

    @property
    def fan_modes(self) -> Optional[List[str]]:
        """Return the list of available fan modes."""
        return [*FAN_MODES_TO_OVERKIZ]

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        if fan_mode == FAN_BYPASS:
            await self.executor.async_execute_command(
                OverkizCommand.SET_AIR_DEMAND_MODE, OverkizCommandParam.AUTO
            )
            await self._set_ventilation_mode(cooling=OverkizCommandParam.ON)
        else:
            await self._set_ventilation_mode(cooling=OverkizCommandParam.OFF)
            await self.executor.async_execute_command(
                OverkizCommand.SET_AIR_DEMAND_MODE, FAN_MODES_TO_OVERKIZ[fan_mode]
            )

        await self.executor.async_execute_command(
            OverkizCommand.REFRESH_VENTILATION_STATE,
        )

    async def _set_ventilation_mode(
        self,
        cooling=None,
        prog=None,
    ):
        """Execute ventilation mode command with all parameters."""
        ventilation_mode = self.executor.select_state(OverkizState.IO_VENTILATION_MODE)

        if cooling:
            ventilation_mode[OverkizCommandParam.COOLING] = cooling

        if prog:
            ventilation_mode[OverkizCommandParam.PROG] = prog

        await self.executor.async_execute_command(
            OverkizCommand.SET_VENTILATIN_MODE, ventilation_mode
        )
