"""Support for AtlanticPassAPCDHWComponement."""
from typing import List, Optional
import logging
_LOGGER = logging.getLogger(__name__)

from homeassistant.const import (
   ATTR_TEMPERATURE,
   TEMP_CELSIUS
)
from homeassistant.components.climate import (
   HVAC_MODE_OFF,
   HVAC_MODE_HEAT,
   SUPPORT_PRESET_MODE,
   SUPPORT_TARGET_TEMPERATURE,
   ClimateEntity,
)
from homeassistant.components.climate.const import (
   PRESET_COMFORT,
   PRESET_ECO,
   PRESET_NONE,
)

from ..tahoma_device import TahomaDevice
from ..coordinator import TahomaDataUpdateCoordinator

"""
ON / OFF switch
{
	"values": ["off", "on"],
	"type": "DiscreteState",
	"qualifiedName": "core:DHWOnOffState"
}
{
	"commandName": "setDHWOnOffState",
	"nparams": 1
}
"""
CORE_DWH_ON_OFF_STATE = "core:DHWOnOffState"
COMMAND_SET_DWH_ON_OFF_STATE = "setDHWOnOffState"

DWH_OFF_STATE = "off"
DHW_ON_STATE = "on"

MAP_HVAC_MODES = {
   DHW_ON_STATE: HVAC_MODE_HEAT,
   DWH_OFF_STATE: HVAC_MODE_OFF,
   
}
MAP_REVERSE_HVAC_MODES = dict(map(reversed, MAP_HVAC_MODES.items()))

"""
Preset selection
{
	"values": ["comfort", "eco", "externalScheduling", "internalScheduling", "manu", "peakAndOffPeakScheduling", "peakAndOffPeakTimes", "stop"],
	"type": "DiscreteState",
	"qualifiedName": "io:PassAPCDHWModeState"
}
{
	"commandName": "setPassAPCDHWMode",
	"nparams": 1
}
"""
PASS_APCDHW_MODE_COMFORT="comfort"
PASS_APCDHW_MODE_ECO="eco"
#PASS_APCDWH_MODE_EXTERNAL_SCHEDULING="externalScheduling"
PASS_APCDWH_MODE_INTERNAL_SCHEDULING="internalScheduling"
#PASS_APCDHW_MODE_MANU="manu"
#PASS_APCDWH_MODE_PEAK_SCHEDULING="peakAndOffPeakScheduling"
#PASS_APCDWH_MODE_PEAK_TIMES="peakAndOffPeakTimes"
PASS_APCDHW_MODE_STOP="stop"
IO_PASS_APCDWH_MODE_STATE = "io:PassAPCDHWModeState"
COMMAND_SET_PASS_APCDHW_MODE = "setPassAPCDHWMode"

MAP_PRESET_MODES = {
   # param 57 (ECS mode) : 0 (off) - 2 (Eco) - 3 (Comfort) - 4 (PROG)
   PASS_APCDHW_MODE_COMFORT: PRESET_COMFORT, # 3
   PASS_APCDHW_MODE_ECO: PRESET_ECO, # 2
   # PASS_APCDWH_MODE_EXTERNAL_SCHEDULING: PASS_APCDWH_MODE_EXTERNAL_SCHEDULING,
   PASS_APCDWH_MODE_INTERNAL_SCHEDULING: PASS_APCDWH_MODE_INTERNAL_SCHEDULING, # 4
   # PASS_APCDHW_MODE_MANU: PASS_APCDHW_MODE_MANU,
   # PASS_APCDWH_MODE_PEAK_SCHEDULING: PASS_APCDWH_MODE_PEAK_SCHEDULING,
   # PASS_APCDWH_MODE_PEAK_TIMES: PASS_APCDWH_MODE_PEAK_TIMES,
   PASS_APCDHW_MODE_STOP: PASS_APCDHW_MODE_STOP # 0
}
MAP_REVERSE_PRESET_MODES = dict(map(reversed, MAP_PRESET_MODES.items()))

"""
Eco temperature
{
	"commandName": "refreshEcoTargetDHWTemperature",
	"nparams": 0
}
{
	"commandName": "setEcoTargetDHWTemperature",
	"nparams": 1
}
{
	"type": "ContinuousState",
	"qualifiedName": "core:EcoTargetDHWTemperatureState"
}
"""
COMMAND_REFRESH_ECO_TARGET_DWH_TEMPERATURE="refreshEcoTargetDHWTemperature"
COMMAND_SET_ECO_TARGET_DWH_TEMPERATURE="setEcoTargetDHWTemperature"
CORE_ECO_TARGET_DWH_TEMPERATURE_STATE="core:EcoTargetDHWTemperatureState"

"""
Target temperature
{
		"commandName": "refreshTargetDHWTemperature",
		"nparams": 0
},
{
	"type": "ContinuousState",
	"qualifiedName": "core:TargetDHWTemperatureState"
}
"""
COMMAND_REFRESH_TARGET_DWH_TEMPERATURE="refreshTargetDHWTemperature"
CORE_TARGET_DWH_TEMPERATURE_STATE="core:TargetDHWTemperatureState"

