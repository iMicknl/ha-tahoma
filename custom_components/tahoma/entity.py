"""Parent class for every Overkiz device."""
from __future__ import annotations

from enum import unique
from typing import cast

from pyoverkiz.enums import OverkizAttribute, OverkizState
from pyoverkiz.models import Device

from homeassistant.backports.enum import StrEnum
from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import OverkizDataUpdateCoordinator
from .executor import OverkizExecutor


class OverkizEntity(CoordinatorEntity):
    """Representation of an Overkiz device entity."""

    coordinator: OverkizDataUpdateCoordinator

    def __init__(
        self, device_url: str, coordinator: OverkizDataUpdateCoordinator
    ) -> None:
        """Initialize the device."""
        super().__init__(coordinator)
        self.device_url = device_url
        self.base_device_url, *_ = self.device_url.split("#")
        self.executor = OverkizExecutor(device_url, coordinator)

        self._attr_assumed_state = not self.device.states
        self._attr_available = self.device.available
        self._attr_unique_id = self.device.device_url
        self._attr_name = self.device.label

        self._attr_device_info = self.generate_device_info()

    @property
    def device(self) -> Device:
        """Return Overkiz device linked to this entity."""
        return self.coordinator.data[self.device_url]

    def generate_device_info(self) -> DeviceInfo:
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
            self.executor.select_attribute(OverkizAttribute.CORE_MANUFACTURER)
            or self.executor.select_state(OverkizState.CORE_MANUFACTURER_NAME)
            or self.coordinator.client.server.manufacturer
        )

        model = (
            self.executor.select_state(
                OverkizState.CORE_MODEL,
                OverkizState.CORE_PRODUCT_MODEL_NAME,
                OverkizState.IO_MODEL,
            )
            or self.device.widget.value
        )

        return DeviceInfo(
            identifiers={(DOMAIN, self.executor.base_device_url)},
            name=self.device.label,
            manufacturer=str(manufacturer),
            model=str(model),
            sw_version=cast(
                str,
                self.executor.select_attribute(OverkizAttribute.CORE_FIRMWARE_REVISION),
            ),
            hw_version=self.device.controllable_name,
            suggested_area=self.coordinator.areas[self.device.place_oid],
            via_device=(DOMAIN, self.executor.get_gateway_id()),
            configuration_url=self.coordinator.client.server.configuration_url,
        )


class OverkizDescriptiveEntity(OverkizEntity):
    """Representation of a Overkiz device entity based on a description."""

    def __init__(
        self,
        device_url: str,
        coordinator: OverkizDataUpdateCoordinator,
        description: EntityDescription,
    ) -> None:
        """Initialize the device."""
        super().__init__(device_url, coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{super().unique_id}-{self.entity_description.key}"

        if self.entity_description.name:
            self._attr_name = f"{super().name} {self.entity_description.name}"


# Used by state translations for sensor and select entities
@unique
class OverkizDeviceClass(StrEnum):
    """Device class for Overkiz specific devices."""

    BATTERY = "overkiz__battery"
    DISCRETE_RSSI_LEVEL = "overkiz__discrete_rssi_level"
    MEMORIZED_SIMPLE_VOLUME = "overkiz__memorized_simple_volume"
    OPEN_CLOSED_PEDESTRIAN = "overkiz__open_closed_pedestrian"
    PRIORITY_LOCK_ORIGINATOR = "overkiz__priority_lock_originator"
    SENSOR_DEFECT = "overkiz__sensor_defect"
    SENSOR_ROOM = "overkiz__sensor_room"
