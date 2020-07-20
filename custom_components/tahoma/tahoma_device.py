"""Parent class for every TaHoma devices."""
from datetime import timedelta

from homeassistant.const import ATTR_BATTERY_LEVEL
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

from .const import DOMAIN
from .tahoma_api import Action

ATTR_RSSI_LEVEL = "rssi_level"

CORE_AVAILABILITY_STATE = "core:AvailabilityState"
CORE_BATTERY_STATE = "core:BatteryState"
CORE_RSSI_LEVEL_STATE = "core:RSSILevelState"
CORE_SENSOR_DEFECT_STATE = "core:SensorDefectState"
CORE_STATUS_STATE = "core:StatusState"

STATE_AVAILABLE = "available"
STATE_BATTERY_FULL = "full"
STATE_BATTERY_NORMAL = "normal"
STATE_BATTERY_LOW = "low"
STATE_BATTERY_VERY_LOW = "verylow"
STATE_DEAD = "dead"


class TahomaDevice(Entity):
    """Representation of a TaHoma device entity."""

    def __init__(self, tahoma_device, controller):
        """Initialize the device."""
        self.tahoma_device = tahoma_device
        self.controller = controller
        self._exec_queue = []

    def update(self):
        """Update method."""
        if self.should_wait():
            self.hass.add_job(self.update)
            return
        self.controller.get_states([self.tahoma_device])
        self.schedule_update_ha_state()

    async def async_added_to_hass(self):
        """Entity created."""
        await super().async_added_to_hass()
        self.schedule_update_ha_state(True)

    @property
    def name(self):
        """Return the name of the device."""
        return self.tahoma_device.label

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        states = self.tahoma_device.active_states

        if CORE_STATUS_STATE in states:
            return states.get(CORE_STATUS_STATE) == STATE_AVAILABLE

        if CORE_SENSOR_DEFECT_STATE in states:
            return states.get(CORE_SENSOR_DEFECT_STATE) != STATE_DEAD

        if CORE_AVAILABILITY_STATE in states:
            return states.get(CORE_AVAILABILITY_STATE) == STATE_AVAILABLE

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
        return self.tahoma_device.type.startswith("rts")

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        attr = {
            "uiclass": self.tahoma_device.uiclass,
            "widget": self.tahoma_device.widget,
            "type": self.tahoma_device.type,
        }

        states = self.tahoma_device.active_states

        if CORE_RSSI_LEVEL_STATE in states:
            attr[ATTR_RSSI_LEVEL] = states.get(CORE_RSSI_LEVEL_STATE)

        if CORE_BATTERY_STATE in states:
            battery_state = states.get(CORE_BATTERY_STATE)

            if battery_state == STATE_BATTERY_FULL:
                battery_state = 100
            elif battery_state == STATE_BATTERY_NORMAL:
                battery_state = 75
            elif battery_state == STATE_BATTERY_LOW:
                battery_state = 25
            elif battery_state == STATE_BATTERY_VERY_LOW:
                battery_state = 10

            attr[ATTR_BATTERY_LEVEL] = battery_state

        if CORE_SENSOR_DEFECT_STATE in states:
            if states.get(CORE_SENSOR_DEFECT_STATE) == STATE_DEAD:
                attr[ATTR_BATTERY_LEVEL] = 0

        for state_name, value in states.items():
            if "State" in state_name:
                attr[state_name] = value

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

    def select_command(self, *commands):
        """Select first existing command in a list of commands."""
        return next(
            (c for c in self.tahoma_device.command_definitions if c in list(commands)),
            None,
        )

    def has_command(self, *commands):
        """Return True if a command exists in a list of commands."""
        return self.select_command(*commands) is not None

    def select_state(self, *states):
        """Select first existing active state in a list of states."""
        return next(
            (
                v
                for k, v in self.tahoma_device.active_states.items()
                if k in list(states)
            ),
            None,
        )

    def has_state(self, *states):
        """Return True if a state exists in self."""
        return self.select_state(*states)

    @Throttle(timedelta(seconds=1))
    def should_wait(self):
        """Wait for actions to finish."""
        exec_queue = self.controller.get_current_executions()
        self._exec_queue = [e for e in self._exec_queue if e in exec_queue]
        return len(self._exec_queue) > 0

    async def async_apply_action(self, cmd_name, *args):
        """Apply Action to Device in async context."""
        await self.hass.async_add_executor_job(self.apply_action, cmd_name, *args)

    def apply_action(self, cmd_name, *args):
        """Apply Action to Device."""
        if cmd_name is None:
            raise ValueError(f"Command {cmd_name} does not exist for {self.name}")
        action = Action(self.tahoma_device.url)
        action.add_command(cmd_name, *args)
        exec_id = self.controller.apply_actions("HomeAssistant", [action])
        self._exec_queue.append(exec_id)
