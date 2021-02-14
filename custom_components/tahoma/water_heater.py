"""Support for TaHoma water heater devices."""
from homeassistant.components.water_heater import DOMAIN as WATER_HEATER

from .const import DOMAIN
from .water_heater_devices.domestic_hot_water_production import (
    DomesticHotWaterProduction,
)

TYPE = {
    "DomesticHotWaterProduction": DomesticHotWaterProduction,
}


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma water heater from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    water_heater_devices = [device for device in data["platforms"].get(WATER_HEATER)]

    entities = [
        TYPE[device.widget](device.deviceurl, coordinator)
        for device in water_heater_devices
        if device.widget in TYPE
    ]
    async_add_entities(entities)
