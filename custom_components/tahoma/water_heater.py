"""Support for Overkiz water heater devices."""
from __future__ import annotations

from homeassistant.components.water_heater import WaterHeaterEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyoverkiz.enums import UIWidget

from . import HomeAssistantOverkizData
from .const import DOMAIN
from .water_heater_devices.domestic_hot_water_production import (
    DomesticHotWaterProduction,
)
from .water_heater_devices.hitachi_dhw import HitachiDHW

TYPE = {
    UIWidget.DOMESTIC_HOT_WATER_PRODUCTION: DomesticHotWaterProduction,
    UIWidget.HITACHI_DHW: HitachiDHW,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Overkiz water heater from a config entry."""
    data: HomeAssistantOverkizData = hass.data[DOMAIN][entry.entry_id]

    entities: list[WaterHeaterEntity] = [
        TYPE[device.widget](device.device_url, data.coordinator)
        for device in data.platforms[Platform.WATER_HEATER]
        if device.widget in TYPE
    ]

    async_add_entities(entities)
