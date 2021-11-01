"""Support for Overkiz select devices."""
from homeassistant.components.cover import DOMAIN as COVER
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.tahoma.coordinator import OverkizDataUpdateCoordinator

from .const import DOMAIN, OverkizCommand, OverkizCommandParam, OverkizState
from .entity import OverkizEntity

SELECT_OPTION_TO_COMMAND = {
    OverkizCommandParam.CLOSED: OverkizCommand.CLOSE,
    OverkizCommandParam.OPEN: OverkizCommand.OPEN,
    OverkizCommandParam.PEDESTRIAN: OverkizCommand.SET_PEDESTRIAN_POSITION,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Overkiz select from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities = [
        PedestrianGateSelect(device.device_url, coordinator)
        for device in data["platforms"][COVER]
        if OverkizState.CORE_OPEN_CLOSED_PEDESTRIAN in device.states
    ]

    async_add_entities(entities)


class PedestrianGateSelect(OverkizEntity, SelectEntity):
    """Representation of the various state for a pedestrian gate."""

    _attr_icon = "mdi:content-save-cog"

    def __init__(
        self,
        device_url: str,
        coordinator: OverkizDataUpdateCoordinator,
    ):
        """Initialize the device."""
        super().__init__(device_url, coordinator)
        self._attr_name = f"{super().name} Position"

    @property
    def current_option(self):
        """Return the selected entity option to represent the entity state."""
        return self.device.states.get(OverkizState.CORE_OPEN_CLOSED_PEDESTRIAN).value

    @property
    def options(self):
        """Return a set of selectable options."""
        return [*SELECT_OPTION_TO_COMMAND]

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option in SELECT_OPTION_TO_COMMAND:
            await self.executor.async_execute_command(SELECT_OPTION_TO_COMMAND[option])
