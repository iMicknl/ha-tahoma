"""Support for Overkiz number devices."""
from homeassistant.components.cover import DOMAIN as COVER
from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.tahoma.coordinator import OverkizDataUpdateCoordinator

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

    _attr_icon = "mdi:content-save-cog"

    def __init__(
        self,
        device_url: str,
        coordinator: OverkizDataUpdateCoordinator,
    ):
        """Initialize the device."""
        super().__init__(device_url, coordinator)
        self._attr_name = f"{super().name} My Position"

    @property
    def value(self) -> float:
        """Return the current My position."""
        return self.device.states.get(CORE_MEMORIZED_POSITION).value

    async def async_set_value(self, value: float) -> None:
        """Update the My position value."""
        await self.executor.async_execute_command(COMMAND_SET_MEMORIZED_POSITION, value)
