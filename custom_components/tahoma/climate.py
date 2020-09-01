"""Support for TaHoma climate devices."""

from homeassistant.components.climate import DOMAIN as CLIMATE

from .climate_devices.AtlanticElectricalHeater import AtlanticElectricalHeater
from .climate_devices.DimmerExteriorHeating import DimmerExteriorHeating
from .climate_devices.SomfyThermostat import SomfyThermostat
from .const import DOMAIN

TYPE = {
    "AtlanticElectricalHeater": AtlanticElectricalHeater,
    "SomfyThermostat": SomfyThermostat,
    "DimmerExteriorHeating": DimmerExteriorHeating,
}


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma climate from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data.get("coordinator")

    climate_devices = [device for device in data.get("entities").get(CLIMATE)]

    entities = [
        TYPE[device.widget](device.deviceurl, coordinator)
        for device in climate_devices
        if device.widget in TYPE
    ]
    async_add_entities(entities)
