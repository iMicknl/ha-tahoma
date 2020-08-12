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
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_DISARMED,
    STATE_ALARM_PENDING,
    STATE_ALARM_TRIGGERED,
)

from .const import DOMAIN
from .tahoma_device import TahomaDevice

COMMAND_ALARM_OFF = "alarmOff"
COMMAND_ALARM_ON = "alarmOn"
COMMAND_ALARM_PARTIAL_1 = "alarmPartial1"
COMMAND_ALARM_PARTIAL_2 = "alarmPartial2"
COMMAND_ARM = "arm"
COMMAND_DISARM = "disarm"
COMMAND_PARTIAL = "partial"
COMMAND_SET_ALARM_STATUS = "setAlarmStatus"

CORE_INTRUSION_STATE = "core:IntrusionState"
INTERNAL_CURRENT_ALARM_MODE_STATE = "internal:CurrentAlarmModeState"
INTERNAL_INTRUSION_DETECTED_STATE = "internal:IntrusionDetectedState"
MYFOX_ALARM_STATUS_STATE = "myfox:AlarmStatusState"

STATE_ARMED = "armed"
STATE_DETECTED = "detected"
STATE_DISARMED = "disarmed"
STATE_OFF = "off"
STATE_PARTIAL = "partial"
STATE_PARTIAL_1 = "partial1"
STATE_PARTIAL_2 = "partial2"
STATE_PENDING = "pending"
STATE_TOTAL = "total"
STATE_UNDETECTED = "undetected"


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

        if self.has_state(MYFOX_ALARM_STATUS_STATE):
            state = self.select_state(MYFOX_ALARM_STATUS_STATE)

            if state == STATE_ARMED:
                alarm_state = STATE_ALARM_ARMED_AWAY
            elif state == STATE_DISARMED:
                alarm_state = STATE_ALARM_DISARMED
            elif state == STATE_PARTIAL:
                alarm_state = STATE_ALARM_ARMED_NIGHT

        if self.has_state(INTERNAL_CURRENT_ALARM_MODE_STATE):
            state = self.select_state(INTERNAL_CURRENT_ALARM_MODE_STATE)

            if state == STATE_OFF:
                alarm_state = STATE_ALARM_DISARMED
            elif state == STATE_PARTIAL_1:
                alarm_state = STATE_ALARM_ARMED_HOME
            elif state == STATE_PARTIAL_2:
                alarm_state = STATE_ALARM_ARMED_NIGHT
            elif state == STATE_TOTAL:
                alarm_state = STATE_ALARM_ARMED_AWAY

        if self.has_state(CORE_INTRUSION_STATE, INTERNAL_INTRUSION_DETECTED_STATE):
            state = self.select_state(
                CORE_INTRUSION_STATE, INTERNAL_INTRUSION_DETECTED_STATE
            )

            if state == STATE_DETECTED:
                alarm_state = STATE_ALARM_TRIGGERED
            elif state == STATE_PENDING:
                alarm_state = STATE_ALARM_PENDING

        return alarm_state

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        supported_features = 0

        if self.has_command(COMMAND_ARM, COMMAND_ALARM_ON):
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
            self.select_command(COMMAND_ARM, COMMAND_ALARM_ON)
        )

    async def async_alarm_trigger(self, code=None) -> None:
        """Send alarm trigger command."""
        await self.async_execute_command(COMMAND_SET_ALARM_STATUS, STATE_DETECTED)

    async def async_alarm_arm_custom_bypass(self, code=None) -> None:
        """Send arm custom bypass command."""
        await self.async_execute_command(COMMAND_SET_ALARM_STATUS, STATE_UNDETECTED)

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        # if self.device.widget == "TSKAlarmController":
        #     return False

        return True
