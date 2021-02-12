"""Support for HitachiDHW."""
from homeassistant.components.climate.const import SUPPORT_TARGET_TEMPERATURE
from homeassistant.components.water_heater import (
    STATE_HIGH_DEMAND,
    SUPPORT_OPERATION_MODE,
    WaterHeaterEntity,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS

from ..tahoma_device import TahomaDevice

MODBUS_DHW_MODE_STATE = "modbus:DHWModeState"

STATE_MANUAL = "manual"
STATE_AUTO = "auto"
STATE_ABSENCE = "absence"
STATE_RELAUNCH = "relaunch"

COMMAND_SET_TARGET_TEMPERATURE = "setTargetTemperature"
COMMAND_SET_DHW_MODE = "setDHWMode"
COMMAND_SET_CURRENT_OPERATING_MODE = "setCurrentOperatingMode"

MODE_STANDARD = "standard"
MODE_HIGH_DEMAND = "high demand"

TAHOMA_TO_OPERATION_MODE = {
    MODE_STANDARD: "standard",
    MODE_HIGH_DEMAND: STATE_HIGH_DEMAND,
}

OPERATION_MODE_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_OPERATION_MODE.items()}


class HitachiDHW(TahomaDevice, WaterHeaterEntity):
    """Representation of a HitachiDHW Water Heater."""

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_OPERATION_MODE | SUPPORT_TARGET_TEMPERATURE

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return 30.0

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return 70.0

    @property
    def current_operation(self):
        """Return current operation ie. eco, electric, performance, ..."""
        return TAHOMA_TO_OPERATION_MODE[self.select_state(MODBUS_DHW_MODE_STATE)]

    @property
    def operation_list(self):
        """Return the list of available operation modes."""
        return [*OPERATION_MODE_TO_TAHOMA]

    async def async_set_operation_mode(self, operation_mode):
        """Set new target operation mode."""
        await self.async_execute_command(
            COMMAND_SET_DHW_MODE, OPERATION_MODE_TO_TAHOMA[operation_mode]
        )

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self.select_state("core:DHWTemperatureState")

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self.select_state("modbus:StatusDHWSettingTemperatureState")

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        target_temperature = kwargs.get(ATTR_TEMPERATURE)
        await self.async_execute_command(
            "setControlDHWSettingTemperature", target_temperature
        )
