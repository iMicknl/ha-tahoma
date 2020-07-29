"""Helpers to help coordinate updates."""
from datetime import timedelta
import logging
from typing import Dict, List, Optional, Union

from pyhoma.client import TahomaClient
from pyhoma.models import DataType, Device, State

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

TYPES = {
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
        self.listener_id = listener_id

    async def _async_update_data(self) -> Dict[str, Device]:
        """Fetch data from Tahoma."""
        try:
            events = await self.client.fetch_event_listener(self.listener_id)
        except Exception as exception:
            raise UpdateFailed(f"Error communicating with the TaHoma API: {exception}")
        else:
            for event in events:
                if event.name == "DeviceStateChangedEvent":
                    for state in event.device_states:
                        device = self.devices[event.deviceurl]
                        device.states[state.name].value = self._get_state(state)
            return self.devices

    @staticmethod
    def _get_state(state: State) -> Union[float, int, bool, str]:
        if state.type:
            caster = TYPES.get(DataType(state.type))
            return caster(state.value)
        return state.value
