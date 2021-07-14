"""Support for TaHoma climate devices."""
from homeassistant.components.climate import DOMAIN as CLIMATE

from .climate_devices.atlantic_electrical_heater import AtlanticElectricalHeater
from .climate_devices.atlantic_electrical_heater_with_adjustable_temperature_setpoint import (
    AtlanticElectricalHeaterWithAdjustableTemperatureSetpoint,
)
from .climate_devices.atlantic_electrical_towel_dryer import (
    AtlanticElectricalTowelDryer,
)
from .climate_devices.atlantic_pass_apc_heating_and_cooling_zone import (
    AtlanticPassAPCHeatingAndCoolingZone,
)
from .climate_devices.atlantic_pass_apc_zone_control import AtlanticPassAPCZoneControl
from .climate_devices.atlantic_pass_apcdhw import AtlanticPassAPCDHW
from .climate_devices.dimmer_exterior_heating import DimmerExteriorHeating
from .climate_devices.evo_home_controller import EvoHomeController
from .climate_devices.heating_set_point import HeatingSetPoint
from .climate_devices.hitachi_air_to_air_heat_pump import HitachiAirToAirHeatPump
from .climate_devices.hitachi_air_to_water_heating_zone import (
    HitachiAirToWaterHeatingZone,
)
from .climate_devices.somfy_thermostat import SomfyThermostat
from .climate_devices.stateless_exterior_heating import StatelessExteriorHeating
from .const import DOMAIN

TYPE = {
    "AtlanticElectricalTowelDryer": AtlanticElectricalTowelDryer,
    "AtlanticElectricalHeater": AtlanticElectricalHeater,
    "AtlanticElectricalHeaterWithAdjustableTemperatureSetpoint": AtlanticElectricalHeaterWithAdjustableTemperatureSetpoint,
    "AtlanticElectricalTowelDryer": AtlanticElectricalTowelDryer,
    "AtlanticPassAPCDHW": AtlanticPassAPCDHW,
    "AtlanticPassAPCHeatingAndCoolingZone": AtlanticPassAPCHeatingAndCoolingZone,
    "AtlanticPassAPCZoneControl": AtlanticPassAPCZoneControl,
    "DimmerExteriorHeating": DimmerExteriorHeating,
    "EvoHomeController": EvoHomeController,
    "HeatingSetPoint": HeatingSetPoint,
    "HitachiAirToAirHeatPump": HitachiAirToAirHeatPump,
    "HitachiAirToWaterHeatingZone": HitachiAirToWaterHeatingZone,
    "SomfyThermostat": SomfyThermostat,
    "StatelessExteriorHeating": StatelessExteriorHeating,
}

SERVICE_CLIMATE_MY_POSITION = "set_climate_my_position"


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma climate from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    climate_devices = [device for device in data["platforms"].get(CLIMATE)]

    entities = [
        TYPE[device.widget](device.deviceurl, coordinator)
        for device in climate_devices
        if device.widget in TYPE
    ]
    async_add_entities(entities)
