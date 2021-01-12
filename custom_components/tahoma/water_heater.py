"""Support for TaHoma switches."""
import logging

from homeassistant.components.water_heater import (  # ATTR_TEMPERATURE,; STATE_ON,; STATE_OFF,; SUPPORT_AWAY_MODE,; SUPPORT_OPERATION_MODE,; SUPPORT_TARGET_TEMPERATURE,; SUPPORT_AWAY_MODE,; SUPPORT_OPERATION_MODE,; SUPPORT_TARGET_TEMPERATURE,
    DOMAIN as WATER_HEATER,
    STATE_ECO,
    WaterHeaterEntity,
)

from .const import DOMAIN
from .tahoma_device import TahomaDevice

# from typing import Optional


# from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS, TEMP_FAHRENHEIT


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities = [
        TahomaWaterHeater(device.deviceurl, coordinator)
        for device in data["entities"].get(WATER_HEATER)
    ]

    async_add_entities(entities)


# DomesticHotWaterProduction
class TahomaWaterHeater(TahomaDevice, WaterHeaterEntity):
    """Representation a TaHoma Water Heater."""

    MAP_HEATING_MODES = {
        "manualEcoActive": STATE_ECO,
        "manualEcoInactive": "manuel",
        "autoMode": "auto",
    }
    MAP_REVERSE_HEATING_MODES = {v: k for k, v in MAP_HEATING_MODES.items()}
