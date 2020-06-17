"""Support for TaHoma sensors."""
from datetime import timedelta
import logging

from homeassistant.components.alarm_control_panel import (
    SUPPORT_ALARM_ARM_AWAY,
    SUPPORT_ALARM_ARM_CUSTOM_BYPASS,
    SUPPORT_ALARM_ARM_HOME,
    SUPPORT_ALARM_ARM_NIGHT,
    SUPPORT_ALARM_TRIGGER,
    AlarmControlPanelEntity,
)
from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_DISARMED,
    STATE_ALARM_TRIGGERED,
)

from .const import DOMAIN, TAHOMA_TYPES
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Tahoma sensors from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]

    entities = []
    controller = data.get("controller")

    for device in data.get("devices"):
        if TAHOMA_TYPES[device.uiclass] == "alarm_control_panel":
            entities.append(TahomaAlarmControlPanel(device, controller))

    async_add_entities(entities)


class TahomaAlarmControlPanel(TahomaDevice, AlarmControlPanelEntity):
    """Representation of a TaHoma Alarm Control Panel."""

    def __init__(self, tahoma_device, controller):
        """Initialize the sensor."""
        self.current_value = None
        self._state = None

        super().__init__(tahoma_device, controller)

    def update(self):
        """Update the state."""
        self.controller.get_states([self.tahoma_device])
        state = None

        if "myfox:AlarmStatusState" in self.tahoma_device.active_states:
            state = self.tahoma_device.active_states.get("myfox:AlarmStatusState")

            if state == "armed":
                self._state = STATE_ALARM_ARMED_AWAY
            elif state == "disarmed":
                self._state = STATE_ALARM_DISARMED
            elif state == "partial":
                self._state = STATE_ALARM_ARMED_HOME
            else:
                self._state = None

        if "core:IntrusionState" in self.tahoma_device.active_states:
            state = self.tahoma_device.active_states.get("core:IntrusionState")

            if state:
                self._state = STATE_ALARM_TRIGGERED

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        attr = {}
        super_attr = super().device_state_attributes
        if super_attr is not None:
            attr.update(super_attr)

        if "core:IntrusionState" in self.tahoma_device.active_states:
            attr["intrusion"] = self.tahoma_device.active_states["core:IntrusionState"]

        if "core:CloudDeviceStatusState" in self.tahoma_device.active_states:
            attr["cloud_device_status"] = self.tahoma_device.active_states[
                "core:CloudDeviceStatusState"
            ]

        return attr

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""

        supported_features = 0

        if (
            "arm" in self.tahoma_device.command_definitions
            or "alarmZoneOn" in self.tahoma_device.command_definitions
        ):
            supported_features |= SUPPORT_ALARM_ARM_AWAY

        if "alarmPartial1" in self.tahoma_device.command_definitions:
            supported_features |= SUPPORT_ALARM_ARM_HOME

        if (
            "partial" in self.tahoma_device.command_definitions
            or "alarmPartial2" in self.tahoma_device.command_definitions
        ):
            supported_features |= SUPPORT_ALARM_ARM_NIGHT

        if "setAlarmStatus" in self.tahoma_device.command_definitions:
            supported_features |= SUPPORT_ALARM_TRIGGER
            supported_features |= SUPPORT_ALARM_ARM_CUSTOM_BYPASS

        return supported_features

    def alarm_disarm(self, code=None):
        """Send disarm command."""

        if "disarm" in self.tahoma_device.command_definitions:
            return self.apply_action("disarm")

        if "alarmOff" in self.tahoma_device.command_definitions:
            return self.apply_action("alarmOff")

    def alarm_arm_home(self, code=None):
        """Send arm home command."""

        if "alarmPartial1" in self.tahoma_device.command_definitions:
            return self.apply_action("alarmPartial1")

    def alarm_arm_night(self, code=None):
        """Send arm night command."""

        if "partial" in self.tahoma_device.command_definitions:
            return self.apply_action("partial")

        if "alarmPartial2" in self.tahoma_device.command_definitions:
            return self.apply_action("alarmPartial2")

    def alarm_arm_away(self, code=None):
        """Send arm away command."""

        if "arm" in self.tahoma_device.command_definitions:
            return self.apply_action("arm")

        if "alarmZoneOn" in self.tahoma_device.command_definitions:
            return self.apply_action("alarmZoneOn")

    def alarm_trigger(self, code=None) -> None:
        """Send alarm trigger command."""
        self.apply_action("setAlarmStatus", "detected")

    def alarm_arm_custom_bypass(self, code=None) -> None:
        """Send arm custom bypass command."""
        self.apply_action("setAlarmStatus", "undetected")
