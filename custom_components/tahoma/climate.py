"""Support for TaHoma climate devices."""

from homeassistant.components.climate import DOMAIN as CLIMATE

from .climate_devices.atlantic_electrical_heater import AtlanticElectricalHeater
from .climate_devices.atlantic_pass_apcdhw import AtlanticPassAPCDHW
from .climate_devices.dimmer_exterior_heating import DimmerExteriorHeating
from .climate_devices.hitachi_air_to_water_heating_zone import (
    HitachiAirToWaterHeatingZone,
)
from .climate_devices.somfy_thermostat import SomfyThermostat
from .climate_devices.stateless_exterior_heating import StatelessExteriorHeating
from .const import DOMAIN

TYPE = {
    "AtlanticElectricalHeater": AtlanticElectricalHeater,
    "HitachiAirToWaterHeatingZone": HitachiAirToWaterHeatingZone,
    "SomfyThermostat": SomfyThermostat,
    "DimmerExteriorHeating": DimmerExteriorHeating,
    "StatelessExteriorHeating": StatelessExteriorHeating,
    "AtlanticPassAPCDHW": AtlanticPassAPCDHW,
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
