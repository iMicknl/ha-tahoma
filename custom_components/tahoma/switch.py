"""Support for TaHoma switches."""
import logging
from typing import Optional

from homeassistant.components.switch import DEVICE_CLASS_SWITCH, SwitchEntity
from homeassistant.const import STATE_ON

from .const import COMMAND_OFF, COMMAND_ON, CORE_ON_OFF_STATE, DOMAIN, TAHOMA_TYPES
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

COMMAND_CYCLE = "cycle"
COMMAND_MEMORIZED_VOLUME = "memorizedVolume"
COMMAND_RING_WITH_SINGLE_SIMPLE_SEQUENCE = "ringWithSingleSimpleSequence"

DEVICE_CLASS_SIREN = "siren"


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    controller = data.get("controller")

    entities = [
        TahomaSwitch(device, controller)
        for device in data.get("devices")
        if TAHOMA_TYPES[device.uiclass] == "switch"
    ]

    async_add_entities(entities)


class TahomaSwitch(TahomaDevice, SwitchEntity):
    """Representation a TaHoma Switch."""

    def __init__(self, tahoma_device, controller):
        """Initialize the switch."""
        super().__init__(tahoma_device, controller)

        self._state = None

    def update(self):
        """Update method."""
        if self.should_wait():
            self.schedule_update_ha_state(True)
            return

        self.controller.get_states([self.tahoma_device])

        if CORE_ON_OFF_STATE in self.tahoma_device.active_states:
            self.current_value = (
                self.tahoma_device.active_states.get(CORE_ON_OFF_STATE) == STATE_ON
            )

    @property
    def device_class(self):
        """Return the class of the device."""
        if self.tahoma_device.uiclass == "Siren":
            return DEVICE_CLASS_SIREN

        return DEVICE_CLASS_SWITCH

    @property
    def icon(self) -> Optional[str]:
        """Return the icon to use in the frontend, if any."""
        if self.device_class == DEVICE_CLASS_SIREN:
            if self.is_on:
                return "mdi:bell-ring"
            else:
                return "mdi:bell-off"

        return None

    def turn_on(self, **kwargs):
        """Send the on command."""
        if COMMAND_ON in self.tahoma_device.command_definitions:
            return self.apply_action(COMMAND_ON)

        if "ringWithSingleSimpleSequence" in self.tahoma_device.command_definitions:
            # Values taken from iosiren.js (tahomalink.com). Parameter usage is currently unknown.
            return self.apply_action(
                COMMAND_RING_WITH_SINGLE_SIMPLE_SEQUENCE,
                120000,
                75,
                2,
                COMMAND_MEMORIZED_VOLUME,
            )

    def turn_off(self, **kwargs):
        """Send the off command."""
        if COMMAND_OFF in self.tahoma_device.command_definitions:
            return self.apply_action(COMMAND_OFF)

    def toggle(self, **kwargs):
        """Click the switch."""
        if "cycle" in self.tahoma_device.command_definitions:
            return self.apply_action(COMMAND_CYCLE)

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self._state == STATE_ON
