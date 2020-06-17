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
        self._state = STATE_OFF
        self._skip_update = False

    def update(self):
        """Update method."""
        # Postpone the immediate state check for changes that take time.
        if self._skip_update:
            self._skip_update = False
            return

        self.controller.get_states([self.tahoma_device])

        _LOGGER.debug("Update %s, state: %s", self._name, self._state)

    @property
    def device_class(self):
        """Return the class of the device."""

        return DEVICE_CLASS_SWITCH

    def turn_on(self, **kwargs):
        """Send the on command."""
        _LOGGER.debug("Turn on: %s", self._name)

        self.apply_action("on")
        self._skip_update = True
        self._state = STATE_ON

    def turn_off(self, **kwargs):
        """Send the off command."""
        self.apply_action("off")
        self._skip_update = True
        self._state = STATE_OFF

    def toggle(self, **kwargs):
        """Click the switch."""
        self.apply_action("cycle")

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return bool(self._state == STATE_ON)
