"""Support for Overkiz TSKAlarmController."""
from __future__ import annotations

from pyoverkiz.enums import OverkizCommand, OverkizCommandParam, OverkizState

from homeassistant.components.alarm_control_panel import AlarmControlPanelEntity
from homeassistant.components.alarm_control_panel.const import (
    SUPPORT_ALARM_ARM_AWAY,
    SUPPORT_ALARM_ARM_HOME,
    SUPPORT_ALARM_ARM_NIGHT,
)
from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_DISARMED,
    STATE_ALARM_PENDING,
    STATE_ALARM_TRIGGERED,
)

from ..entity import OverkizEntity


class TSKAlarmController(OverkizEntity, AlarmControlPanelEntity):
    """Representation of a Overkiz Alarm Control Panel."""

    _attr_supported_features = (
        SUPPORT_ALARM_ARM_AWAY | SUPPORT_ALARM_ARM_HOME | SUPPORT_ALARM_ARM_NIGHT
    )
    _attr_entity_registry_enabled_default = False

    @property
    def state(self):
        """Return the state of the device."""
        if (
            self.executor.select_state(OverkizState.INTERNAL_INTRUSION_DETECTED)
            == OverkizCommandParam.DETECTED
        ):
            return STATE_ALARM_TRIGGERED

        if self.executor.select_state(
            OverkizState.INTERNAL_CURRENT_ALARM_MODE
        ) != self.executor.select_state(OverkizState.INTERNAL_TARGET_ALARM_MODE):
            return STATE_ALARM_PENDING

        MAP_INTERNAL_STATUS_STATE = {
            OverkizCommandParam.OFF: STATE_ALARM_DISARMED,
            OverkizCommandParam.ZONE_1: STATE_ALARM_ARMED_HOME,
            OverkizCommandParam.ZONE_2: STATE_ALARM_ARMED_NIGHT,
            OverkizCommandParam.TOTAL: STATE_ALARM_ARMED_AWAY,
        }

        return MAP_INTERNAL_STATUS_STATE[
            self.executor.select_state(OverkizState.INTERNAL_TARGET_ALARM_MODE)
        ]

    async def async_alarm_disarm(self, code=None):
        """Send disarm command."""
        await self.executor.async_execute_command(OverkizCommand.ALARM_OFF)

    async def async_alarm_arm_home(self, code=None):
        """Send arm home command."""
        await self.executor.async_execute_command(
            OverkizCommand.SET_TARGET_ALARM_MODE, OverkizCommandParam.PARTIAL_1
        )

    async def async_alarm_arm_night(self, code=None):
        """Send arm night command."""
        await self.executor.async_execute_command(
            OverkizCommand.SET_TARGET_ALARM_MODE, OverkizCommandParam.PARTIAL_2
        )

    async def async_alarm_arm_away(self, code=None):
        """Send arm away command."""
        await self.executor.async_execute_command(
            OverkizCommand.SET_TARGET_ALARM_MODE, OverkizCommandParam.TOTAL
        )

    async def async_alarm_trigger(self, code=None) -> None:
        """Send alarm trigger command."""
        await self.executor.async_execute_command(OverkizCommand.ALARM_ON)
