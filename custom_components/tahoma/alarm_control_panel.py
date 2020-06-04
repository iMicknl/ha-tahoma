"""Support for Tahoma sensors."""
from datetime import timedelta
import logging

from homeassistant.const import ATTR_BATTERY_LEVEL

from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_DISARMED,
)

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    SUPPORT_ALARM_ARM_AWAY,
    SUPPORT_ALARM_ARM_CUSTOM_BYPASS,
    SUPPORT_ALARM_ARM_HOME,
    SUPPORT_ALARM_ARM_NIGHT,
    SUPPORT_ALARM_TRIGGER,
)

from .const import (
    DOMAIN,
    TAHOMA_TYPES,
)
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
    """Representation of a Tahoma Sensor."""

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
            attr["intrusion"] = self.tahoma_device.active_states[
                "core:IntrusionState"
            ]

        if "core:CloudDeviceStatusState" in self.tahoma_device.active_states:
            attr["cloud_device_status"] = self.tahoma_device.active_states[
                "core:CloudDeviceStatusState"
            ]
            
        return attr

    def alarm_disarm(self, code=None):
        """Send disarm command."""
        self.apply_action("disarm")

    def alarm_arm_home(self, code=None):
        """Send arm home command."""
        self.apply_action("partial")

    def alarm_arm_away(self, code=None):
        """Send arm away command."""
        self.apply_action("arm")

    def alarm_trigger(self, code=None) -> None:
        """Send alarm trigger command."""
        self.apply_action("setAlarmStatus", "detected")

    def alarm_arm_custom_bypass(self, code=None) -> None:
        """Send arm custom bypass command."""
        self.apply_action("setAlarmStatus", "undetected")

