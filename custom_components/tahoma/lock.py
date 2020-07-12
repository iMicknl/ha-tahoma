"""Support for TaHoma lock."""
from datetime import timedelta
import logging

from homeassistant.components.lock import LockEntity
from homeassistant.const import ATTR_BATTERY_LEVEL, STATE_LOCKED, STATE_UNLOCKED

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

    def __init__(self, tahoma_device, controller):
        """Initialize the device."""
        super().__init__(tahoma_device, controller)
        self._lock_status = None

    def unlock(self, **kwargs):
        """Unlock method."""
        self.apply_action(COMMAND_UNLOCK)

    def lock(self, **kwargs):
        """Lock method."""
        self.apply_action(COMMAND_LOCK)

    @property
    def name(self):
        """Return the name of the lock."""
        return self.tahoma_device.active_states["core:NameState"]

    @property
    def is_locked(self):
        """Return True if the lock is locked."""
        return (
            self.tahoma_device.active_states.get("core:LockedUnlockedState")
            == STATE_LOCKED
        )
