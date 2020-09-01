"""Support for TaHoma climate devices."""
import logging
from pprint import pformat

from homeassistant.components.climate import DOMAIN as CLIMATE
from homeassistant.helpers import entity_platform

from .climate_devices.atlantic_electrical_heater import AtlanticElectricalHeater
from .climate_devices.dimmer_exterior_heating import DimmerExteriorHeating
from .climate_devices.somfy_thermostat import SomfyThermostat
from .climate_devices.stateless_exterior_heating import StatelessExteriorHeating
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

TYPE = {
    "AtlanticElectricalHeater": AtlanticElectricalHeater,
    "SomfyThermostat": SomfyThermostat,
    "DimmerExteriorHeating": DimmerExteriorHeating,
    "StatelessExteriorHeating": StatelessExteriorHeating,
}

SERVICE_MY = "climate_my"
SUPPORT_MY = pow(2, 20)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma climate from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data.get("coordinator")

    climate_devices = [device for device in data.get("entities").get(CLIMATE)]
    _LOGGER.debug(f"Climate devices found:\n{pformat(climate_devices)}")

    entities = [
        TYPE[device.widget](device.deviceurl, coordinator)
        for device in climate_devices
        if device.widget in TYPE
    ]
    async_add_entities(entities)
    _LOGGER.debug(f"Entities added:\n{pformat(entities)}")

    platform = entity_platform.current_platform.get()
    platform.async_register_entity_service(SERVICE_MY, {}, "async_my", [SUPPORT_MY])
