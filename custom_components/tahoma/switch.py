"""Support for Overkiz switches."""
from typing import Any, Optional

from homeassistant.components.cover import DOMAIN as COVER
from homeassistant.components.switch import (
    DEVICE_CLASS_SWITCH,
    DOMAIN as SWITCH,
    SwitchEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ENTITY_CATEGORY_CONFIG
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, OverkizCommand, OverkizCommandParam, OverkizState
from .coordinator import OverkizDataUpdateCoordinator
from .cover_devices.tahoma_cover import COMMAND_SET_CLOSURE_AND_LINEAR_SPEED
from .entity import OverkizEntity

DEVICE_CLASS_SIREN = "siren"

ICON_BELL_RING = "mdi:bell-ring"
ICON_BELL_OFF = "mdi:bell-off"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Overkiz sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities = [
        OverkizSwitch(device.device_url, coordinator)
        for device in data["platforms"][SWITCH]
    ]

    entities.extend(
        [
            OverkizLowSpeedCoverSwitch(device.device_url, coordinator)
            for device in data["platforms"][COVER]
            if COMMAND_SET_CLOSURE_AND_LINEAR_SPEED in device.definition.commands
        ]
    )

    async_add_entities(entities)


class OverkizSwitch(OverkizEntity, SwitchEntity):
    """Representation an Overkiz Switch."""

    @property
    def device_class(self):
        """Return the class of the device."""
        if self.device.ui_class == "Siren":
            return DEVICE_CLASS_SIREN

        return DEVICE_CLASS_SWITCH

    @property
    def icon(self) -> Optional[str]:
        """Return the icon to use in the frontend, if any."""
        if self.device_class == DEVICE_CLASS_SIREN:
            if self.is_on:
                return ICON_BELL_RING
            return ICON_BELL_OFF

        return None

    async def async_turn_on(self, **_):
        """Send the on command."""
        if self.executor.has_command(OverkizCommand.ON):
            await self.executor.async_execute_command(OverkizCommand.ON)

        elif self.executor.has_command(OverkizCommand.SET_FORCE_HEATING):
            await self.executor.async_execute_command(
                OverkizCommand.SET_FORCE_HEATING, OverkizCommandParam.ON
            )

        elif self.executor.has_command(OverkizCommand.RING_WITH_SINGLE_SIMPLE_SEQUENCE):
            await self.executor.async_execute_command(
                OverkizCommand.RING_WITH_SINGLE_SIMPLE_SEQUENCE,  # https://www.tahomalink.com/enduser-mobile-web/steer-html5-client/vendor/somfy/io/siren/const.js
                2 * 60 * 1000,  # 2 minutes
                75,  # 90 seconds bip, 30 seconds silence
                2,  # repeat 3 times
                OverkizCommand.MEMORIZED_VOLUME,
            )

    async def async_turn_off(self, **_):
        """Send the off command."""
        if self.executor.has_command(OverkizCommand.RING_WITH_SINGLE_SIMPLE_SEQUENCE):
            await self.executor.async_execute_command(
                OverkizCommand.RING_WITH_SINGLE_SIMPLE_SEQUENCE,
                2000,
                100,
                0,
                OverkizCommand.STANDARD,
            )

        elif self.executor.has_command(OverkizCommand.SET_FORCE_HEATING):
            await self.executor.async_execute_command(
                OverkizCommand.SET_FORCE_HEATING, OverkizCommandParam.OFF
            )

        elif self.executor.has_command(OverkizCommand.OFF):
            await self.executor.async_execute_command(OverkizCommand.OFF)

    async def async_toggle(self, **_):
        """Click the switch."""
        if self.executor.has_command(OverkizCommand.CYCLE):
            await self.executor.async_execute_command(OverkizCommand.CYCLE)

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return (
            self.executor.select_state(
                OverkizState.CORE_ON_OFF, OverkizState.IO_FORCE_HEATING_STATE
            )
            == OverkizCommandParam.ON
        )


class OverkizLowSpeedCoverSwitch(OverkizEntity, SwitchEntity, RestoreEntity):
    """Representation of Low Speed Switch."""

    _attr_icon = "mdi:feather"

    def __init__(self, device_url: str, coordinator: OverkizDataUpdateCoordinator):
        """Initialize the low speed switch."""
        super().__init__(device_url, coordinator)
        self._is_on = False
        self._attr_name = f"{super().name} low speed"
        self._attr_entity_category = ENTITY_CATEGORY_CONFIG

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        if state:
            self._is_on = state.state == OverkizCommandParam.ON

    @property
    def is_on(self) -> bool:
        """Get whether the switch is in on state."""
        return self._is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Send the on command."""
        self._is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Send the off command."""
        self._is_on = False
        self.async_write_ha_state()
