"""Support for Overkiz AlarmPanelController."""
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
)

from ..entity import OverkizEntity


class AlarmPanelController(OverkizEntity, AlarmControlPanelEntity):
    """Representation of a Overkiz Alarm Control Panel."""

    _attr_supported_features = (
        SUPPORT_ALARM_ARM_AWAY | SUPPORT_ALARM_ARM_HOME | SUPPORT_ALARM_ARM_NIGHT
    )

    @property
    def state(self):
        """Return the state of the device."""
        MAP_ARM_TYPE = {
            OverkizCommandParam.DISARMED: STATE_ALARM_DISARMED,
            OverkizCommandParam.ARMED_DAY: STATE_ALARM_ARMED_HOME,
            OverkizCommandParam.ARMED_NIGHT: STATE_ALARM_ARMED_NIGHT,
            OverkizCommandParam.ARMED: STATE_ALARM_ARMED_AWAY,
        }

        return MAP_ARM_TYPE[
            self.executor.select_state(OverkizState.VERISURE_ALARM_PANEL_MAIN_ARM_TYPE)
        ]

    async def async_alarm_disarm(self, code=None):
        """Send disarm command."""
        await self.executor.async_execute_command(OverkizCommand.DISARM)

    async def async_alarm_arm_home(self, code=None):
        """Send arm home command."""
        await self.executor.async_execute_command(OverkizCommand.ARM_PARTIAL_DAY)

    async def async_alarm_arm_night(self, code=None):
        """Send arm night command."""
        await self.executor.async_execute_command(OverkizCommand.ARM_PARTIAL_NIGHT)

    async def async_alarm_arm_away(self, code=None):
        """Send arm away command."""
        await self.executor.async_execute_command(OverkizCommand.ARM)
