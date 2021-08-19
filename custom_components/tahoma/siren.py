"""Support for Overkiz sirens."""
from homeassistant.components.siren import DOMAIN as SIREN, SirenEntity
from homeassistant.components.siren.const import (
    SUPPORT_DURATION,
    SUPPORT_TONES,
    SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON,
    SUPPORT_VOLUME_SET,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CORE_ON_OFF_STATE, DOMAIN
from .entity import OverkizEntity

COMMAND_MEMORIZED_VOLUME = "memorizedVolume"
COMMAND_RING_WITH_SINGLE_SIMPLE_SEQUENCE = "ringWithSingleSimpleSequence"
COMMAND_STANDARD = "standard"


STATE_ON = "on"

SUPPORT_FLAGS = SUPPORT_TURN_OFF | SUPPORT_TURN_ON


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Overkiz sirens from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities = [
        OverkizSiren(device.deviceurl, coordinator)
        for device in data["platforms"][SIREN]
    ]

    async_add_entities(entities)


class OverkizSiren(OverkizEntity, SirenEntity):
    """Representation an Overkiz Switch."""

    _attr_supported_features = (
        SUPPORT_FLAGS | SUPPORT_TONES | SUPPORT_VOLUME_SET | SUPPORT_DURATION
    )

    async def async_turn_on(self, **_):
        """Send the on command."""

        duration = 2 * 60  # 2 minutes
        duration_in_ms = duration * 1000

        await self.executor.async_execute_command(
            COMMAND_RING_WITH_SINGLE_SIMPLE_SEQUENCE,  # https://www.tahomalink.com/enduser-mobile-web/steer-html5-client/vendor/somfy/io/siren/const.js
            duration_in_ms,  # 2 minutes
            75,  # 90 seconds bip, 30 seconds silence
            2,  # repeat 3 times
            COMMAND_MEMORIZED_VOLUME,
        )

    async def async_turn_off(self, **_):
        """Send the off command."""
        await self.executor.async_execute_command(
            COMMAND_RING_WITH_SINGLE_SIMPLE_SEQUENCE,
            2000,
            100,
            0,
            COMMAND_STANDARD,
        )

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self.executor.select_state(CORE_ON_OFF_STATE) == STATE_ON
