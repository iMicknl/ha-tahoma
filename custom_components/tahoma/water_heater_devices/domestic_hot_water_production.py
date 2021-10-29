"""Support for DomesticHotWaterProduction."""
from homeassistant.components.climate.const import SUPPORT_TARGET_TEMPERATURE
from homeassistant.components.water_heater import (
    SUPPORT_AWAY_MODE,
    SUPPORT_OPERATION_MODE,
    WaterHeaterEntity,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS

from ..const import OverkizCommand, OverkizCommandState, OverkizState
from ..entity import OverkizEntity

MAP_OPERATION_MODES = {
    OverkizCommandState.MANUAL_ECO_ACTIVE: OverkizCommandState.ECO,
    OverkizCommandState.MANUAL_ECO_INACTIVE: OverkizCommandState.MANUAL,
    OverkizCommandState.AUTO: OverkizCommandState.AUTO,
}

MAP_REVERSE_OPERATION_MODES = {v: k for k, v in MAP_OPERATION_MODES.items()}


class DomesticHotWaterProduction(OverkizEntity, WaterHeaterEntity):
    """Representation of a DomesticHotWaterProduction Water Heater."""

    _attr_operation_list = [*MAP_REVERSE_OPERATION_MODES]
    _attr_supported_features = (
        SUPPORT_OPERATION_MODE | SUPPORT_AWAY_MODE | SUPPORT_TARGET_TEMPERATURE
    )
    _attr_temperature_unit = TEMP_CELSIUS

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return self.executor.select_state(
            OverkizState.CORE_MINIMAL_TEMPERATURE_MANUAL_MODE
        )

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return self.executor.select_state(
            OverkizState.CORE_MAXIMAL_TEMPERATURE_MANUAL_MODE
        )

    @property
    def current_operation(self):
        """Return current operation ie. eco, electric, performance, ..."""
        return MAP_OPERATION_MODES[self.executor.select_state(OverkizState.IO_DHW_MODE)]

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self.executor.select_state(OverkizState.IO_MIDDLE_WATER_TEMPERATURE)

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self.executor.select_state(OverkizState.CORE_TARGET_TEMPERATURE)

    @property
    def target_temperature_high(self):
        """Return the highbound target temperature we try to reach."""
        return self.executor.select_state(
            OverkizState.CORE_MAXIMAL_TEMPERATURE_MANUAL_MODE
        )

    @property
    def target_temperature_low(self):
        """Return the lowbound target temperature we try to reach."""
        return self.executor.select_state(
            OverkizState.CORE_MINIMAL_TEMPERATURE_MANUAL_MODE
        )

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        target_temperature = kwargs.get(ATTR_TEMPERATURE)
        await self.executor.async_execute_command(
            OverkizCommand.SET_TARGET_TEMPERATURE, target_temperature
        )

    async def async_set_operation_mode(self, operation_mode):
        """Set new target operation mode."""
        await self.executor.async_execute_command(
            OverkizCommand.SET_DHW_MODE, MAP_REVERSE_OPERATION_MODES[operation_mode]
        )

    @property
    def is_away_mode_on(self):
        """Return true if away mode is on."""
        return (
            self.executor.select_state(OverkizState.CORE_OPERATING_MODE).get(
                OverkizCommandState.ABSENCE
            )
            == OverkizCommandState.ON
        )

    async def async_turn_away_mode_on(self):
        """Turn away mode on."""
        await self.executor.async_execute_command(
            OverkizCommand.SET_CURRENT_OPERATING_MODE,
            {
                OverkizCommandState.RELAUNCH: OverkizCommandState.OFF,
                OverkizCommandState.ABSENCE: OverkizCommandState.ON,
            },
        )

    async def async_turn_away_mode_off(self):
        """Turn away mode off."""
        await self.executor.async_execute_command(
            OverkizCommand.SET_CURRENT_OPERATING_MODE,
            {
                OverkizCommandState.RELAUNCH: OverkizCommandState.OFF,
                OverkizCommandState.ABSENCE: OverkizCommandState.OFF,
            },
        )
