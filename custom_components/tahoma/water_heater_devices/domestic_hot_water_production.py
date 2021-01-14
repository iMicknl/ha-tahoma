"""Support for DomesticHotWaterProduction."""
from homeassistant.components.climate.const import SUPPORT_TARGET_TEMPERATURE
from homeassistant.components.water_heater import (
    STATE_ECO,
    SUPPORT_AWAY_MODE,
    SUPPORT_OPERATION_MODE,
    WaterHeaterEntity,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS

from ..tahoma_device import TahomaDevice

CORE_MAXIMAL_TEMPERATURE_MANUAL_MODE_STATE = "core:MaximalTemperatureManualModeState"
CORE_MINIMAL_TEMPERATURE_MANUAL_MODE_STATE = "core:MinimalTemperatureManualModeState"

IO_DHW_MODE_STATE = "io:DHWModeState"

STATE_MANUEL = "manuel"
STATE_AUTO = "auto"


# Somfy to Hass
MAP_OPERATION_MODES = {
    "manualEcoActive": STATE_ECO,
    "manualEcoInactive": STATE_MANUEL,
    "autoMode": STATE_AUTO,
}

MAP_REVERSE_OPERATION_MODES = {v: k for k, v in MAP_OPERATION_MODES.items()}


# https://github.com/Cyr-ius/hass-cozytouch/issues/12
class DomesticHotWaterProduction(TahomaDevice, WaterHeaterEntity):
    """Representation of a DomesticHotWaterProduction Water Heater."""

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return self.select_state(CORE_MINIMAL_TEMPERATURE_MANUAL_MODE_STATE)

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return self.select_state(CORE_MAXIMAL_TEMPERATURE_MANUAL_MODE_STATE)

    @property
    def current_operation(self):
        """Return current operation ie. eco, electric, performance, ..."""
        return MAP_OPERATION_MODES[self.select_state(IO_DHW_MODE_STATE)]

    @property
    def operation_list(self):
        """Return the list of available operation modes."""
        return [*MAP_REVERSE_OPERATION_MODES]

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self.select_state("io:MiddleWaterTemperatureState")

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self.select_state("core:TargetTemperatureState")  # TODO Validate

    @property
    def target_temperature_high(self):
        """Return the highbound target temperature we try to reach."""
        return self.select_state(CORE_MAXIMAL_TEMPERATURE_MANUAL_MODE_STATE)

    @property
    def target_temperature_low(self):
        """Return the lowbound target temperature we try to reach."""
        return self.select_state(CORE_MINIMAL_TEMPERATURE_MANUAL_MODE_STATE)

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        target_temperature = kwargs.get(ATTR_TEMPERATURE)
        await self.select_command("setTargetTemperature", target_temperature)

    async def async_set_operation_mode(self, operation_mode):
        """Set new target operation mode."""
        # TODO Understand if we need to set DHWMode or CurrentOperatingMode
        # HomeKit does it different https://github.com/dubocr/homebridge-tahoma/blob/0fca75b3867330d50bb79d6d2c05c5657135b6ed/services/Thermostat.js#L371-L380
        await self.async_execute_command(
            "setDHWMode", MAP_REVERSE_OPERATION_MODES[operation_mode]
        )

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_OPERATION_MODE | SUPPORT_AWAY_MODE | SUPPORT_TARGET_TEMPERATURE
