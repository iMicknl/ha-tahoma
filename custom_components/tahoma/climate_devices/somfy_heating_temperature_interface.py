"""Support for Somfy Heating Temperature Interface."""
import logging
from typing import Optional

from pyoverkiz.enums import OverkizCommand, OverkizCommandParam, OverkizState

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
    """Representation of Somfy Heating Temperature Interface.

    The thermostat has 3 ways of working:
      - Auto: Switch to eco/comfort temperature on a schedule (day/hour of the day)
      - Manual comfort: The thermostat use the temperature of the comfort setting (19°C degree by default)
      - Manual eco: The thermostat use the temperature of the eco setting (17°C by default)
      - Freeze protection: The thermostat use the temperature of the freeze protection (7°C by default)

    There's also the possibility to change the working mode, this can be used to change from a heated
    floor to a cooling floor in the summer.
    """

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
        """Return hvac operation i.e. heat, cool mode."""
        if (
            self.executor.select_state(OverkizState.CORE_ON_OFF)
            == OverkizCommandParam.OFF
        ):
            return HVAC_MODE_OFF

        state = self.executor.select_state(
            OverkizState.OVP_HEATING_TEMPERATURE_INTERFACE_ACTIVE_MODE
        )
        if mode := OVERKIZ_TO_HVAC_MODES.get(state):
            return mode

        if state is not None:
            # Unknown and potentially a new state, log to make it easier to report
            _LOGGER.warning(
                "Overkiz %s state unknown: %s",
                OverkizState.OVP_HEATING_TEMPERATURE_INTERFACE_ACTIVE_MODE,
                state,
            )
        return HVAC_MODE_OFF

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
    def hvac_action(self) -> Optional[str]:
        """Return the current running hvac operation if supported."""
        current_operation = self.executor.select_state(
            OverkizState.OVP_HEATING_TEMPERATURE_INTERFACE_OPERATING_MODE
        )

        if action := OVERKIZ_TO_HVAC_ACTION.get(current_operation):
            return action

        if current_operation is not None:
            # Unknown and potentially a new state, log to make it easier to report
            _LOGGER.error(
                "Overkiz %s state unknown: %s",
                OverkizState.OVP_HEATING_TEMPERATURE_INTERFACE_OPERATING_MODE,
                current_operation,
            )
        return None

    @property
    def target_temperature(self) -> Optional[float]:
        """Return the target temperature."""
        if self.preset_mode not in PRESET_MODES_TO_OVERKIZ:
            return None

        # Allow to get the current target temperature for the current preset
        # The preset can be switched manually or on a schedule (auto).
        # This allows to reflect the current target temperature automatically
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

        if mode not in MODE_COMMAND_MAPPING:
            _LOGGER.error("Unknown temperature mode: %s", mode)
            return None

        return await self.executor.async_execute_command(
            MODE_COMMAND_MAPPING[mode], temperature
        )
