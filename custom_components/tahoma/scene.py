"""Support for Overkiz scenes."""
from typing import Any

from homeassistant.components.scene import DOMAIN as SCENE, Scene
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyoverkiz.client import OverkizClient
from pyoverkiz.models import Scenario

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Overkiz scenes from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities = [
        OverkizScene(scene, coordinator.client) for scene in data["platforms"][SCENE]
    ]
    async_add_entities(entities)


class OverkizScene(Scene):
    """Representation of an Overkiz scene entity."""

    def __init__(self, scenario: Scenario, client: OverkizClient):
        """Initialize the scene."""
        self.scenario = scenario
        self.client = client
        self._attr_name = self.scenario.label
        self._attr_unique_id = self.scenario.oid

    async def async_activate(self, **_: Any) -> None:
        """Activate the scene."""
        await self.client.execute_scenario(self.scenario.oid)
