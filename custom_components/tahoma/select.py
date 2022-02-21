"""Support for Overkiz select."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from pyoverkiz.enums import OverkizCommand, OverkizCommandParam, OverkizState

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HomeAssistantOverkizData
from .const import DOMAIN, IGNORED_OVERKIZ_DEVICES
from .entity import OverkizDescriptiveEntity, OverkizDeviceClass


@dataclass
class OverkizSelectDescriptionMixin:
    """Define an entity description mixin for select entities."""

    options: list[str | OverkizCommandParam]
    select_option: Callable[[str, Callable[..., Awaitable[None]]], Awaitable[None]]


@dataclass
class OverkizSelectDescription(SelectEntityDescription, OverkizSelectDescriptionMixin):
    """Class to describe an Overkiz select entity."""


def _select_option_open_closed_pedestrian(
    option: str, execute_command: Callable[..., Awaitable[None]]
) -> Awaitable[None]:
    """Change the selected option for Open/Closed/Pedestrian."""
    return execute_command(
        {
            OverkizCommandParam.CLOSED: OverkizCommand.CLOSE,
            OverkizCommandParam.OPEN: OverkizCommand.OPEN,
            OverkizCommandParam.PEDESTRIAN: OverkizCommand.SET_PEDESTRIAN_POSITION,
        }[OverkizCommandParam(option)],
        None,
    )


def _select_option_memorized_simple_volume(
    option: str, execute_command: Callable[..., Awaitable[None]]
) -> Awaitable[None]:
    """Change the selected option for Memorized Simple Volume."""
    return execute_command(OverkizCommand.SET_MEMORIZED_SIMPLE_VOLUME, option)


SELECT_DESCRIPTIONS: list[OverkizSelectDescription] = [
    OverkizSelectDescription(
        key=OverkizState.CORE_OPEN_CLOSED_PEDESTRIAN,
        name="Position",
        icon="mdi:content-save-cog",
        options=[
            OverkizCommandParam.OPEN,
            OverkizCommandParam.PEDESTRIAN,
            OverkizCommandParam.CLOSED,
        ],
        select_option=_select_option_open_closed_pedestrian,
        device_class=OverkizDeviceClass.OPEN_CLOSED_PEDESTRIAN,
    ),
    OverkizSelectDescription(
        key=OverkizState.IO_MEMORIZED_SIMPLE_VOLUME,
        name="Memorized Simple Volume",
        icon="mdi:volume-high",
        options=[OverkizCommandParam.STANDARD, OverkizCommandParam.HIGHEST],
        select_option=_select_option_memorized_simple_volume,
        entity_category=EntityCategory.CONFIG,
        device_class=OverkizDeviceClass.MEMORIZED_SIMPLE_VOLUME,
    ),
    # SomfyHeatingTemperatureInterface
    OverkizSelectDescription(
        key=OverkizState.OVP_HEATING_TEMPERATURE_INTERFACE_OPERATING_MODE,
        name="Operating Mode",
        icon="mdi:sun-snowflake",
        options=[OverkizCommandParam.HEATING, OverkizCommandParam.COOLING],
        select_option=lambda option, execute_command: execute_command(
            OverkizCommand.SET_OPERATING_MODE, option
        ),
        entity_category=EntityCategory.CONFIG,
    ),
]

SUPPORTED_STATES = {description.key: description for description in SELECT_DESCRIPTIONS}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Overkiz select from a config entry."""
    data: HomeAssistantOverkizData = hass.data[DOMAIN][entry.entry_id]
    entities: list[OverkizSelect] = []

    for device in data.coordinator.data.values():
        if (
            device.widget in IGNORED_OVERKIZ_DEVICES
            or device.ui_class in IGNORED_OVERKIZ_DEVICES
        ):
            continue

        for state in device.definition.states:
            if description := SUPPORTED_STATES.get(state.qualified_name):
                entities.append(
                    OverkizSelect(
                        device.device_url,
                        data.coordinator,
                        description,
                    )
                )

    async_add_entities(entities)


class OverkizSelect(OverkizDescriptiveEntity, SelectEntity):
    """Representation of an Overkiz Select entity."""

    entity_description: OverkizSelectDescription

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        if state := self.device.states.get(self.entity_description.key):
            return str(state.value)

        return None

    @property
    def options(self) -> list[str]:
        """Return a set of selectable options."""
        return self.entity_description.options

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.entity_description.select_option(
            option, self.executor.async_execute_command
        )
