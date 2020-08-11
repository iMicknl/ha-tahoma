"""Support for TaHoma alarm."""
from datetime import timedelta
from typing import Optional

from homeassistant.components.alarm_control_panel import (
    DOMAIN as ALARM_CONTROL_PANEL,
    AlarmControlPanelEntity,
)
from homeassistant.components.alarm_control_panel.const import (
    SUPPORT_ALARM_ARM_AWAY,
    SUPPORT_ALARM_ARM_CUSTOM_BYPASS,
    SUPPORT_ALARM_ARM_HOME,
    SUPPORT_ALARM_ARM_NIGHT,
    SUPPORT_ALARM_TRIGGER,
)
from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_DISARMED,
    STATE_ALARM_TRIGGERED,
    STATE_OFF,
)

from .const import DOMAIN
from .tahoma_device import TahomaDevice

COMMAND_ARM = "arm"
COMMAND_ALARM_ZONE_ON = "alarmZoneOn"
COMMAND_PARTIAL = "partial"
COMMAND_ALARM_PARTIAL_1 = "alarmPartial1"
COMMAND_ALARM_PARTIAL_2 = "alarmPartial2"
COMMAND_SET_ALARM_STATUS = "setAlarmStatus"
COMMAND_DISARM = "disarm"
COMMAND_ALARM_OFF = "alarmOff"


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data.get("coordinator")

    entities = [
        TahomaAlarmControlPanel(device.deviceurl, coordinator)
        for device in data.get("entities").get(ALARM_CONTROL_PANEL)
    ]
    async_add_entities(entities)


class TahomaAlarmControlPanel(TahomaDevice, AlarmControlPanelEntity):
    """Representation of a TaHoma Alarm Control Panel."""

    @property
    def state(self):
        """Return the state of the device."""

        alarm_state = None

        if self.has_state("myfox:AlarmStatusState"):
            state = self.select_state("myfox:AlarmStatusState")

            if state == "armed":
                alarm_state = STATE_ALARM_ARMED_AWAY
            elif state == "disarmed":
                alarm_state = STATE_ALARM_DISARMED
            elif state == "partial":
                alarm_state = STATE_ALARM_ARMED_HOME
            else:
                alarm_state = None

        if self.has_state("core:IntrusionState"):
            state = self.select_state("core:IntrusionState")

            if state:
                alarm_state = STATE_ALARM_TRIGGERED

        if self.has_state("internal:CurrentAlarmModeState"):
            state = self.select_state("internal:CurrentAlarmModeState")

            if state == "off":
                alarm_state = STATE_OFF

        if self.has_state("internal:IntrusionDetectedState"):
            state = self.select_state("internal:IntrusionDetectedState")

            if state == "detected":
                alarm_state = STATE_ALARM_TRIGGERED

        return alarm_state

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        supported_features = 0

        if self.has_command(COMMAND_ARM, COMMAND_ALARM_ZONE_ON):
            supported_features |= SUPPORT_ALARM_ARM_AWAY

        if self.has_command(COMMAND_ALARM_PARTIAL_1):
            supported_features |= SUPPORT_ALARM_ARM_HOME

        if self.has_command(COMMAND_PARTIAL, COMMAND_ALARM_PARTIAL_2):
            supported_features |= SUPPORT_ALARM_ARM_NIGHT

        if self.has_command(COMMAND_SET_ALARM_STATUS):
            supported_features |= SUPPORT_ALARM_TRIGGER
            supported_features |= SUPPORT_ALARM_ARM_CUSTOM_BYPASS

        return supported_features

    async def async_alarm_disarm(self, code=None):
        """Send disarm command."""
        await self.async_execute_command(
            self.select_command(COMMAND_DISARM, COMMAND_ALARM_OFF)
        )

    async def async_alarm_arm_home(self, code=None):
        """Send arm home command."""
        await self.async_execute_command(self.select_command(COMMAND_ALARM_PARTIAL_1))

    async def async_alarm_arm_night(self, code=None):
        """Send arm night command."""
        await self.async_execute_command(
            self.select_command(COMMAND_PARTIAL, COMMAND_ALARM_PARTIAL_2)
        )

    async def async_alarm_arm_away(self, code=None):
        """Send arm away command."""
        await self.async_execute_command(
            self.select_command(COMMAND_ARM, COMMAND_ALARM_ZONE_ON)
        )

    async def async_alarm_trigger(self, code=None) -> None:
        """Send alarm trigger command."""
        await self.async_execute_command(COMMAND_SET_ALARM_STATUS, "detected")

    async def async_alarm_arm_custom_bypass(self, code=None) -> None:
        """Send arm custom bypass command."""
        await self.async_execute_command(COMMAND_SET_ALARM_STATUS, "undetected")
