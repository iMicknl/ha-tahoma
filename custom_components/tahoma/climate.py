"""Support for TaHoma climate devices."""

from homeassistant.components.climate import DOMAIN as CLIMATE

from .climate_aeh import AtlanticElectricalHeater
from .climate_deh import DimmerExteriorHeating
from .climate_st import SomfyThermostat
from .const import DOMAIN

AEH = "AtlanticElectricalHeater"
ST = "SomfyThermostat"
DEH = "DimmerExteriorHeating"


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma climate from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]
    controller = data.get("controller")

    climate_devices = [device for device in data.get("entities").get(CLIMATE)]

    entities = []
    for device in climate_devices:
        if device.widget == AEH:
            entities.append(AtlanticElectricalHeater(device, controller))
        elif device.widget == ST:
            base_url = device.deviceurl.split("#", 1)[0]
            sensor = None
            entity_registry = await hass.helpers.entity_registry.async_get_registry()
            for k, v in entity_registry.entities.items():
                if v.unique_id == base_url + "#2":
                    sensor = k
                    break
            entities.append(SomfyThermostat(device, controller, sensor))
        elif device.widget == DEH:
            entities.append(DimmerExteriorHeating(device, controller))
    async_add_entities(entities)
