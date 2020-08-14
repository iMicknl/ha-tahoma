"""Helpers to help coordinate updates."""
from collections import defaultdict
from datetime import timedelta
import logging
from typing import Dict, List, Optional, Union

from pyhoma.client import TahomaClient
from pyhoma.models import DataType, Device, State

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_UPDATE_INTERVAL

TYPES = {
    DataType.NONE: None,
    DataType.INTEGER: int,
    DataType.DATE: int,
    DataType.STRING: str,
    DataType.FLOAT: float,
    DataType.BOOLEAN: bool,
}


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
        listener_id: str,
        update_interval: Optional[timedelta] = None,
    ):
        """Initialize global data updater."""
        super().__init__(
            hass, logger, name=name, update_interval=update_interval,
        )

        self.client = client
        self.devices: Dict[str, Device] = {d.deviceurl: d for d in devices}
        self.executions: Dict[str, defaultdict] = {}
        self.listener_id = listener_id

    async def _async_update_data(self) -> Dict[str, Device]:
        """Fetch data from Tahoma."""
        try:
            events = await self.client.fetch_event_listener(self.listener_id)
        except Exception as exception:
            raise UpdateFailed(f"Error communicating with the TaHoma API: {exception}")
        else:
            for event in events:
                print(f"{event.name} {event.exec_id} {event.deviceurl}")

                if event.name == "DeviceAvailableEvent":
                    print(event.deviceurl)

                if event.name == "DeviceStateChangedEvent":
                    for state in event.device_states:
                        device = self.devices[event.deviceurl]
                        if state.name not in device.states:
                            device.states[state.name] = state
                        device.states[state.name].value = self._get_state(state)

                if event.name == "ExecutionRegisteredEvent":
                    self.update_interval = timedelta(seconds=1)

                if (
                    event.name == "ExecutionStateChangedEvent"
                    and event.exec_id in self.executions
                ) and event.new_state == "COMPLETED":
                    self.executions.pop(event.exec_id, None)

            if len(self.executions) < 1:
                self.update_interval = DEFAULT_UPDATE_INTERVAL

            return self.devices

    @staticmethod
    def _get_state(state: State) -> Union[float, int, bool, str, None]:
        """Cast string value to the right type."""
        if state.type != DataType.NONE:
            caster = TYPES.get(DataType(state.type))
            return caster(state.value)
        return state.value
