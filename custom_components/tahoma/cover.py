"""Support for TaHoma cover - shutters etc."""
import logging

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

from .const import DOMAIN, TAHOMA_TYPES
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

ATTR_LOCK_ORIG = "lock_originator"
ATTR_MEM_POS = "memorized_position"

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
COMMAND_STOP = "stop"
COMMAND_STOP_IDENTIFY = "stopIdentify"
COMMAND_UP = "up"

CORE_CLOSURE_STATE = "core:ClosureState"
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

ICON_LOCK_ALERT = "mdi:lock-alert"
ICON_WEATHER_WINDY = "mdi:weather-windy"

IO_PRIORITY_LOCK_ORIGINATOR_STATE = "io:PriorityLockOriginatorState"

STATE_CLOSED = "closed"

TAHOMA_COVER_DEVICE_CLASSES = {
    "Awning": DEVICE_CLASS_AWNING,
    "ExteriorScreen": DEVICE_CLASS_BLIND,
    "Pergola": DEVICE_CLASS_AWNING,
    "RollerShutter": DEVICE_CLASS_SHUTTER,
    "Window": DEVICE_CLASS_WINDOW,
    "Blind": DEVICE_CLASS_BLIND,
    "GarageDoor": DEVICE_CLASS_GARAGE,
    "ExteriorVenetianBlind": DEVICE_CLASS_BLIND,
    "VeluxInteriorBlind": DEVICE_CLASS_BLIND,
    "Gate": DEVICE_CLASS_GATE,
    "Curtain": DEVICE_CLASS_CURTAIN,
    "SwingingShutter": DEVICE_CLASS_SHUTTER,
}


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma covers from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]
    controller = data.get("controller")

    entities = [
        TahomaCover(device, controller)
        for device in data.get("devices")
        if TAHOMA_TYPES[device.uiclass] == "cover"
    ]

    async_add_entities(entities)


