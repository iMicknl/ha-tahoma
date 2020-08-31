"""Support for TaHoma climate devices."""
import logging

from homeassistant.components.climate import DOMAIN as CLIMATE
from homeassistant.helpers import entity_platform

from .climate_aeh import AtlanticElectricalHeater
from .climate_deh import DimmerExteriorHeating
from .climate_seh import StatelessExteriorHeating
from .climate_st import SomfyThermostat
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

TYPE = {
    "AtlanticElectricalHeater": AtlanticElectricalHeater,
    "SomfyThermostat": SomfyThermostat,
    "DimmerExteriorHeating": DimmerExteriorHeating,
    "StatelessExteriorHeating": StatelessExteriorHeating,
}

SERVICE_MY = "climate_my"
SUPPORT_MY = 512


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

    for device in climate_devices:
        if device.widget == "StatelessExteriorHeating":
            platform = entity_platform.current_platform.get()
            platform.async_register_entity_service(
                SERVICE_MY, {}, "async_my", [SUPPORT_MY]
            )
