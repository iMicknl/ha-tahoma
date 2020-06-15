"""Support for TaHoma scenes."""
import logging
from typing import Any

from homeassistant.components.scene import Scene

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma scenes from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]

    entities = []
    controller = data.get("controller")

    for scene in data.get("scenes"):
        entities.append(TahomaScene(scene, controller))

    async_add_entities(entities)


class TahomaScene(Scene):
    """Representation of a TaHoma scene entity."""

    def __init__(self, tahoma_scene, controller):
        """Initialize the scene."""
        self.tahoma_scene = tahoma_scene
        self.controller = controller
        self._name = self.tahoma_scene.name

    def activate(self, **kwargs: Any) -> None:
        """Activate the scene."""
        self.controller.launch_action_group(self.tahoma_scene.oid)

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self.tahoma_scene.oid

    @property
    def name(self):
        """Return the name of the scene."""
        return self._name

    @property
    def device_state_attributes(self):
        """Return the state attributes of the scene."""
        return {"tahoma_scene_oid": self.tahoma_scene.oid}
