"""Support for Overkiz water heater devices."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyoverkiz.enums import OverkizState, UIWidget

from .const import DOMAIN
from .water_heater_devices.domestic_hot_water_production import (
    DomesticHotWaterProduction,
)
from .water_heater_devices.domestic_hot_water_production_sauter_guelma import (
    DomesticHotWaterProductionSauterGUELMA,
)
from .water_heater_devices.hitachi_dhw import HitachiDHW

TYPE = {
    UIWidget.DOMESTIC_HOT_WATER_PRODUCTION: DomesticHotWaterProduction,
    UIWidget.HITACHI_DHW: HitachiDHW,
    UIWidget.DOMESTIC_HOT_WATER_PRODUCTION
    + "SauterGUELMA": DomesticHotWaterProductionSauterGUELMA
}

def device_type(device):
    device_full_name = (
        device.widget
        + device.states.get(OverkizState.CORE_MANUFACTURER_NAME).value
        + device.states.get(OverkizState.CORE_NAME).value
    )
    return device_full_name if device_full_name in TYPE else device.widget


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Overkiz water heater from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    water_heater_devices = [
        device for device in data["platforms"][Platform.WATER_HEATER]
    ]

    entities = [
        TYPE[device_type(device)](device.device_url, coordinator)
        for device in water_heater_devices
        if device.widget in TYPE
    ]
    async_add_entities(entities)
