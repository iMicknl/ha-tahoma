"""Parent class for every TaHoma device."""
import logging
import re
from typing import Any, Dict, Optional

from homeassistant.const import ATTR_BATTERY_LEVEL
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from pyhoma.models import Command, Device

from .const import DOMAIN
from .coordinator import TahomaDataUpdateCoordinator

ATTR_RSSI_LEVEL = "rssi_level"

CORE_AVAILABILITY_STATE = "core:AvailabilityState"
CORE_BATTERY_STATE = "core:BatteryState"
CORE_MANUFACTURER = "core:Manufacturer"
CORE_MANUFACTURER_NAME_STATE = "core:ManufacturerNameState"
CORE_MODEL_STATE = "core:ModelState"
CORE_PRODUCT_MODEL_NAME_STATE = "core:ProductModelNameState"
CORE_RSSI_LEVEL_STATE = "core:RSSILevelState"
CORE_SENSOR_DEFECT_STATE = "core:SensorDefectState"
CORE_STATUS_STATE = "core:StatusState"

IO_MODEL_STATE = "io:ModelState"

STATE_AVAILABLE = "available"
STATE_BATTERY_FULL = "full"
STATE_BATTERY_NORMAL = "normal"
STATE_BATTERY_LOW = "low"
STATE_BATTERY_VERY_LOW = "verylow"
STATE_DEAD = "dead"

BATTERY_MAP = {
    STATE_BATTERY_FULL: 100,
    STATE_BATTERY_NORMAL: 75,
    STATE_BATTERY_LOW: 25,
    STATE_BATTERY_VERY_LOW: 10,
}

_LOGGER = logging.getLogger(__name__)


class TahomaEntity(CoordinatorEntity, Entity):
    """Representation of a TaHoma device entity."""

    def __init__(self, device_url: str, coordinator: TahomaDataUpdateCoordinator):
        """Initialize the device."""
        super().__init__(coordinator)
        self.device_url = device_url
        self.base_device_url = self.get_base_device_url()

    @property
    def device(self) -> Device:
        """Return TaHoma device linked to this entity."""
        return self.coordinator.data[self.device_url]

    @property
    def name(self) -> str:
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
    def assumed_state(self) -> bool:
        """Return True if unable to access real state of the entity."""
        return not self.device.states

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes of the device."""
        attr = {}

        if self.has_state(CORE_RSSI_LEVEL_STATE):
            attr[ATTR_RSSI_LEVEL] = self.select_state(CORE_RSSI_LEVEL_STATE)

        if self.has_state(CORE_BATTERY_STATE):
            battery_state = self.select_state(CORE_BATTERY_STATE)
            attr[ATTR_BATTERY_LEVEL] = BATTERY_MAP.get(battery_state, battery_state)

        if self.select_state(CORE_SENSOR_DEFECT_STATE) == STATE_DEAD:
            attr[ATTR_BATTERY_LEVEL] = 0

        if self.device.attributes:
            for attribute in self.device.attributes:
                attr[attribute.name] = attribute.value

        if self.device.states:
            for state in self.device.states:
                if "State" in state.name:
                    attr[state.name] = state.value

        return attr

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return device registry information for this entity."""
        # Some devices, such as the Smart Thermostat have several devices in one physical device,
        # with same device url, terminated by '#' and a number.
        # In this case, we use the base device url as the device identifier.
        if "#" in self.device_url and not self.device_url.endswith("#1"):
            # Only return the url of the base device, to inherit device name and model from parent device.
            return {
                "identifiers": {(DOMAIN, self.base_device_url)},
            }

        manufacturer = (
            self.select_attribute(CORE_MANUFACTURER)
            or self.select_state(CORE_MANUFACTURER_NAME_STATE)
            or "Somfy"
        )
        model = (
            self.select_state(
                CORE_MODEL_STATE, CORE_PRODUCT_MODEL_NAME_STATE, IO_MODEL_STATE
            )
            or self.device.widget
        )

        return {
            "identifiers": {(DOMAIN, self.base_device_url)},
            "name": self.device.label,
            "manufacturer": manufacturer,
            "model": model,
            "sw_version": self.device.controllable_name,
            "via_device": self.get_gateway_id(),
            "suggested_area": self.coordinator.areas[self.device.placeoid],
        }

    def select_command(self, *commands: str) -> Optional[str]:
        """Select first existing command in a list of commands."""
        existing_commands = self.device.definition.commands

        return next((c for c in commands if c in existing_commands), None)

    def has_command(self, *commands: str) -> bool:
        """Return True if a command exists in a list of commands."""
        return self.select_command(*commands) is not None

    def select_state(self, *states) -> Optional[str]:
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

    def has_state(self, *states: str) -> bool:
        """Return True if a state exists in self."""
        return self.select_state(*states) is not None

    def select_attribute(self, *attributes) -> Optional[str]:
        """Select first existing active state in a list of states."""
        if self.device.attributes:
            return next(
                (
                    attribute.value
                    for attribute in self.device.attributes
                    if attribute.name in list(attributes)
                ),
                None,
            )

    async def async_execute_command(self, command_name: str, *args: Any):
        """Execute device command in async context."""
        try:
            exec_id = await self.coordinator.client.execute_command(
                self.device.deviceurl,
                Command(command_name, list(args)),
                "Home Assistant",
            )
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error(exception)
            return

        # ExecutionRegisteredEvent doesn't contain the deviceurl, thus we need to register it here
        self.coordinator.executions[exec_id] = {
            "deviceurl": self.device.deviceurl,
            "command_name": command_name,
        }

        await self.coordinator.async_refresh()

    async def async_cancel_command(self, exec_id: str):
        """Cancel device command in async context."""
        await self.coordinator.client.cancel_command(exec_id)

    def get_base_device_url(self):
        """Return base device url."""
        if "#" not in self.device_url:
            return self.device_url

        device_url, _ = self.device_url.split("#")
        return device_url

    def get_gateway_id(self):
        """Retrieve gateway id from device url."""
        result = re.search(r":\/\/(.*)\/", self.device_url)

        if result:
            return result.group(1)
        else:
            return None
