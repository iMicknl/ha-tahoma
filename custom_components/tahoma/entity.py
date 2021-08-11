"""Parent class for every Overkiz device."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Callable

from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.const import ATTR_BATTERY_LEVEL
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from pyhoma.models import Device

from .const import DOMAIN
from .coordinator import TahomaDataUpdateCoordinator
from .executor import OverkizExecutor

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


class OverkizEntity(CoordinatorEntity, Entity):
    """Representation of a Overkiz device entity."""

    def __init__(self, device_url: str, coordinator: TahomaDataUpdateCoordinator):
        """Initialize the device."""
        super().__init__(coordinator)
        self.device_url = device_url
        self.base_device_url, *_ = self.device_url.split("#")
        self.executor = OverkizExecutor(device_url, coordinator)

    @property
    def device(self) -> Device:
        """Return Overkiz device linked to this entity."""
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
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""
        # Some devices, such as the Smart Thermostat have several devices in one physical device,
        # with same device url, terminated by '#' and a number.
        # In this case, we use the base device url as the device identifier.
        if "#" in self.device_url and not self.device_url.endswith("#1"):
            # Only return the url of the base device, to inherit device name and model from parent device.
            return {
                "identifiers": {(DOMAIN, self.executor.base_device_url)},
            }

        manufacturer = (
            self.executor.select_attribute(CORE_MANUFACTURER)
            or self.executor.select_state(CORE_MANUFACTURER_NAME_STATE)
            or "Somfy"
        )

        model = (
            self.executor.select_state(
                CORE_MODEL_STATE, CORE_PRODUCT_MODEL_NAME_STATE, IO_MODEL_STATE
            )
            or self.device.widget
        )

        return {
            "identifiers": {(DOMAIN, self.executor.base_device_url)},
            "manufacturer": manufacturer,
            "name": self.device.label,
            "model": model,
            "sw_version": self.device.controllable_name,
            "suggested_area": self.coordinator.areas[self.device.placeoid],
            "via_device": self.executor.get_gateway_id(),
        }

    @property
    def device_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the device."""
        attr = {}

        if self.executor.has_state(CORE_RSSI_LEVEL_STATE):
            attr[ATTR_RSSI_LEVEL] = self.executor.select_state(CORE_RSSI_LEVEL_STATE)

        if self.executor.has_state(CORE_BATTERY_STATE):
            battery_state = self.executor.select_state(CORE_BATTERY_STATE)
            attr[ATTR_BATTERY_LEVEL] = BATTERY_MAP.get(battery_state, battery_state)

        if self.executor.select_state(CORE_SENSOR_DEFECT_STATE) == STATE_DEAD:
            attr[ATTR_BATTERY_LEVEL] = 0

        if self.device.attributes:
            for attribute in self.device.attributes:
                attr[attribute.name] = attribute.value

        if self.device.states:
            for state in self.device.states:
                if "State" in state.name:
                    attr[state.name] = state.value

        return attr


@dataclass
class OverkizSensorDescription(SensorEntityDescription):
    """Class to describe an Overkiz sensor."""

    value: Callable[[str | int | float], str | int | float] | None = lambda val: val


@dataclass
class OverkizBinarySensorDescription(BinarySensorEntityDescription):
    """Class to describe an Overkiz binary sensor."""

    is_on: Callable[[str], bool] = lambda state: state


class OverkizDescriptiveEntity(OverkizEntity):
    """Representation of a Overkiz device entity based on a description."""

    def __init__(
        self,
        device_url: str,
        coordinator: TahomaDataUpdateCoordinator,
        description: OverkizSensorDescription | OverkizBinarySensorDescription,
    ):
        """Initialize the device."""
        super().__init__(device_url, coordinator)
        self.entity_description = description

    @property
    def name(self) -> str:
        """Return the name of the device."""
        return f"{super().name} {self.entity_description.name}"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{super().unique_id}-{self.entity_description.key}"
