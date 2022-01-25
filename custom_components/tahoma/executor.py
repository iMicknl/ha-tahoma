"""Class for helpers and community with the OverKiz API."""
from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

from pyoverkiz.models import Command, Device

from .coordinator import OverkizDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class OverkizExecutor:
    """Representation of an Overkiz device with execution handler."""

    def __init__(self, device_url: str, coordinator: OverkizDataUpdateCoordinator):
        """Initialize the executor."""
        self.device_url = device_url
        self.coordinator = coordinator
        self.base_device_url, *_ = self.device_url.split("#")

    @property
    def device(self) -> Device:
        """Return Overkiz device linked to this entity."""
        return self.coordinator.data[self.device_url]

    def linked_device(self, index) -> Device:
        """Return Overkiz device sharing the same base url."""
        return self.coordinator.data[f"{self.base_device_url}#{index}"]

    def select_command(self, *commands: str) -> str | None:
        """Select first existing command in a list of commands."""
        existing_commands = self.device.definition.commands
        return next((c for c in commands if c in existing_commands), None)

    def has_command(self, *commands: str) -> bool:
        """Return True if a command exists in a list of commands."""
        return self.select_command(*commands) is not None

    def select_state(self, *states) -> str | None:
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

    def select_attribute(self, *attributes) -> str | None:
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
                self.device.device_url,
                Command(command_name, list(args)),
                "Home Assistant",
            )
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error(exception)
            return

        # ExecutionRegisteredEvent doesn't contain the device_url, thus we need to register it here
        self.coordinator.executions[exec_id] = {
            "device_url": self.device.device_url,
            "command_name": command_name,
        }

        await self.coordinator.async_refresh()

    async def async_cancel_command(self, commands_to_cancel: list[str]) -> bool:
        """Cancel running execution by command."""

        # Cancel a running execution
        # Retrieve executions initiated via Home Assistant from Data Update Coordinator queue
        exec_id = next(
            (
                exec_id
                # Reverse dictionary to cancel the last added execution
                for exec_id, execution in reversed(self.coordinator.executions.items())
                if execution.get("device_url") == self.device.device_url
                and execution.get("command_name") in commands_to_cancel
            ),
            None,
        )

        if exec_id:
            await self.async_cancel_execution(exec_id)
            return True

        # Retrieve executions initiated outside Home Assistant via API
        executions = await self.coordinator.client.get_current_executions()
        exec_id = next(
            (
                execution.id
                for execution in executions
                # Reverse dictionary to cancel the last added execution
                for action in reversed(execution.action_group.get("actions"))
                for command in action.get("commands")
                if action.get("device_url") == self.device.device_url
                and command.get("name") in commands_to_cancel
            ),
            None,
        )

        if exec_id:
            await self.async_cancel_execution(exec_id)
            return True

        return False

    async def async_cancel_execution(self, exec_id: str):
        """Cancel running execution via execution id."""
        await self.coordinator.client.cancel_command(exec_id)

    def get_gateway_id(self):
        """
        Retrieve gateway id from device url.

        device URL (<protocol>://<gatewayId>/<deviceAddress>[#<subsystemId>])
        """
        url = urlparse(self.device_url)
        return url.netloc
