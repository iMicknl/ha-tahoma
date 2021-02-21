"""Support for HitachiAirToWaterHeatingZone."""
import logging
from typing import Any, Dict, List, Optional

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    PRESET_COMFORT,
    PRESET_ECO,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS

from ..tahoma_entity import TahomaEntity

_LOGGER = logging.getLogger(__name__)

COMMAND_SET_AUTO_MANU_MODE = "setAutoManuMode"
COMMAND_SET_TARGET_MODE = "setTargetMode"
COMMAND_SET_THERMOSTAT_SETTING_CONTROL_ZONE_1 = "setThermostatSettingControlZone1"

MODBUS_YUTAKI_TARGET_MODE_STATE = "modbus:YutakiTargetModeState"
MODBUS_ROOM_AMBIENT_TEMPERATURE_STATUS_ZONE_1_STATE = (
    "modbus:RoomAmbientTemperatureStatusZone1State"
)
MODBUS_THERMOSTAT_SETTING_STATUS_ZONE_1_STATE = (
    "modbus:ThermostatSettingStatusZone1State"
)
MODBUS_AUTO_MANU_MODE_ZONE_1_STATE = "modbus:AutoManuModeZone1State"
MODBUS_THERMOSTAT_SETTING_CONTROL_ZONE_1_STATE = (
    "modbus:ThermostatSettingControlZone1State"
)

HVAC_STATE_MANU = "manu"
HVAC_STATE_AUTO = "auto"

PRESET_STATE_ECO = "eco"
PRESET_STATE_COMFORT = "comfort"

TAHOMA_TO_HVAC_MODE = {
    HVAC_STATE_MANU: HVAC_MODE_HEAT,
    HVAC_STATE_AUTO: HVAC_MODE_AUTO,
}

HVAC_MODE_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_HVAC_MODE.items()}

TAHOMA_TO_PRESET_MODE = {
    PRESET_STATE_COMFORT: PRESET_COMFORT,
    PRESET_STATE_ECO: PRESET_ECO,
}

PRESET_MODE_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_PRESET_MODE.items()}


class HitachiAirToWaterHeatingZone(TahomaEntity, ClimateEntity):
    """Representation of HitachiAirToWaterHeatingZone."""

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return the device state attributes."""
        device_info = super().device_info or {}
        device_info["manufacturer"] = "Hitachi"

        return device_info

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
        return TAHOMA_TO_HVAC_MODE[
            self.select_state(MODBUS_AUTO_MANU_MODE_ZONE_1_STATE)
        ]

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return [*HVAC_MODE_TO_TAHOMA]

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        await self.async_execute_command(
            COMMAND_SET_AUTO_MANU_MODE, HVAC_MODE_TO_TAHOMA[hvac_mode]
        )

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes."""
        return [*PRESET_MODE_TO_TAHOMA]

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp."""
        return TAHOMA_TO_PRESET_MODE[self.select_state(MODBUS_YUTAKI_TARGET_MODE_STATE)]

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        await self.async_execute_command(
            COMMAND_SET_TARGET_MODE, PRESET_MODE_TO_TAHOMA[preset_mode]
        )

    @property
    def current_temperature(self) -> Optional[float]:
        """Return the current temperature."""
        return self.select_state(MODBUS_ROOM_AMBIENT_TEMPERATURE_STATUS_ZONE_1_STATE)

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return 5.0

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return 35.0

    @property
    def target_temperature_step(self) -> Optional[float]:
        """Return the supported step of target temperature."""
        return 1.0

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self.select_state(MODBUS_THERMOSTAT_SETTING_CONTROL_ZONE_1_STATE)

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)

        await self.async_execute_command(
            COMMAND_SET_THERMOSTAT_SETTING_CONTROL_ZONE_1, int(temperature)
        )
