"""Parent class for every TaHoma devices."""
from datetime import timedelta

from tahoma_api.client import TahomaClient
from tahoma_api.models import Command, Device

from homeassistant.const import ATTR_BATTERY_LEVEL
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

from .const import DOMAIN

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

    def __init__(self, device: Device, client: TahomaClient):
        """Initialize the device."""
        self.device = device
        self.client = client
        self._exec_queue = []

    async def async_update(self):
        """Update method."""
        if await self.should_wait():
            self.hass.async_add_job(self.async_update)
            return

        self.device.states = await self.client.get_state(self.device.deviceurl)

    async def async_added_to_hass(self):
        """Entity created."""
        await super().async_added_to_hass()
        self.async_schedule_update_ha_state(True)

    @property
    def name(self):
        """Return the name of the device."""
        return self.device.label

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.device.available

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self.device.deviceurl

    @property
    def assumed_state(self):
        """Return True if unable to access real state of the entity."""
        return self.device.states is not None and len(self.device.states) > 0

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        attr = {
            "ui_class": self.device.ui_class,
            "widget": self.device.widget,
            "controllable_name": self.device.controllable_name,
        }

        if self.has_state(CORE_RSSI_LEVEL_STATE):
            attr[ATTR_RSSI_LEVEL] = self.select_state(CORE_RSSI_LEVEL_STATE)

        if self.has_state(CORE_BATTERY_STATE):
            battery_state = self.select_state(CORE_BATTERY_STATE)

            if battery_state == STATE_BATTERY_FULL:
                battery_state = 100
            elif battery_state == STATE_BATTERY_NORMAL:
                battery_state = 75
            elif battery_state == STATE_BATTERY_LOW:
                battery_state = 25
            elif battery_state == STATE_BATTERY_VERY_LOW:
                battery_state = 10

            attr[ATTR_BATTERY_LEVEL] = battery_state

        if self.has_state(CORE_SENSOR_DEFECT_STATE):
            if self.select_state(CORE_SENSOR_DEFECT_STATE) == STATE_DEAD:
                attr[ATTR_BATTERY_LEVEL] = 0

        if self.device.states:
            for state in self.device.states:
                if "State" in state.name:
                    attr[state.name] = state.value

        return attr

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "manufacturer": "Somfy",
            "name": self.name,
            "model": self.device.widget,
            "sw_version": self.device.controllable_name,
        }

    def select_command(self, *commands):
        """Select first existing command in a list of commands."""
        return next(
            (
                c
                for c in self.device.definition.commands
                if c.command_name in list(commands)
            ),
            None,
        )

    def has_command(self, *commands):
        """Return True if a command exists in a list of commands."""
        return self.select_command(*commands) is not None

    def select_state(self, *states):
        """Select first existing active state in a list of states."""
        if self.device.states:
            return next(
                (
                    state.value
                    for state in self.device.states
                    if state.name in list(states)
                ),
                None,
            )
        return None

    def has_state(self, *states):
        """Return True if a state exists in self."""
        return self.select_state(*states)

    @Throttle(timedelta(seconds=1))
    async def should_wait(self):
        """Wait for actions to finish."""
        exec_queue = await self.client.get_current_executions()
        self._exec_queue = [e.id for e in self._exec_queue if e in exec_queue]

        return len(self._exec_queue) > 0

    async def async_execute_command(self, command_name, *args):
        """Execute device command in async context."""
        exec_id = await self.client.execute_command(
            self.device.deviceurl, Command(command_name, *args), "Home Assistant"
        )

        self._exec_queue.append(exec_id)
