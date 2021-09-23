"""Support for Overkiz sirens."""
from homeassistant.components.siren import DOMAIN as SIREN, SirenEntity
from homeassistant.components.siren.const import (
    ATTR_DURATION,
    SUPPORT_DURATION,
    SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON,
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

    _attr_supported_features = SUPPORT_TURN_OFF | SUPPORT_TURN_ON | SUPPORT_DURATION

    @property
    def is_on(self):
        """Get whether the siren is in on state."""
        return self.executor.select_state(CORE_ON_OFF_STATE) == STATE_ON

    async def async_turn_on(self, **kwargs):
        """Send the on command."""

        if kwargs.get(ATTR_DURATION):
            duration = kwargs.get(ATTR_DURATION)
        else:
            duration = 2 * 60  # 2 minutes

        duration_in_ms = duration * 1000

        await self.executor.async_execute_command(
            COMMAND_RING_WITH_SINGLE_SIMPLE_SEQUENCE,  # https://www.tahomalink.com/enduser-mobile-web/steer-html5-client/vendor/somfy/io/siren/const.js
            duration_in_ms,  # 2 minutes
            75,  # 90 seconds bip, 30 seconds silence
            2,  # repeat 3 times
            COMMAND_MEMORIZED_VOLUME,
        )

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        # await self.executor.async_execute_command(
        #     COMMAND_RING_WITH_SINGLE_SIMPLE_SEQUENCE,
        #     2000,
        #     100,
        #     0,
        #     COMMAND_STANDARD,
        # )

        await self.async_cancel_or_stop_siren(COMMAND_RING_WITH_SINGLE_SIMPLE_SEQUENCE)

    async def async_cancel_or_stop_siren(self, cancel_commands) -> None:
        """Cancel running execution or send stop command."""
        # Cancelling a running execution will stop the siren movement
        # Retrieve executions initiated via Home Assistant from Data Update Coordinator queue
        exec_id = next(
            (
                exec_id
                # Reverse dictionary to cancel the last added execution
                for exec_id, execution in reversed(self.coordinator.executions.items())
                if execution.get("deviceurl") == self.device.deviceurl
                and execution.get("command_name") in cancel_commands
            ),
            None,
        )

        if exec_id:
            return await self.executor.async_cancel_command(exec_id)

        # Retrieve executions initiated outside Home Assistant via API
        executions = await self.coordinator.client.get_current_executions()
        exec_id = next(
            (
                execution.id
                for execution in executions
                # Reverse dictionary to cancel the last added execution
                for action in reversed(execution.action_group.get("actions"))
                for command in action.get("commands")
                if action.get("deviceurl") == self.device.deviceurl
                and command.get("name") in cancel_commands
            ),
            None,
        )

        if exec_id:
            return await self.executor.async_cancel_command(exec_id)
