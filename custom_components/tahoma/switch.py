"""Support for TaHoma switches."""
import logging

from homeassistant.components.switch import DEVICE_CLASS_SWITCH, SwitchEntity
from homeassistant.const import STATE_OFF, STATE_ON

from .const import DOMAIN, TAHOMA_TYPES
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma sensors from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]

    entities = []
    controller = data.get("controller")

    for device in data.get("devices"):
        if TAHOMA_TYPES[device.uiclass] == "switch":
            entities.append(TahomaSwitch(device, controller))

    async_add_entities(entities)


class TahomaSwitch(TahomaDevice, SwitchEntity):
    """Representation a TaHoma Switch."""

    def __init__(self, tahoma_device, controller):
        """Initialize the switch."""
        super().__init__(tahoma_device, controller)

        self._state = None

    def update(self):
        """Update method."""

        self.controller.get_states([self.tahoma_device])

        if "core:OnOffState" in self.tahoma_device.active_states:
            self.current_value = (
                self.tahoma_device.active_states.get("core:OnOffState") == "on"
            )

    @property
    def device_class(self):
        """Return the class of the device."""

        return DEVICE_CLASS_SWITCH

    @property
    def icon(self) -> Optional[str]:
        """Return the icon to use in the frontend, if any."""

        if self.tahoma_device.uiclass == "Siren":
            return "mdi:bell-ring"

        return None

    def turn_on(self, **kwargs):
        """Send the on command."""

        if "on" in self.tahoma_device.command_definitions:
            return self.apply_action("on")

        if "ringWithSingleSimpleSequence" in self.tahoma_device.command_definitions:
            return self.apply_action("ringWithSingleSimpleSequence")

        self.apply_action("on")

    def turn_off(self, **kwargs):
        """Send the off command."""

        if "off" in self.tahoma_device.command_definitions:
            return self.apply_action("off")

    def toggle(self, **kwargs):
        """Click the switch."""

        if "cycle" in self.tahoma_device.command_definitions:
            return self.apply_action("cycle")

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return bool(self._state == STATE_ON)
