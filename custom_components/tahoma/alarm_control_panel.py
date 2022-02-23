"""Support for Overkiz Alarms."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HomeAssistantOverkizData
from .alarm_entities import WIDGET_TO_ALARM_ENTITY
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Overkiz alarm control panel from a config entry."""
    data: HomeAssistantOverkizData = hass.data[DOMAIN][entry.entry_id]

    entities = [
        WIDGET_TO_ALARM_ENTITY[device.widget](device.device_url, data.coordinator)
        for device in data.platforms[Platform.ALARM_CONTROL_PANEL]
        if device.widget in WIDGET_TO_ALARM_ENTITY
    ]

    async_add_entities(entities)
