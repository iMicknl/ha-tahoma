"""Support for DomesticHotWaterProduction."""

from homeassistant.components.water_heater import (
    STATE_ECO,
    SUPPORT_AWAY_MODE,
    SUPPORT_OPERATION_MODE,
)
from homeassistant.const import TEMP_CELSIUS
from pyoverkiz.enums import OverkizCommand, OverkizCommandParam, OverkizState

from .domestic_hot_water_production import DomesticHotWaterProduction

STATE_MANUAL = "manual"
STATE_AUTO = "auto"

OVERKIZ_TO_OPERATION_MODE = {
    OverkizCommandParam.MANUAL_ECO_ACTIVE: STATE_ECO,
    OverkizCommandParam.MANUAL_ECO_INACTIVE: STATE_MANUAL,
    OverkizCommandParam.AUTO_MODE: STATE_AUTO,
}

OPERATION_MODE_TO_OVERKIZ = {v: k for k, v in OVERKIZ_TO_OPERATION_MODE.items()}


class DomesticHotWaterProductionSauterGUELMA(DomesticHotWaterProduction):
    """Representation of a DomesticHotWaterProductionSauterGUELMA Water Heater."""

    _attr_operation_list = [*OPERATION_MODE_TO_OVERKIZ]

    _attr_supported_features = SUPPORT_OPERATION_MODE | SUPPORT_AWAY_MODE
    _attr_temperature_unit = TEMP_CELSIUS

    def __init__(self, device_url, coordinator):
        """Initialize DomesticHotWaterProductionSauterGUELMA."""
        super().__init__(device_url, coordinator)

    @property
    def current_operation(self):
        """Return current operation ie. eco, electric, performance, ..."""
        return OVERKIZ_TO_OPERATION_MODE[
            self.executor.select_state(OverkizState.MODBUSLINK_DHW_MODE)
        ]

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self.executor.select_state(
            OverkizState.MODBUSLINK_MIDDLE_WATER_TEMPERATURE
        )

    @property
    def is_away_mode_on(self):
        """Return true if away mode is on."""
        return (
            self.executor.select_state(OverkizState.MODBUSLINK_DHW_ABSENCE_MODE)
            == OverkizCommandParam.ON
        )

    async def async_turn_away_mode_on(self):
        """Turn away mode on."""
        await self.executor.async_execute_command(
            OverkizCommand.SET_ABSENCE_MODE, OverkizCommandParam.ON
        )

    async def async_turn_away_mode_off(self):
        """Turn away mode off."""
        await self.executor.async_execute_command(
            OverkizCommand.SET_ABSENCE_MODE, OverkizCommandParam.OFF
        )
