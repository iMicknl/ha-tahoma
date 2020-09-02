"""Support for TaHoma cover - shutters etc."""
import logging

import voluptuous as vol

from homeassistant.components.cover import (
    ATTR_POSITION,
    ATTR_TILT_POSITION,
    DEVICE_CLASS_AWNING,
    DEVICE_CLASS_BLIND,
    DEVICE_CLASS_CURTAIN,
    DEVICE_CLASS_GARAGE,
    DEVICE_CLASS_GATE,
    DEVICE_CLASS_SHUTTER,
    DEVICE_CLASS_WINDOW,
    DOMAIN as COVER,
    SUPPORT_CLOSE,
    SUPPORT_CLOSE_TILT,
    SUPPORT_OPEN,
    SUPPORT_OPEN_TILT,
    SUPPORT_SET_POSITION,
    SUPPORT_SET_TILT_POSITION,
    SUPPORT_STOP,
    SUPPORT_STOP_TILT,
    CoverEntity,
)
from homeassistant.helpers import entity_platform

from .const import DOMAIN
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

COMMAND_CYCLE = "cycle"
COMMAND_CLOSE = "close"
COMMAND_CLOSE_SLATS = "closeSlats"
COMMAND_DOWN = "down"
COMMAND_MY = "my"
COMMAND_OPEN = "open"
COMMAND_OPEN_SLATS = "openSlats"
COMMAND_SET_CLOSURE = "setClosure"
COMMAND_SET_ORIENTATION = "setOrientation"
COMMAND_SET_PEDESTRIAN_POSITION = "setPedestrianPosition"
COMMAND_SET_POSITION = "setPosition"
COMMAND_SET_POSITION_AND_LINEAR_SPEED = "setPositionAndLinearSpeed"
COMMAND_STOP = "stop"
COMMAND_STOP_IDENTIFY = "stopIdentify"
COMMAND_UP = "up"

CORE_CLOSURE_STATE = "core:ClosureState"
CORE_CLOSURE_OR_ROCKER_POSITION_STATE = "core:ClosureOrRockerPositionState"
CORE_DEPLOYMENT_STATE = "core:DeploymentState"
CORE_MEMORIZED_1_POSITION_STATE = "core:Memorized1PositionState"
CORE_OPEN_CLOSED_PARTIAL_STATE = "core:OpenClosedPartialState"
CORE_OPEN_CLOSED_PEDESTRIAN_STATE = "core:OpenClosedPedestrianState"
CORE_OPEN_CLOSED_STATE = "core:OpenClosedState"
CORE_OPEN_CLOSED_UNKNOWN_STATE = "core:OpenClosedUnknownState"
CORE_PEDESTRIAN_POSITION_STATE = "core:PedestrianPositionState"
CORE_PRIORITY_LOCK_TIMER_STATE = "core:PriorityLockTimerState"
CORE_SLATS_OPEN_CLOSED_STATE = "core:SlatsOpenClosedState"
CORE_SLATS_ORIENTATION_STATE = "core:SlatsOrientationState"
CORE_TARGET_CLOSURE_STATE = "core:TargetClosureState"
MYFOX_SHUTTER_STATUS_STATE = "myfox:ShutterStatusState"

ICON_LOCK_ALERT = "mdi:lock-alert"
ICON_WEATHER_WINDY = "mdi:weather-windy"

IO_PRIORITY_LOCK_ORIGINATOR_STATE = "io:PriorityLockOriginatorState"

STATE_CLOSED = "closed"

SERVICE_COVER_MY_POSITION = "set_cover_my_position"
SERVICE_COVER_POSITION_LOW_SPEED = "set_cover_position_low_speed"

SUPPORT_MY = 512
SUPPORT_COVER_POSITION_LOW_SPEED = 1024


TAHOMA_COVER_DEVICE_CLASSES = {
    "Awning": DEVICE_CLASS_AWNING,
    "Blind": DEVICE_CLASS_BLIND,
    "Curtain": DEVICE_CLASS_CURTAIN,
    "ExteriorScreen": DEVICE_CLASS_BLIND,
    "ExteriorVenetianBlind": DEVICE_CLASS_BLIND,
    "GarageDoor": DEVICE_CLASS_GARAGE,
    "Gate": DEVICE_CLASS_GATE,
    "MyFoxSecurityCamera": DEVICE_CLASS_SHUTTER,
    "Pergola": DEVICE_CLASS_AWNING,
    "RollerShutter": DEVICE_CLASS_SHUTTER,
    "SwingingShutter": DEVICE_CLASS_SHUTTER,
    "VeluxInteriorBlind": DEVICE_CLASS_BLIND,
    "Window": DEVICE_CLASS_WINDOW,
}


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma covers from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data.get("coordinator")

    entities = [
        TahomaCover(device.deviceurl, coordinator)
        for device in data.get("entities").get(COVER)
    ]

    async_add_entities(entities)

    platform = entity_platform.current_platform.get()
    platform.async_register_entity_service(
        SERVICE_COVER_MY_POSITION, {}, "async_my", [SUPPORT_MY]
    )

    platform.async_register_entity_service(
        SERVICE_COVER_POSITION_LOW_SPEED,
        {
            vol.Required(ATTR_POSITION): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=100)
            )
        },
        "async_set_cover_position_low_speed",
        [SUPPORT_COVER_POSITION_LOW_SPEED],
    )