class TahomaCover(TahomaDevice, CoverEntity):
    """Representation a TaHoma Cover."""

    def update(self):
        """Update method."""
        if self.should_wait():
            self.schedule_update_ha_state(True)
            return
        self.controller.get_states([self.tahoma_device])

    @property
    def current_cover_position(self):
        """Return current position of cover."""

        states = self.tahoma_device.active_states

        position = None

        # Set position for vertical covers
        if CORE_CLOSURE_STATE in states:
            position = 100 - states.get(CORE_CLOSURE_STATE)

        # Set position for horizontal covers
        if CORE_DEPLOYMENT_STATE in states:
            position = 100 - states.get(CORE_DEPLOYMENT_STATE)

        # Set position for gates
        if CORE_PEDESTRIAN_POSITION_STATE in states:
            position = 100 - states.get(CORE_PEDESTRIAN_POSITION_STATE)

        if CORE_TARGET_CLOSURE_STATE in states:
            position = 100 - states.get(CORE_TARGET_CLOSURE_STATE)

        if position is not None:
            # HorizontalAwning devices need a reversed position that can not be obtained via the API
            if "Horizontal" in self.tahoma_device.widget:
                position = 100 - position

            # TODO Check if this offset is really necessary
            if position <= 5:
                position = 0
            if position >= 95:
                position = 100

        return position

    @property
    def current_cover_tilt_position(self):
        """Return current position of cover tilt.

        None is unknown, 0 is closed, 100 is fully open.
        """
        states = self.tahoma_device.active_states
        position = None
        if CORE_SLATS_ORIENTATION_STATE in states:
            position = 100 - states.get(CORE_SLATS_ORIENTATION_STATE)
        return position

    def set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = 100 - kwargs.get(ATTR_POSITION, 0)

        # HorizontalAwning devices need a reversed position that can not be obtained via the API
        if "Horizontal" in self.tahoma_device.widget:
            position = kwargs.get(ATTR_POSITION, 0)

        if COMMAND_SET_POSITION in self.tahoma_device.command_definitions:
            return self.apply_action(COMMAND_SET_POSITION, position)

        if COMMAND_SET_CLOSURE in self.tahoma_device.command_definitions:
            return self.apply_action(COMMAND_SET_CLOSURE, position)

        if COMMAND_SET_PEDESTRIAN_POSITION in self.tahoma_device.command_definitions:
            return self.apply_action(COMMAND_SET_PEDESTRIAN_POSITION, position)

    def set_cover_tilt_position(self, **kwargs):
        """Move the cover tilt to a specific position."""
        self.apply_action(
            COMMAND_SET_ORIENTATION, 100 - kwargs.get(ATTR_TILT_POSITION, 0)
        )

    @property
    def is_closed(self):
        """Return if the cover is closed."""

        states = self.tahoma_device.active_states
        if CORE_OPEN_CLOSED_STATE in states:
            return states.get(CORE_OPEN_CLOSED_STATE) == STATE_CLOSED

        if CORE_SLATS_OPEN_CLOSED_STATE in states:
            return states.get(CORE_SLATS_OPEN_CLOSED_STATE) == STATE_CLOSED

        if CORE_OPEN_CLOSED_PARTIAL_STATE in states:
            return states.get(CORE_OPEN_CLOSED_PARTIAL_STATE) == STATE_CLOSED

        if CORE_OPEN_CLOSED_PEDESTRIAN_STATE in states:
            return states.get(CORE_OPEN_CLOSED_PEDESTRIAN_STATE) == STATE_CLOSED

        if CORE_OPEN_CLOSED_UNKNOWN_STATE in states:
            return states.get(CORE_OPEN_CLOSED_UNKNOWN_STATE) == STATE_CLOSED

        if self.current_cover_position is not None:
            return self.current_cover_position == 0

        if self.current_cover_tilt_position is not None:
            return self.current_cover_tilt_position == 0

        return None

    @property
    def device_class(self):
        """Return the class of the device."""
        return (
            TAHOMA_COVER_DEVICE_CLASSES.get(self.tahoma_device.widget)
            or TAHOMA_COVER_DEVICE_CLASSES.get(self.tahoma_device.uiclass)
            or DEVICE_CLASS_BLIND
        )

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        attr = {}
        super_attr = super().device_state_attributes

        if super_attr is not None:
            attr.update(super_attr)

        if CORE_MEMORIZED_1_POSITION_STATE in self.tahoma_device.active_states:
            attr[ATTR_MEM_POS] = self.tahoma_device.active_states[
                CORE_MEMORIZED_1_POSITION_STATE
            ]

        if IO_PRIORITY_LOCK_ORIGINATOR_STATE in self.tahoma_device.active_states:
            attr[ATTR_LOCK_ORIG] = self.tahoma_device.active_states[
                IO_PRIORITY_LOCK_ORIGINATOR_STATE
            ]
        return attr

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        states = self.tahoma_device.active_states
        if states.get(CORE_PRIORITY_LOCK_TIMER_STATE, 0) > 0:
            if states.get(IO_PRIORITY_LOCK_ORIGINATOR_STATE) == "wind":
                return ICON_WEATHER_WINDY
            else:
                return ICON_LOCK_ALERT
        return None

    def open_cover(self, **kwargs):
        """Open the cover."""

        if COMMAND_OPEN in self.tahoma_device.command_definitions:
            return self.apply_action(COMMAND_OPEN)

        if COMMAND_UP in self.tahoma_device.command_definitions:
            return self.apply_action(COMMAND_UP)

    def open_cover_tilt(self, **kwargs):
        """Open the cover tilt."""

        if COMMAND_OPEN_SLATS in self.tahoma_device.command_definitions:
            return self.apply_action(COMMAND_OPEN_SLATS)

    def close_cover(self, **kwargs):
        """Close the cover."""

        if COMMAND_CLOSE in self.tahoma_device.command_definitions:
            return self.apply_action(COMMAND_CLOSE)

        if COMMAND_DOWN in self.tahoma_device.command_definitions:
            return self.apply_action(COMMAND_DOWN)

    def close_cover_tilt(self, **kwargs):
        """Close the cover tilt."""

        if COMMAND_CLOSE_SLATS in self.tahoma_device.command_definitions:
            return self.apply_action(COMMAND_CLOSE_SLATS)

    def stop_cover(self, **kwargs):
        """Stop the cover."""

        if COMMAND_STOP in self.tahoma_device.command_definitions:
            return self.apply_action(COMMAND_STOP)

        if COMMAND_STOP_IDENTIFY in self.tahoma_device.command_definitions:
            return self.apply_action(COMMAND_STOP_IDENTIFY)

        if COMMAND_MY in self.tahoma_device.command_definitions:
            return self.apply_action(COMMAND_MY)

    def stop_cover_tilt(self, **kwargs):
        """Stop the cover."""

        if COMMAND_STOP_IDENTIFY in self.tahoma_device.command_definitions:
            return self.apply_action(COMMAND_STOP_IDENTIFY)

        if COMMAND_STOP in self.tahoma_device.command_definitions:
            return self.apply_action(COMMAND_STOP)

        if COMMAND_MY in self.tahoma_device.command_definitions:
            return self.apply_action(COMMAND_MY)

    @property
    def supported_features(self):
        """Flag supported features."""

        supported_features = 0

        if COMMAND_OPEN_SLATS in self.tahoma_device.command_definitions:
            supported_features |= SUPPORT_OPEN_TILT

            if (
                COMMAND_STOP in self.tahoma_device.command_definitions
                or COMMAND_STOP_IDENTIFY in self.tahoma_device.command_definitions
                or COMMAND_MY in self.tahoma_device.command_definitions
            ):
                supported_features |= SUPPORT_STOP_TILT

        if COMMAND_CLOSE_SLATS in self.tahoma_device.command_definitions:
            supported_features |= SUPPORT_CLOSE_TILT

        if COMMAND_SET_ORIENTATION in self.tahoma_device.command_definitions:
            supported_features |= SUPPORT_SET_TILT_POSITION

        if (
            COMMAND_SET_POSITION in self.tahoma_device.command_definitions
            or COMMAND_SET_CLOSURE in self.tahoma_device.command_definitions
            or COMMAND_SET_PEDESTRIAN_POSITION in self.tahoma_device.command_definitions
        ):
            supported_features |= SUPPORT_SET_POSITION

        if (
            COMMAND_OPEN in self.tahoma_device.command_definitions
            or COMMAND_UP in self.tahoma_device.command_definitions
        ):
            supported_features |= SUPPORT_OPEN

            if (
                COMMAND_STOP in self.tahoma_device.command_definitions
                or COMMAND_MY in self.tahoma_device.command_definitions
                or COMMAND_STOP_IDENTIFY in self.tahoma_device.command_definitions
            ):
                supported_features |= SUPPORT_STOP

        if (
            COMMAND_CLOSE in self.tahoma_device.command_definitions
            or COMMAND_DOWN in self.tahoma_device.command_definitions
        ):
            supported_features |= SUPPORT_CLOSE

        return supported_features
