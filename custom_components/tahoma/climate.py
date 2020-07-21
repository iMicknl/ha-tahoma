"""Support for TaHoma climate devices."""

from .climate_aeh import AtlanticElectricalHeater
from .climate_st import SomfyThermostat
from .const import DOMAIN, TAHOMA_TYPES

AEH = "AtlanticElectricalHeater"
ST = "SomfyThermostat"
SUPPORTED_CLIMATE_DEVICES = [AEH, ST]


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma climate from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]
    controller = data.get("controller")

    climate_devices = [
        d for d in data.get("devices") if TAHOMA_TYPES[d.uiclass] == "climate"
    ]

    entities = []
    for device in climate_devices:
        if device.widget == AEH:
            entities.append(AtlanticElectricalHeater(device, controller))
        elif device.widget == ST:
            base_url = device.url.split("#", 1)[0]
            sensor = None
            entity_registry = await hass.helpers.entity_registry.async_get_registry()
            for k, v in entity_registry.entities.items():
                if v.unique_id == base_url + "#2":
                    sensor = k
                    break
            entities.append(SomfyThermostat(device, controller, sensor))
    async_add_entities(entities)
