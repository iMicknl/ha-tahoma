"""Support for Overkiz lock."""
from homeassistant.components.lock import DOMAIN as LOCK, LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_LOCKED
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import OverkizEntity

COMMAND_LOCK = "lock"
COMMAND_UNLOCK = "unlock"

CORE_LOCKED_UNLOCKED_STATE = "core:LockedUnlockedState"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Overkiz locks from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities = [
        OverkizLock(device.device_url, coordinator)
        for device in data["platforms"][LOCK]
    ]

    async_add_entities(entities)


class OverkizLock(OverkizEntity, LockEntity):
    """Representation of a TaHoma Lock."""

    async def async_unlock(self, **_):
        """Unlock method."""
        await self.executor.async_execute_command(COMMAND_UNLOCK)

    async def async_lock(self, **_):
        """Lock method."""
        await self.executor.async_execute_command(COMMAND_LOCK)

    @property
    def is_locked(self):
        """Return True if the lock is locked."""
        return self.executor.select_state(CORE_LOCKED_UNLOCKED_STATE) == STATE_LOCKED
