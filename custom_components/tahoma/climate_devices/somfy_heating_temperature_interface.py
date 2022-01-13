"""Support for Somfy Heating Temperature Interface."""
import logging
from typing import Optional

from homeassistant.components.climate import SUPPORT_PRESET_MODE, ClimateEntity
from homeassistant.components.climate.const import (
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_HEAT,
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_OFF,
    PRESET_AWAY,
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_NONE,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS
from pyoverkiz.enums import OverkizCommand, OverkizCommandParam, OverkizState

from ..coordinator import OverkizDataUpdateCoordinator
from ..entity import OverkizEntity

_LOGGER = logging.getLogger(__name__)

OVERKIZ_TO_PRESET_MODES = {
    OverkizCommandParam.SECURED: PRESET_AWAY,
    OverkizCommandParam.ECO: PRESET_ECO,
    OverkizCommandParam.COMFORT: PRESET_COMFORT,
    OverkizCommandParam.FREE: PRESET_NONE,
}

PRESET_MODES_TO_OVERKIZ = {v: k for k, v in OVERKIZ_TO_PRESET_MODES.items()}

OVERKIZ_TO_HVAC_MODES = {
    OverkizCommandParam.AUTO: HVAC_MODE_AUTO,
    OverkizCommandParam.MANU: HVAC_MODE_HEAT_COOL,
}

HVAC_MODES_TO_OVERKIZ = {v: k for k, v in OVERKIZ_TO_HVAC_MODES.items()}

OVERKIZ_TO_HVAC_ACTION = {
    OverkizCommandParam.COOLING: CURRENT_HVAC_COOL,
    OverkizCommandParam.HEATING: CURRENT_HVAC_HEAT,
}

MAP_PRESET_TEMPERATURES = {
    PRESET_COMFORT: OverkizState.CORE_COMFORT_ROOM_TEMPERATURE,
    PRESET_ECO: OverkizState.CORE_ECO_ROOM_TEMPERATURE,
    PRESET_AWAY: OverkizState.CORE_SECURED_POSITION_TEMPERATURE,
}

MODE_COMMAND_MAPPING = {
    OverkizCommandParam.COMFORT: OverkizCommand.SET_COMFORT_TEMPERATURE,
    OverkizCommandParam.ECO: OverkizCommand.SET_ECO_TEMPERATURE,
    OverkizCommandParam.SECURED: OverkizCommand.SET_SECURED_POSITION_TEMPERATURE,
}


class SomfyHeatingTemperatureInterface(OverkizEntity, ClimateEntity):
    """Representation of Somfy Heating Temperature Interface."""

    _attr_temperature_unit = TEMP_CELSIUS
    _attr_hvac_modes = [*HVAC_MODES_TO_OVERKIZ]
    _attr_preset_modes = [*PRESET_MODES_TO_OVERKIZ]
    _attr_supported_features = SUPPORT_PRESET_MODE

    def __init__(self, device_url: str, coordinator: OverkizDataUpdateCoordinator):
        """Init method."""
        super().__init__(device_url, coordinator)
        self.temperature_device = self.executor.linked_device(2)

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        if (
            self.executor.select_state(OverkizState.CORE_ON_OFF)
            == OverkizCommandParam.OFF
        ):
            return HVAC_MODE_OFF

        if (
            OverkizState.OVP_HEATING_TEMPERATURE_INTERFACE_ACTIVE_MODE
            in self.device.states
        ):

            return OVERKIZ_TO_HVAC_MODES[
                self.executor.select_state(
                    OverkizState.OVP_HEATING_TEMPERATURE_INTERFACE_ACTIVE_MODE
                )
            ]

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        await self.executor.async_execute_command(
            OverkizCommand.SET_ACTIVE_MODE, HVAC_MODES_TO_OVERKIZ[hvac_mode]
        )

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp."""
        return OVERKIZ_TO_PRESET_MODES[
            self.executor.select_state(
                OverkizState.OVP_HEATING_TEMPERATURE_INTERFACE_SETPOINT_MODE
            )
        ]

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        await self.executor.async_execute_command(
            OverkizCommand.SET_MANU_AND_SET_POINT_MODES,
            PRESET_MODES_TO_OVERKIZ[preset_mode],
        )

    @property
    def hvac_action(self) -> str:
        """Return the current running hvac operation if supported."""
        current_operation = self.executor.select_state(
            OverkizState.OVP_HEATING_TEMPERATURE_INTERFACE_OPERATING_MODE
        )

        if current_operation in OVERKIZ_TO_HVAC_ACTION:
            return OVERKIZ_TO_HVAC_ACTION[current_operation]

    @property
    def target_temperature(self) -> Optional[float]:
        """Return the temperature."""
        if self.preset_mode not in PRESET_MODES_TO_OVERKIZ:
            return None

        mode = PRESET_MODES_TO_OVERKIZ[self.preset_mode]
        if mode not in MAP_PRESET_TEMPERATURES:
            return None

        return self.executor.select_state(MAP_PRESET_TEMPERATURES[mode])

    @property
    def current_temperature(self) -> Optional[float]:
        """Return the current temperature."""
        return self.temperature_device.states.get(OverkizState.CORE_TEMPERATURE).value

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new temperature."""

        mode = self.executor.select_state(
            OverkizState.OVP_HEATING_TEMPERATURE_INTERFACE_SETPOINT_MODE
        )
        temperature = kwargs.get(ATTR_TEMPERATURE)

        if mode in MODE_COMMAND_MAPPING:
            return await self.executor.async_execute_command(
                MODE_COMMAND_MAPPING[mode], temperature
            )
        else:
            _LOGGER.error("Unkown mode: %s", mode)
        return None