"""
Comfort temperature
{
	"commandName": "refreshComfortTargetDHWTemperature",
	"nparams": 0
}
{
	"commandName": "setComfortTargetDHWTemperature",
	"nparams": 1
}
{
	"type": "ContinuousState",
	"qualifiedName": "core:ComfortTargetDHWTemperatureState"
}
"""
COMMAND_SET_COMFORT_TARGET_DWH_TEMPERATURE="setComfortTargetDHWTemperature"
COMMAND_REFRESH_COMFORT_TARGET_DWH_TEMPERATURE="refreshComfortTargetDHWTemperature"
CORE_COMFORT_TARGET_DWH_TEMPERATURE_STATE="core:ComfortTargetDHWTemperatureState"

"""
Commands not tested/implemented :
{
   "commandName": "refreshDHWDerogationAvailability",
   "nparams": 0
}, {
   "commandName": "refreshDHWOnOffState",
   "nparams": 0
}, {
   "commandName": "setBoostOnOffState",
   "nparams": 1
}, {
   "commandName": "refreshDHWConfiguration",
   "nparams": 0
}, {
   "commandName": "refreshPassAPCDHWProfile",
   "nparams": 0
}

States not tests / implemented :
{
   "values": ["off", "on"],
   "type": "DiscreteState",
   "qualifiedName": "core:BoostOnOffState"
}, {
   "values": ["available", "unavailable"],
   "type": "DiscreteState",
   "qualifiedName": "core:DHWDerogationAvailabilityState"
}, {
   "values": ["available", "unavailable"],
   "type": "DiscreteState",
   "qualifiedName": "core:StatusState"
}, {
   "values": ["cumulated", "snapshot"],
   "type": "DiscreteState",
   "qualifiedName": "io:PassAPCDHWConfigurationState"
}, {
   "values": ["absence", "comfort", "derogation", "eco", "externalSetpoint", "frostprotection", "manu", "stop"],
   "type": "DiscreteState",
   "qualifiedName": "io:PassAPCDHWProfileState"
}
"""
CORE_BOOST_ON_OFF_STATE = "core:BoostOnOffState"
CORE_DHW_DEROGATION_AVAILABILITY_STATE = "core:DHWDerogationAvailabilityState"
CORE_STATUS_STATE = "core:StatusState"
IO_PASS_APCDHW_CONFIGURATION_STATE = "io:PassAPCDHWConfigurationState"
IO_PASS_APCDHW_PROFILE_STATE = "io:PassAPCDHWProfileState"


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
      """Return minimum percentage."""
      # FIXME: only for naia micro ?
      return 30

   @property
   def max_temp(self) -> float:
      """Return maximum percentage."""
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
      # update target temperature
      await self.async_execute_command(
         "refreshTargetDHWTemperature"
      )

   async def async_set_temperature(self, **kwargs) -> None:
      """Set new temperature for current preset"""
      temperature = kwargs.get(ATTR_TEMPERATURE)
      # it's only possible to define a eco or comfort temperature
      if (self.preset_mode == PRESET_ECO):
         await self.async_execute_command(
            COMMAND_SET_ECO_TARGET_DWH_TEMPERATURE, temperature
         )
      elif (self.preset_mode == PRESET_COMFORT):
         await self.async_execute_command(
            COMMAND_SET_COMFORT_TARGET_DWH_TEMPERATURE, temperature
         )

      # Refresh target temperature immediately
      await self.async_execute_command(
         "refreshTargetDHWTemperature"
      )

   @property
   def target_temperature(self):
      """ Return the temperature corresponding to the PRESET """
      if (self.preset_mode == PRESET_ECO):
         return self.select_state(CORE_ECO_TARGET_DWH_TEMPERATURE_STATE)
      elif (self.preset_mode == PRESET_COMFORT):
         return self.select_state(CORE_COMFORT_TARGET_DWH_TEMPERATURE_STATE)
      else:
         return  self.select_state(CORE_TARGET_DWH_TEMPERATURE_STATE)

   @property
   def current_temperature(self):
      self.debug()
      # current temperature is the same as target temperature
      return self.target_temperature

   def debug(self):
      """FIXME: Only for debugging purpose"""
      for value in [
         IO_PASS_APCDWH_MODE_STATE, CORE_ECO_TARGET_DWH_TEMPERATURE_STATE, 
         CORE_COMFORT_TARGET_DWH_TEMPERATURE_STATE, CORE_DWH_ON_OFF_STATE, CORE_TARGET_DWH_TEMPERATURE_STATE,
         CORE_BOOST_ON_OFF_STATE, CORE_DHW_DEROGATION_AVAILABILITY_STATE, CORE_STATUS_STATE, IO_PASS_APCDHW_CONFIGURATION_STATE, IO_PASS_APCDHW_PROFILE_STATE
         ]:
         _LOGGER.info("%s: %s", value, self.select_state(value))