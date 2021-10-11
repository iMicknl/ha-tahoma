"""Support for Overkiz number devices."""
from homeassistant.components.cover import DOMAIN as COVER
from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import OverkizEntity

CORE_MEMORIZED_POSITION = "core:Memorized1PositionState"
COMMAND_SET_MEMORIZED_POSITION = "setMemorized1Position"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Overkiz number from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities = [
        MyPositionNumber(device.deviceurl, coordinator)
        for device in data["platforms"][COVER]
        if CORE_MEMORIZED_POSITION in device.states
    ]

    async_add_entities(entities)


class MyPositionNumber(OverkizEntity, NumberEntity):
    """Representation of a My Position Number."""

    _attr_name = "My Position"
    _attr_icon = "mdi:content-save-cog"
    _attr_min_value: 0
    _attr_max_value: 100

    @property
    def value(self) -> float:
        """Return the current My position."""
        return self.device.states.get(CORE_MEMORIZED_POSITION).value

    async def async_set_value(self, value: float) -> None:
        """Update the My position value."""
        await self.executor.async_execute_command(COMMAND_SET_MEMORIZED_POSITION, value)
