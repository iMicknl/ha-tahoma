"""Support for Overkiz switches."""
from typing import Any

from homeassistant.components.cover import DOMAIN as COVER
from homeassistant.components.switch import (
    DEVICE_CLASS_SWITCH,
    DOMAIN as SWITCH,
    SwitchEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import COMMAND_OFF, COMMAND_ON, CORE_ON_OFF_STATE, DOMAIN
from .coordinator import OverkizDataUpdateCoordinator
from .cover_devices.tahoma_cover import COMMAND_SET_CLOSURE_AND_LINEAR_SPEED
from .entity import OverkizEntity

COMMAND_CYCLE = "cycle"
COMMAND_SET_FORCE_HEATING = "setForceHeating"
COMMAND_STANDARD = "standard"

IO_FORCE_HEATING_STATE = "io:ForceHeatingState"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Overkiz switch from a config entry."""
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

    _attr_device_class = DEVICE_CLASS_SWITCH

    async def async_turn_on(self, **_):
        """Send the on command."""
        if self.executor.has_command(COMMAND_ON):
            await self.executor.async_execute_command(COMMAND_ON)
        elif self.executor.has_command(COMMAND_SET_FORCE_HEATING):
            await self.executor.async_execute_command(
                COMMAND_SET_FORCE_HEATING, STATE_ON
            )

    async def async_turn_off(self, **_):
        """Send the off command."""
        if self.executor.has_command(COMMAND_OFF):
            await self.executor.async_execute_command(COMMAND_OFF)
        elif self.executor.has_command(COMMAND_SET_FORCE_HEATING):
            await self.executor.async_execute_command(
                COMMAND_SET_FORCE_HEATING, STATE_OFF
            )

    async def async_toggle(self, **_):
        """Click the switch."""
        if self.executor.has_command(COMMAND_CYCLE):
            await self.executor.async_execute_command(COMMAND_CYCLE)

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return (
            self.executor.select_state(CORE_ON_OFF_STATE, IO_FORCE_HEATING_STATE)
            == STATE_ON
        )


class OverkizLowSpeedCoverSwitch(OverkizEntity, SwitchEntity, RestoreEntity):
    """Representation of Low Speed Switch."""

    _attr_icon = "mdi:feather"

    def __init__(self, device_url: str, coordinator: OverkizDataUpdateCoordinator):
        """Initialize the low speed switch."""
        super().__init__(device_url, coordinator)
        self._is_on = False
        self._attr_name = f"{super().name} low speed"

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        if state:
            self._is_on = state.state == STATE_ON

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
