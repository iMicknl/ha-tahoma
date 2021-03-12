"""Support for TaHoma sensors."""

from dataclasses import dataclass
from typing import Any, Callable, Optional, Union

from homeassistant.components import sensor
from homeassistant.const import PERCENTAGE, SIGNAL_STRENGTH_DECIBELS
from homeassistant.helpers.entity import Entity

from .coordinator import TahomaDataUpdateCoordinator
from .tahoma_entity import TahomaEntity


@dataclass
class StateDescription:
    """Class to describe a sensor."""

    key: str
    name: str
    icon: Optional[str] = None
    unit: Union[None, str, Callable[[dict], str]] = None
    value: Callable[[Any], Any] = lambda val: val
    device_class: Optional[str] = None
    default_enabled: bool = True


supported_states = {
    "core:BatteryState": StateDescription(
        key="core:BatteryState",
        name="Battery",
        unit=PERCENTAGE,
        device_class=sensor.DEVICE_CLASS_BATTERY,
    ),
    "core:RSSILevelState": StateDescription(
        key="core:RSSILevelState",
        name="RSSI Level",
        value=lambda value: round(value),
        unit=SIGNAL_STRENGTH_DECIBELS,
        device_class=sensor.DEVICE_CLASS_SIGNAL_STRENGTH,
    ),
    "core:ExpectedNumberOfShowerState": StateDescription(
        key="core:ExpectedNumberOfShowerState",
        name="Expected Number Of Shower",
        icon="mdi-shower-head",
        value=lambda value: round(value),
    ),
}


class TahomaStateSensor(TahomaEntity, Entity):
    """Representation of a TaHoma Sensor, based on a secondary device."""

    def __init__(
        self,
        device_url: str,
        coordinator: TahomaDataUpdateCoordinator,
        state_description: StateDescription,
    ):
        """Initialize the device."""
        super().__init__(device_url, coordinator)
        self._state_description = state_description

    @property
    def state(self):
        """Return the value of the sensor."""
        state = self.select_state(self._state_description.key)

        return self._state_description.value(state) if state is not None else None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._state_description.unit

    @property
    def name(self) -> str:
        """Return the name of the device."""
        return self._state_description.name

    @property
    def icon(self) -> Optional[str]:
        """Return the icon to use in the frontend, if any."""
        return self._state_description.icon

    @property
    def device_class(self) -> Optional[str]:
        """Return the device class of this entity if any."""
        return self._state_description.device_class

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return self._state_description.default_enabled

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{super().unique_id}-{self._state_description.key}"
