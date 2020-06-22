"""Parent class for every TaHoma devices."""

from homeassistant.const import ATTR_BATTERY_LEVEL
from homeassistant.helpers.entity import Entity

from .const import (
    ATTR_RSSI_LEVEL,
    CORE_RSSI_LEVEL_STATE,
    CORE_SENSOR_DEFECT_STATE,
    CORE_STATUS_STATE,
    DOMAIN,
)
from .tahoma_api import Action


class TahomaDevice(Entity):
    """Representation of a TaHoma device entity."""

    def __init__(self, tahoma_device, controller):
        """Initialize the device."""
        self.tahoma_device = tahoma_device
        self._name = self.tahoma_device.label
        self.controller = controller

    async def async_added_to_hass(self):
        """Entity created."""
        await super().async_added_to_hass()
        self.schedule_update_ha_state(True)

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""

        if CORE_STATUS_STATE in self.tahoma_device.active_states:
            return bool(
                self.tahoma_device.active_states.get(CORE_STATUS_STATE) == "available"
            )

        if CORE_SENSOR_DEFECT_STATE in self.tahoma_device.active_states:
            return (
                self.tahoma_device.active_states.get(CORE_SENSOR_DEFECT_STATE) != "dead"
            )

        # A RTS power socket doesn't have a feedback channel,
        # so we must assume the socket is available.
        return True

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self.tahoma_device.url

    @property
    def assumed_state(self):
        """Return True if unable to access real state of the entity."""
        if self.tahoma_device.type.startswith("rts"):
            return True

        return False

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""

        attr = {
            "uiclass": self.tahoma_device.uiclass,
            "widget": self.tahoma_device.widget,
            "type": self.tahoma_device.type,
        }

        if CORE_RSSI_LEVEL_STATE in self.tahoma_device.active_states:
            attr[ATTR_RSSI_LEVEL] = self.tahoma_device.active_states[
                CORE_RSSI_LEVEL_STATE
            ]

        # TODO Parse 'lowBattery' for low battery warning. 'dead' for not available.
        # "dead", "lowBattery", "maintenanceRequired", "noDefect"
        if CORE_SENSOR_DEFECT_STATE in self.tahoma_device.active_states:
            attr[ATTR_BATTERY_LEVEL] = self.tahoma_device.active_states[
                CORE_SENSOR_DEFECT_STATE
            ]

        return attr

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "manufacturer": "Somfy",
            "name": self.name,
            "model": self.tahoma_device.widget,
            "sw_version": self.tahoma_device.type,
        }

    async def async_apply_action(self, cmd_name, *args):
        """Apply Action to Device in async context."""
        await self.hass.async_add_executor_job(self.apply_action, cmd_name, *args)

    def apply_action(self, cmd_name, *args):
        """Apply Action to Device."""

        action = Action(self.tahoma_device.url)
        action.add_command(cmd_name, *args)
        exec_id = self.controller.apply_actions("HomeAssistant", [action])
        while exec_id in self.controller.get_current_executions():
            continue
