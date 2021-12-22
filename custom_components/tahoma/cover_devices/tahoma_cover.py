"""Base class for TaHoma covers, shutters, awnings, etc."""
from homeassistant.components.cover import (
    ATTR_POSITION,
    ATTR_TILT_POSITION,
    SUPPORT_CLOSE_TILT,
    SUPPORT_OPEN_TILT,
    SUPPORT_SET_TILT_POSITION,
    SUPPORT_STOP_TILT,
    CoverEntity,
)
from pyoverkiz.enums import OverkizCommand, OverkizCommandParam, OverkizState

from ..entity import OverkizEntity

ATTR_OBSTRUCTION_DETECTED = "obstruction-detected"

COMMANDS_STOP = [OverkizCommand.STOP, OverkizCommand.STOP_IDENTIFY, OverkizCommand.MY]
COMMANDS_STOP_TILT = [
    OverkizCommand.STOP,
    OverkizCommand.STOP_IDENTIFY,
    OverkizCommand.MY,
]
COMMANDS_OPEN = [OverkizCommand.OPEN, OverkizCommand.UP, OverkizCommand.CYCLE]
COMMANDS_OPEN_TILT = [OverkizCommand.OPEN_SLATS]
COMMANDS_CLOSE = [OverkizCommand.CLOSE, OverkizCommand.DOWN, OverkizCommand.CYCLE]
COMMANDS_CLOSE_TILT = [OverkizCommand.CLOSE_SLATS]

COMMANDS_SET_TILT_POSITION = [OverkizCommand.SET_ORIENTATION]

SERVICE_COVER_POSITION_LOW_SPEED = "set_cover_position_low_speed"

SUPPORT_COVER_POSITION_LOW_SPEED = 1024


class OverkizGenericCover(OverkizEntity, CoverEntity):
    """Representation of a TaHoma Cover."""

    @property
    def current_cover_tilt_position(self):
        """Return current position of cover tilt.

        None is unknown, 0 is closed, 100 is fully open.
        """
        position = self.executor.select_state(
            OverkizState.CORE_SLATS_ORIENTATION, OverkizState.CORE_SLATE_ORIENTATION
        )
        return 100 - position if position is not None else None

    async def async_set_cover_position_low_speed(self, **kwargs):
        """Move the cover to a specific position with a low speed."""
        position = 100 - kwargs.get(ATTR_POSITION, 0)

        await self.executor.async_execute_command(
            OverkizCommand.SET_CLOSURE_AND_LINEAR_SPEED, position, "lowspeed"
        )

    async def async_set_cover_tilt_position(self, **kwargs):
        """Move the cover tilt to a specific position."""
        await self.executor.async_execute_command(
            self.executor.select_command(*COMMANDS_SET_TILT_POSITION),
            100 - kwargs.get(ATTR_TILT_POSITION, 0),
        )

    @property
    def is_closed(self):
        """Return if the cover is closed."""

        state = self.executor.select_state(
            OverkizState.CORE_OPEN_CLOSED,
            OverkizState.CORE_SLATS_OPEN_CLOSED,
            OverkizState.CORE_OPEN_CLOSED_PARTIAL,
            OverkizState.CORE_OPEN_CLOSED_PEDESTRIAN,
            OverkizState.CORE_OPEN_CLOSED_UNKNOWN,
            OverkizState.MYFOX_SHUTTER_STATUS,
        )
        if state is not None:
            return state == OverkizCommandParam.CLOSED

        # Keep this condition after the previous one.  Some device like the pedestrian gate, always return 50 as position.
        if self.current_cover_position is not None:
            return self.current_cover_position == 0

        if self.current_cover_tilt_position is not None:
            return self.current_cover_tilt_position == 0

        return None

    async def async_open_cover_tilt(self, **_):
        """Open the cover tilt."""
        await self.executor.async_execute_command(
            self.executor.select_command(*COMMANDS_OPEN_TILT)
        )

    async def async_close_cover_tilt(self, **_):
        """Close the cover tilt."""
        await self.executor.async_execute_command(
            self.executor.select_command(*COMMANDS_CLOSE_TILT)
        )

    async def async_stop_cover(self, **_):
        """Stop the cover."""
        await self.async_cancel_or_stop_cover(
            COMMANDS_OPEN + [OverkizCommand.SET_CLOSURE] + COMMANDS_CLOSE,
            COMMANDS_STOP,
        )

    async def async_stop_cover_tilt(self, **_):
        """Stop the cover tilt."""
        await self.executor.async_cancel_or_stop_cover(
            COMMANDS_OPEN_TILT + COMMANDS_SET_TILT_POSITION + COMMANDS_CLOSE_TILT,
            COMMANDS_STOP_TILT,
        )

    async def async_cancel_or_stop_cover(self, cancel_commands, stop_commands) -> None:
        """Cancel running execution or send stop command."""
        success = await self.executor.async_cancel_command(cancel_commands)

        if not success:
            # Fallback to available stop commands when no executions are found
            # Stop commands don't work with all devices, due to a bug in Somfy service
            await self.executor.async_execute_command(
                self.executor.select_command(*stop_commands)
            )

    @property
    def is_opening(self):
        """Return if the cover is opening or not."""

        if self.assumed_state:
            return None

        if any(
            execution.get("device_url") == self.device.device_url
            and execution.get("command_name") in COMMANDS_OPEN + COMMANDS_OPEN_TILT
            for execution in self.coordinator.executions.values()
        ):
            return True

        is_moving = self.device.states.get(OverkizState.CORE_MOVING)
        current_closure = self.device.states.get(OverkizState.CORE_CLOSURE)
        target_closure = self.device.states.get(OverkizState.CORE_TARGET_CLOSURE)
        return (
            is_moving
            and is_moving.value
            and current_closure
            and target_closure
            and current_closure.value > target_closure.value
        )

    @property
    def is_closing(self):
        """Return if the cover is closing or not."""

        if self.assumed_state:
            return None

        if any(
            execution.get("device_url") == self.device.device_url
            and execution.get("command_name") in COMMANDS_CLOSE + COMMANDS_CLOSE_TILT
            for execution in self.coordinator.executions.values()
        ):
            return True

        is_moving = self.device.states.get(OverkizState.CORE_MOVING)
        current_closure = self.device.states.get(OverkizState.CORE_CLOSURE)
        target_closure = self.device.states.get(OverkizState.CORE_TARGET_CLOSURE)
        return (
            is_moving
            and is_moving.value
            and current_closure
            and target_closure
            and current_closure.value < target_closure.value
        )

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        attr = super().extra_state_attributes or {}

        # Obstruction Detected attribute is used by HomeKit
        if self.executor.has_state(OverkizState.IO_PRIORITY_LOCK_LEVEL):
            attr[ATTR_OBSTRUCTION_DETECTED] = True

        return attr

    @property
    def supported_features(self):
        """Flag supported features."""
        supported_features = 0

        if self.executor.has_command(*COMMANDS_OPEN_TILT):
            supported_features |= SUPPORT_OPEN_TILT

            if self.executor.has_command(*COMMANDS_STOP_TILT):
                supported_features |= SUPPORT_STOP_TILT

        if self.executor.has_command(*COMMANDS_CLOSE_TILT):
            supported_features |= SUPPORT_CLOSE_TILT

        if self.executor.has_command(*COMMANDS_SET_TILT_POSITION):
            supported_features |= SUPPORT_SET_TILT_POSITION

        if self.executor.has_command(OverkizCommand.SET_CLOSURE_AND_LINEAR_SPEED):
            supported_features |= SUPPORT_COVER_POSITION_LOW_SPEED

        return supported_features
