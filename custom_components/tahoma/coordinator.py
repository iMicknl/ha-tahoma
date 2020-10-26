"""Helpers to help coordinate updates."""
from datetime import timedelta
import logging
from typing import Dict, List, Optional, Union

from aiohttp import ServerDisconnectedError
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pyhoma.client import TahomaClient
from pyhoma.enums import EventName, ExecutionState
from pyhoma.exceptions import (
    BadCredentialsException,
    MaintenanceException,
    NotAuthenticatedException,
    TooManyRequestsException,
)
from pyhoma.models import DataType, Device, State

TYPES = {
    DataType.NONE: None,
    DataType.INTEGER: int,
    DataType.DATE: int,
    DataType.STRING: str,
    DataType.FLOAT: float,
    DataType.BOOLEAN: bool,
}

_LOGGER = logging.getLogger(__name__)


class TahomaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching TaHoma data."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        *,
        name: str,
        client: TahomaClient,
        devices: List[Device],
        update_interval: Optional[timedelta] = None,
    ):
        """Initialize global data updater."""
        super().__init__(
            hass,
            logger,
            name=name,
            update_interval=update_interval,
        )

        self.data = {}
        self.original_update_interval = update_interval
        self.client = client
        self.devices: Dict[str, Device] = {d.deviceurl: d for d in devices}
        self.executions: Dict[str, Dict[str, str]] = {}

        _LOGGER.debug(
            "Initialized DataUpdateCoordinator with %s interval.", str(update_interval)
        )

    async def _async_update_data(self) -> Dict[str, Device]:
        """Fetch TaHoma data via event listener."""
        try:
            events = await self.client.fetch_events()
        except BadCredentialsException as exception:
            raise UpdateFailed("invalid_auth") from exception
        except TooManyRequestsException as exception:
            raise UpdateFailed("too_many_requests") from exception
        except MaintenanceException as exception:
            raise UpdateFailed("server_in_maintenance") from exception
        except (ServerDisconnectedError, NotAuthenticatedException) as exception:
            _LOGGER.debug(exception)
            self.executions = {}
            await self.client.login()
            self.devices = await self._get_devices()
            return self.devices
        except Exception as exception:
            _LOGGER.debug(exception)
            raise UpdateFailed(exception) from exception

        for event in events:
            _LOGGER.debug(
                "%s/%s (device: %s, state: %s -> %s)",
                event.name,
                event.exec_id,
                event.deviceurl,
                event.old_state,
                event.new_state,
            )

            if event.name == EventName.DEVICE_AVAILABLE:
                self.devices[event.deviceurl].available = True

            elif event.name in [
                EventName.DEVICE_UNAVAILABLE,
                EventName.DEVICE_DISABLED,
            ]:
                self.devices[event.deviceurl].available = False

            elif event.name in [
                EventName.DEVICE_CREATED,
                EventName.DEVICE_UPDATED,
            ]:
                self.devices = await self._get_devices()

            elif event.name == EventName.DEVICE_REMOVED:
                registry = await device_registry.async_get_registry(self.hass)
                registry.async_remove_device(event.deviceurl)
                del self.devices[event.deviceurl]

            elif event.name == EventName.DEVICE_STATE_CHANGED:
                for state in event.device_states:
                    device = self.devices[event.deviceurl]
                    if state.name not in device.states:
                        device.states[state.name] = state
                    device.states[state.name].value = self._get_state(state)

            elif event.name == EventName.EXECUTION_REGISTERED:
                if event.exec_id not in self.executions:
                    self.executions[event.exec_id] = {}

                self.update_interval = timedelta(seconds=1)

            elif (
                event.name == EventName.EXECUTION_STATE_CHANGED
                and event.exec_id in self.executions
                and event.new_state in [ExecutionState.COMPLETED, ExecutionState.FAILED]
            ):
                del self.executions[event.exec_id]

        if not self.executions:
            self.update_interval = self.original_update_interval

        return self.devices

    async def _get_devices(self) -> Dict[str, Device]:
        """Fetch devices."""
        _LOGGER.debug("Fetching all devices and state via /setup/devices")
        return {d.deviceurl: d for d in await self.client.get_devices(refresh=True)}

    @staticmethod
    def _get_state(state: State) -> Union[float, int, bool, str, None]:
        """Cast string value to the right type."""
        if state.type != DataType.NONE:
            caster = TYPES.get(DataType(state.type))
            return caster(state.value)
        return state.value
