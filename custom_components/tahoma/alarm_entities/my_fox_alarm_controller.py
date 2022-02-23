"""Support for Overkiz MyFoxAlarmController."""
from __future__ import annotations

from pyoverkiz.enums import OverkizCommand, OverkizCommandParam, OverkizState

from homeassistant.components.alarm_control_panel import AlarmControlPanelEntity
from homeassistant.components.alarm_control_panel.const import (
    SUPPORT_ALARM_ARM_AWAY,
    SUPPORT_ALARM_ARM_NIGHT,
)
from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_DISARMED,
    STATE_ALARM_TRIGGERED,
)

from ..entity import OverkizEntity


class MyFoxAlarmController(OverkizEntity, AlarmControlPanelEntity):
    """Representation of a Overkiz Alarm Control Panel."""

    _attr_supported_features = SUPPORT_ALARM_ARM_AWAY | SUPPORT_ALARM_ARM_NIGHT

    @property
    def state(self):
        """Return the state of the device."""
        if (
            self.executor.select_state(OverkizState.CORE_INTRUSION)
            == OverkizCommandParam.DETECTED
        ):
            return STATE_ALARM_TRIGGERED

        MAP_MYFOX_STATUS_STATE = {
            OverkizCommandParam.ARMED: STATE_ALARM_ARMED_AWAY,
            OverkizCommandParam.DISARMED: STATE_ALARM_DISARMED,
            OverkizCommandParam.PARTIAL: STATE_ALARM_ARMED_NIGHT,
        }

        return MAP_MYFOX_STATUS_STATE[
            self.executor.select_state(OverkizState.MYFOX_ALARM_STATUS)
        ]

    async def async_alarm_disarm(self, code=None):
        """Send disarm command."""
        await self.executor.async_execute_command(OverkizCommand.DISARM)

    async def async_alarm_arm_night(self, code=None):
        """Send arm night command."""
        await self.executor.async_execute_command(OverkizCommand.PARTIAL)

    async def async_alarm_arm_away(self, code=None):
        """Send arm away command."""
        await self.executor.async_execute_command(OverkizCommand.ARM)
