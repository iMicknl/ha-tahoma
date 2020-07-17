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
from .switch import COMMAND_CYCLE
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

    @property
    def current_cover_position(self):
        """Return current position of cover."""

        position = self.select_state(
            CORE_CLOSURE_STATE,
            CORE_DEPLOYMENT_STATE,
            CORE_PEDESTRIAN_POSITION_STATE,
            CORE_TARGET_CLOSURE_STATE,
        )

        return position if "Horizontal" in self.tahoma_device.widget else 100 - position

    @property
    def current_cover_tilt_position(self):
        """Return current position of cover tilt.

        None is unknown, 0 is closed, 100 is fully open.
        """
        position = self.select_state(CORE_SLATS_ORIENTATION_STATE)
        return 100 - position if position else None

    def set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = 100 - kwargs.get(ATTR_POSITION, 0)

        # HorizontalAwning devices need a reversed position that can not be obtained via the API
        if "Horizontal" in self.tahoma_device.widget:
            position = kwargs.get(ATTR_POSITION, 0)

        command = self.select_command(
            COMMAND_SET_POSITION, COMMAND_SET_CLOSURE, COMMAND_SET_PEDESTRIAN_POSITION
        )
        self.apply_action(command, position)

    def set_cover_tilt_position(self, **kwargs):
        """Move the cover tilt to a specific position."""
        self.apply_action(
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
        )

        if state is not None:
            return state == "closed"

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
        attr[ATTR_MEM_POS] = self.select_state(CORE_MEMORIZED_1_POSITION_STATE)
        attr[ATTR_LOCK_ORIG] = self.select_state(IO_PRIORITY_LOCK_ORIGINATOR_STATE)
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
        self.apply_action(self.select_command(COMMAND_OPEN, COMMAND_UP))

    def open_cover_tilt(self, **kwargs):
        """Open the cover tilt."""
        self.apply_action(self.select_command(COMMAND_OPEN_SLATS))

    def close_cover(self, **kwargs):
        """Close the cover."""
        self.apply_action(self.select_command(COMMAND_CLOSE, COMMAND_DOWN))

    def close_cover_tilt(self, **kwargs):
        """Close the cover tilt."""
        self.apply_action(self.select_command(COMMAND_CLOSE_SLATS))

    def stop_cover(self, **kwargs):
        """Stop the cover."""
        self.apply_action(
            self.select_command(COMMAND_STOP, COMMAND_STOP_IDENTIFY, COMMAND_MY)
        )

    def stop_cover_tilt(self, **kwargs):
        """Stop the cover."""
        self.apply_action(
            self.select_command(COMMAND_STOP_IDENTIFY, COMMAND_STOP, COMMAND_MY)
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

        if self.has_command(COMMAND_OPEN, COMMAND_UP):
            supported_features |= SUPPORT_OPEN

            if self.has_command(COMMAND_STOP_IDENTIFY, COMMAND_STOP, COMMAND_MY):
                supported_features |= SUPPORT_STOP

        if self.has_command(COMMAND_CLOSE, COMMAND_DOWN):
            supported_features |= SUPPORT_CLOSE

        return supported_features

    def toggle(self):
        """Toggle the entity."""
        if self.has_command(COMMAND_CYCLE):
            self.apply_action(COMMAND_CYCLE)
        else:
            super().toggle()