class TahomaCover(TahomaDevice, CoverEntity):
    """Representation of a TaHoma Cover."""

    @property
    def current_cover_position(self):
        """
        Return current position of cover.

        None is unknown, 0 is closed, 100 is fully open.
        """
        position = self.select_state(
            CORE_CLOSURE_STATE,
            CORE_DEPLOYMENT_STATE,
            CORE_PEDESTRIAN_POSITION_STATE,
            CORE_TARGET_CLOSURE_STATE,
            CORE_CLOSURE_OR_ROCKER_POSITION_STATE,
        )

        # Uno devices can have a position not in 0 to 100 range when unknown
        if position is None or position < 0 or position > 100:
            return None

        if "Horizontal" not in self.device.widget:
            position = 100 - position

        return position

    @property
    def current_cover_tilt_position(self):
        """Return current position of cover tilt.

        None is unknown, 0 is closed, 100 is fully open.
        """
        position = self.select_state(CORE_SLATS_ORIENTATION_STATE)
        return 100 - position if position is not None else None

    async def async_set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = 100 - kwargs.get(ATTR_POSITION, 0)

        # HorizontalAwning devices need a reversed position that can not be obtained via the API
        if "Horizontal" in self.device.widget:
            position = kwargs.get(ATTR_POSITION, 0)

        command = self.select_command(
            COMMAND_SET_POSITION, COMMAND_SET_CLOSURE, COMMAND_SET_PEDESTRIAN_POSITION
        )
        await self.async_execute_command(command, position)

    async def async_set_cover_position_low_speed(self, **kwargs):
        """Move the cover to a specific position with a low speed."""
        position = 100 - kwargs.get(ATTR_POSITION, 0)

        # HorizontalAwning devices need a reversed position that can not be obtained via the API
        if "Horizontal" in self.device.widget:
            position = kwargs.get(ATTR_POSITION, 0)

        await self.async_execute_command(
            COMMAND_SET_POSITION_AND_LINEAR_SPEED, position, "lowspeed"
        )

    async def async_set_cover_tilt_position(self, **kwargs):
        """Move the cover tilt to a specific position."""
        await self.async_execute_command(
            COMMAND_SET_ORIENTATION, 100 - kwargs.get(ATTR_TILT_POSITION, 0)
        )

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        state = self.select_state(
            CORE_OPEN_CLOSED_STATE,
            CORE_SLATS_OPEN_CLOSED_STATE,
            CORE_OPEN_CLOSED_PARTIAL_STATE,
            CORE_OPEN_CLOSED_PEDESTRIAN_STATE,
            CORE_OPEN_CLOSED_UNKNOWN_STATE,
            MYFOX_SHUTTER_STATUS_STATE,
        )

        if state is not None:
            return state == STATE_CLOSED

        if self.current_cover_position is not None:
            return self.current_cover_position == 0

        if self.current_cover_tilt_position is not None:
            return self.current_cover_tilt_position == 0

        return None

    @property
    def device_class(self):
        """Return the class of the device."""
        return (
            TAHOMA_COVER_DEVICE_CLASSES.get(self.device.widget)
            or TAHOMA_COVER_DEVICE_CLASSES.get(self.device.ui_class)
            or DEVICE_CLASS_BLIND
        )

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        if (
            self.has_state(CORE_PRIORITY_LOCK_TIMER_STATE)
            and self.select_state(CORE_PRIORITY_LOCK_TIMER_STATE) > 0
        ):
            if self.select_state(IO_PRIORITY_LOCK_ORIGINATOR_STATE) == "wind":
                return ICON_WEATHER_WINDY
            else:
                return ICON_LOCK_ALERT

        return None

    async def async_open_cover(self, **_):
        """Open the cover."""
        await self.async_execute_command(
            self.select_command(COMMAND_OPEN, COMMAND_UP, COMMAND_CYCLE)
        )

    async def async_open_cover_tilt(self, **_):
        """Open the cover tilt."""
        await self.async_execute_command(self.select_command(COMMAND_OPEN_SLATS))

    async def async_close_cover(self, **_):
        """Close the cover."""
        await self.async_execute_command(
            self.select_command(COMMAND_CLOSE, COMMAND_DOWN, COMMAND_CYCLE)
        )

    async def async_close_cover_tilt(self, **_):
        """Close the cover tilt."""
        await self.async_execute_command(self.select_command(COMMAND_CLOSE_SLATS))

    async def async_stop_cover(self, **_):
        """Stop the cover."""
        exec_id = next(
            (
                exec_id
                for exec_id, execution in self.coordinator.executions.items()
                if execution.get("deviceurl") == self.device.deviceurl
                and execution.get("command_name")
                in [
                    COMMAND_OPEN,
                    COMMAND_UP,
                    COMMAND_CYCLE,
                    COMMAND_CLOSE,
                    COMMAND_DOWN,
                    COMMAND_SET_POSITION,
                    COMMAND_SET_CLOSURE,
                    COMMAND_SET_PEDESTRIAN_POSITION,
                    COMMAND_SET_POSITION_AND_LINEAR_SPEED,
                ]
            ),
            None,
        )

        if exec_id:
            self.debug("Cancelling command " + exec_id)
            await self.async_cancel_command(exec_id)
        else:
            self.debug("Calling stop command")
            await self.async_execute_command(
                self.select_command(COMMAND_STOP, COMMAND_STOP_IDENTIFY, COMMAND_MY)
            )

    async def async_stop_cover_tilt(self, **_):
        """Stop the cover tilt."""
        exec_id = next(
            (
                exec_id
                for exec_id, execution in self.coordinator.executions.items()
                if execution.get("deviceurl") == self.device.deviceurl
                and execution.get("command_name")
                in [COMMAND_OPEN_SLATS, COMMAND_CLOSE_SLATS, COMMAND_SET_ORIENTATION]
            ),
            None,
        )

        if exec_id:
            self.debug("Cancelling command " + exec_id)
            await self.async_cancel_command(exec_id)
        else:
            self.debug("Calling stop command")
            await self.async_execute_command(
                self.select_command(COMMAND_STOP_IDENTIFY, COMMAND_STOP, COMMAND_MY)
            )

    async def async_my(self, **_):
        """Set cover to preset position."""
        await self.async_execute_command(COMMAND_MY)

    @property
    def is_opening(self):
        """Return if the cover is opening or not."""
        return any(
            execution.get("deviceurl") == self.device.deviceurl
            and execution.get("command_name")
            in [COMMAND_OPEN, COMMAND_UP, COMMAND_OPEN_SLATS]
            for execution in self.coordinator.executions.values()
        )

    @property
    def is_closing(self):
        """Return if the cover is closing or not."""
        return any(
            execution.get("deviceurl") == self.device.deviceurl
            and execution.get("command_name")
            in [COMMAND_CLOSE, COMMAND_DOWN, COMMAND_CLOSE_SLATS]
            for execution in self.coordinator.executions.values()
        )

    @property
    def supported_features(self):
        """Flag supported features."""
        supported_features = 0

        if self.has_command(COMMAND_OPEN_SLATS):
            supported_features |= SUPPORT_OPEN_TILT

            if self.has_command(COMMAND_STOP_IDENTIFY, COMMAND_STOP, COMMAND_MY):
                supported_features |= SUPPORT_STOP_TILT

        if self.has_command(COMMAND_CLOSE_SLATS):
            supported_features |= SUPPORT_CLOSE_TILT

        if self.has_command(COMMAND_SET_ORIENTATION):
            supported_features |= SUPPORT_SET_TILT_POSITION

        if self.has_command(
            COMMAND_SET_POSITION, COMMAND_SET_CLOSURE, COMMAND_SET_PEDESTRIAN_POSITION
        ):
            supported_features |= SUPPORT_SET_POSITION

        if self.has_command(COMMAND_OPEN, COMMAND_UP, COMMAND_CYCLE):
            supported_features |= SUPPORT_OPEN

            if self.has_command(COMMAND_STOP_IDENTIFY, COMMAND_STOP, COMMAND_MY):
                supported_features |= SUPPORT_STOP

        if self.has_command(COMMAND_CLOSE, COMMAND_DOWN, COMMAND_CYCLE):
            supported_features |= SUPPORT_CLOSE

        if self.has_command(COMMAND_SET_POSITION_AND_LINEAR_SPEED):
            supported_features |= SUPPORT_COVER_POSITION_LOW_SPEED

        if self.has_command(COMMAND_MY):
            supported_features |= SUPPORT_MY

        return supported_features
