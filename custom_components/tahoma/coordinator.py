from datetime import timedelta
import logging
from typing import Awaitable, Callable, Dict, List, Optional

from tahoma_api.client import TahomaClient
from tahoma_api.models import Device

from homeassistant.core import HomeAssistant
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator


class TahomaDataUpdateCoordinator(DataUpdateCoordinator):
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

        super().__init__(
            hass, logger, name=name, update_interval=update_interval,
        )

        self.client = client
        self.devices: Dict[str, Device] = {d.deviceurl: d for d in devices}
        self.listener_id = listener_id

    async def _async_update_data(self) -> Dict[str, Device]:
        """Fetch data from Tahoma."""
        events = await self.client.fetch_event_listener(self.listener_id)
        for event in events:
            if event.name == "DeviceStateChangedEvent":
                for state in event.device_states:
                    self.devices[event.deviceurl].states[state.name].value = state.value
        return self.devices
