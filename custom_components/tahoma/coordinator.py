"""Helpers to help coordinate updates."""
from datetime import timedelta
import logging
from typing import Dict, List, Optional, Union

from aiohttp import ServerDisconnectedError
from pyhoma.client import TahomaClient
from pyhoma.exceptions import NotAuthenticatedException
from pyhoma.models import DataType, Device, State

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

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
            hass, logger, name=name, update_interval=update_interval,
        )

        self.original_update_interval = update_interval
        self.client = client
        self.devices: Dict[str, Device] = {d.deviceurl: d for d in devices}
        self.executions: Dict[str, Dict[str, str]] = {}

    async def _async_update_data(self) -> Dict[str, Device]:
        """Fetch TaHoma data via event listener."""
        try:
            events = await self.client.fetch_events()
        except (ServerDisconnectedError, NotAuthenticatedException) as exception:
            _LOGGER.debug(exception)
            self.executions = {}
            await self.client.login()
            self.devices = {
                d.deviceurl: d for d in await self.client.get_devices(refresh=True)
            }
            return self.devices
        except Exception as exception:
            raise UpdateFailed(exception)

        for event in events:
            _LOGGER.debug(
                f"{event.name}/{event.exec_id} (device:{event.deviceurl},state:{event.old_state}->{event.new_state})"
            )

            if event.name == "DeviceAvailableEvent":
                self.devices[event.deviceurl].available = True

            elif event.name == "DeviceUnavailableEvent":
                self.devices[event.deviceurl].available = False

            elif event.name == "DeviceStateChangedEvent":
                for state in event.device_states:
                    device = self.devices[event.deviceurl]
                    if state.name not in device.states:
                        device.states[state.name] = state
                    device.states[state.name].value = self._get_state(state)

            if event.name == "ExecutionRegisteredEvent":
                if event.exec_id not in self.executions:
                    self.executions[event.exec_id] = {}

                self.update_interval = timedelta(seconds=1)

            if (
                event.name == "ExecutionStateChangedEvent"
                and event.exec_id in self.executions
                and event.new_state in ["COMPLETED", "FAILED"]
            ):
                del self.executions[event.exec_id]

        if not self.executions:
            self.update_interval = self.original_update_interval

        return self.devices

    @staticmethod
    def _get_state(state: State) -> Union[float, int, bool, str, None]:
        """Cast string value to the right type."""
        if state.type != DataType.NONE:
            caster = TYPES.get(DataType(state.type))
            return caster(state.value)
        return state.value
