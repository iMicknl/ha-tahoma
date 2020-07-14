"""Support for TaHoma lock."""
from datetime import timedelta
import logging

from homeassistant.components.lock import LockEntity
from homeassistant.const import STATE_LOCKED

from .const import DOMAIN, TAHOMA_TYPES
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=120)

COMMAND_LOCK = "lock"
COMMAND_UNLOCK = "unlock"

CORE_LOCKED_UNLOCKED_STATE = "core:LockedUnlockedState"


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma locks from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]
    controller = data.get("controller")

    entities = [
        TahomaLock(device, controller)
        for device in data.get("devices")
        if TAHOMA_TYPES[device.uiclass] == "lock"
    ]

    async_add_entities(entities)


class TahomaLock(TahomaDevice, LockEntity):
    """Representation a TaHoma lock."""

    def unlock(self, **kwargs):
        """Unlock method."""
        self.apply_action(COMMAND_UNLOCK)

    def lock(self, **kwargs):
        """Lock method."""
        self.apply_action(COMMAND_LOCK)

    @property
    def is_locked(self):
        """Return True if the lock is locked."""
        return self.select_state([CORE_LOCKED_UNLOCKED_STATE]) == STATE_LOCKED
