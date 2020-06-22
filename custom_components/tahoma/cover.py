"""Support for TaHoma cover - shutters etc."""
from datetime import timedelta
import logging

from homeassistant.components.cover import (
    ATTR_POSITION,
    ATTR_TILT_POSITION,
    DEVICE_CLASS_AWNING,
    DEVICE_CLASS_BLIND,
    DEVICE_CLASS_CURTAIN,
    DEVICE_CLASS_GARAGE,
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
from homeassistant.util.dt import utcnow

from .const import (
    ATTR_LOCK_END_TS,
    ATTR_LOCK_LEVEL,
    ATTR_LOCK_ORIG,
    ATTR_LOCK_START_TS,
    ATTR_MEM_POS,
    COMMAND_SET_CLOSURE,
    COMMAND_SET_ORIENTATION,
    COMMAND_SET_PEDESTRIAN_POSITION,
    COMMAND_SET_POSITION,
    CORE_CLOSURE_STATE,
    CORE_DEPLOYMENT_STATE,
    CORE_MEMORIZED_1_POSITION_STATE,
    CORE_PEDESTRIAN_POSITION_STATE,
    CORE_PRIORITY_LOCK_TIMER_STATE,
    CORE_SLATS_ORIENTATION_STATE,
    CORE_TARGET_CLOSURE_STATE,
    DOMAIN,
    IO_PRIORITY_LOCK_LEVEL_STATE,
    IO_PRIORITY_LOCK_ORIGINATOR_STATE,
    TAHOMA_COVER_DEVICE_CLASSES,
    TAHOMA_TYPES,
)
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma covers from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]

    entities = []
    controller = data.get("controller")

    for device in data.get("devices"):
        if TAHOMA_TYPES[device.uiclass] == "cover":
            entities.append(TahomaCover(device, controller))

    async_add_entities(entities)


class TahomaCover(TahomaDevice, CoverEntity):
    """Representation a TaHoma Cover."""

    def __init__(self, tahoma_device, controller):
        """Initialize the device."""
        super().__init__(tahoma_device, controller)

        self._icon = None
        self._lock_timer = 0  # Can be 0 and bigger
        self._lock_start_ts = None
        self._lock_end_ts = None

        # Can be 'comfortLevel1', 'comfortLevel2', 'comfortLevel3',
        # 'comfortLevel4', 'environmentProtection', 'humanProtection',
        # 'userLevel1', 'userLevel2'
        self._lock_level = None

        # Can be 'LSC', 'SAAC', 'SFC', 'UPS', 'externalGateway', 'localUser',
        # 'myself', 'rain', 'security', 'temperature', 'timer', 'user', 'wind'
        self._lock_originator = None

    def update(self):
        """Update method."""
        self.controller.get_states([self.tahoma_device])

        # Set current position.
        # Home Assistant: 0 is closed, 100 is fully open.
        # core:ClosureState: 100 is closed, 0 is fully open.

        # Set position for vertical covers
        if CORE_CLOSURE_STATE in self.tahoma_device.active_states:
            self._position = 100 - self.tahoma_device.active_states.get(
                CORE_CLOSURE_STATE
            )

        # Set position for horizontal covers
        if CORE_DEPLOYMENT_STATE in self.tahoma_device.active_states:
            self._position = 100 - self.tahoma_device.active_states.get(
                CORE_DEPLOYMENT_STATE
            )

        # Set position for gates
        if CORE_PEDESTRIAN_POSITION_STATE in self.tahoma_device.active_states:
            self._position = 100 - self.tahoma_device.active_states.get(
                CORE_PEDESTRIAN_POSITION_STATE
            )

        if CORE_TARGET_CLOSURE_STATE in self.tahoma_device.active_states:
            self._position = 100 - self.tahoma_device.active_states.get(
                CORE_TARGET_CLOSURE_STATE
            )

        # Set tilt position for slats
        if CORE_SLATS_ORIENTATION_STATE in self.tahoma_device.active_states:
            self._tilt_position = 100 - self.tahoma_device.active_states.get(
                CORE_SLATS_ORIENTATION_STATE
            )

        if getattr(self, "_position", False):
            # HorizontalAwning devices need a reversed position that can not be obtained via the API
            if "Horizontal" in self.tahoma_device.widget:
                self._position = 100 - self._position

            # TODO Check if this offset is really necessary
            if self._position <= 5:
                self._position = 0
            if self._position >= 95:
                self._position = 100

        # Set Lock Timers
        if CORE_PRIORITY_LOCK_TIMER_STATE in self.tahoma_device.active_states:
            old_lock_timer = self._lock_timer
            self._lock_timer = self.tahoma_device.active_states[
                CORE_PRIORITY_LOCK_TIMER_STATE
            ]

            # Derive timestamps from _lock_timer, only if not already set or something has changed
            if self._lock_timer > 0:
                _LOGGER.debug("Update %s, lock_timer: %d", self._name, self._lock_timer)
                if self._lock_start_ts is None:
                    self._lock_start_ts = utcnow()
                if self._lock_end_ts is None or old_lock_timer != self._lock_timer:
                    self._lock_end_ts = utcnow() + timedelta(seconds=self._lock_timer)
            else:
                self._lock_start_ts = None
                self._lock_end_ts = None
        else:
            self._lock_timer = 0
            self._lock_start_ts = None
            self._lock_end_ts = None

        # Set Lock Level
        self._lock_level = self.tahoma_device.active_states.get(
            IO_PRIORITY_LOCK_LEVEL_STATE
        )

        # Set Lock Originator
        self._lock_originator = self.tahoma_device.active_states.get(
            IO_PRIORITY_LOCK_ORIGINATOR_STATE
        )

    @property
    def current_cover_position(self):
        """Return current position of cover."""
        return getattr(self, "_position", None)

    @property
    def current_cover_tilt_position(self):
        """Return current position of cover tilt.

        None is unknown, 0 is closed, 100 is fully open.
        """
        return getattr(self, "_tilt_position", None)

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

        if "core:OpenClosedState" in self.tahoma_device.active_states:
            return (
                self.tahoma_device.active_states.get("core:OpenClosedState") == "closed"
            )

        if "core:SlatsOpenClosedState" in self.tahoma_device.active_states:
            return (
                self.tahoma_device.active_states.get("core:SlatsOpenClosedState")
                == "closed"
            )

        if "core:OpenClosedPartialState" in self.tahoma_device.active_states:
            return (
                self.tahoma_device.active_states.get("core:OpenClosedPartialState")
                == "closed"
            )

        if "core:OpenClosedPedestrianState" in self.tahoma_device.active_states:
            return (
                self.tahoma_device.active_states.get("core:OpenClosedPedestrianState")
                == "closed"
            )

        if "core:OpenClosedUnknownState" in self.tahoma_device.active_states:
            return (
                self.tahoma_device.active_states.get("core:OpenClosedUnknownState")
                == "closed"
            )

        if getattr(self, "_position", None) is not None:
            return self._position == 0

        if getattr(self, "_tilt_position", None) is not None:
            return self._tilt_position == 0

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
        if self._lock_start_ts is not None:
            attr[ATTR_LOCK_START_TS] = self._lock_start_ts.isoformat()
        if self._lock_end_ts is not None:
            attr[ATTR_LOCK_END_TS] = self._lock_end_ts.isoformat()
        if self._lock_level is not None:
            attr[ATTR_LOCK_LEVEL] = self._lock_level
        if self._lock_originator is not None:
            attr[ATTR_LOCK_ORIG] = self._lock_originator

        return attr

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        if self._lock_timer > 0:
            if self._lock_originator == "wind":
                return "mdi:weather-windy"
            else:
                return "mdi:lock-alert"

        return self._icon

    def open_cover(self, **kwargs):
        """Open the cover."""

        if "open" in self.tahoma_device.command_definitions:
            return self.apply_action("open")

        if "up" in self.tahoma_device.command_definitions:
            return self.apply_action("up")

    def open_cover_tilt(self, **kwargs):
        """Open the cover tilt."""

        if "openSlats" in self.tahoma_device.command_definitions:
            return self.apply_action("openSlats")

    def close_cover(self, **kwargs):
        """Close the cover."""

        if "close" in self.tahoma_device.command_definitions:
            return self.apply_action("close")

        if "down" in self.tahoma_device.command_definitions:
            return self.apply_action("down")

    def close_cover_tilt(self, **kwargs):
        """Close the cover tilt."""

        if "closeSlats" in self.tahoma_device.command_definitions:
            return self.apply_action("closeSlats")

    def stop_cover(self, **kwargs):
        """Stop the cover."""

        if "stop" in self.tahoma_device.command_definitions:
            return self.apply_action("stop")

        if "stopIdentify" in self.tahoma_device.command_definitions:
            return self.apply_action("stopIdentify")

        if "my" in self.tahoma_device.command_definitions:
            return self.apply_action("my")

    def stop_cover_tilt(self, **kwargs):
        """Stop the cover."""

        if "stopIdentify" in self.tahoma_device.command_definitions:
            return self.apply_action("stopIdentify")

        if "stop" in self.tahoma_device.command_definitions:
            return self.apply_action("stop")

        if "my" in self.tahoma_device.command_definitions:
            return self.apply_action("my")

    @property
    def supported_features(self):
        """Flag supported features."""

        supported_features = 0

        if "openSlats" in self.tahoma_device.command_definitions:
            supported_features |= SUPPORT_OPEN_TILT

            if (
                "stop" in self.tahoma_device.command_definitions
                or "stopIdentify" in self.tahoma_device.command_definitions
                or "my" in self.tahoma_device.command_definitions
            ):
                supported_features |= SUPPORT_STOP_TILT

        if "closeSlats" in self.tahoma_device.command_definitions:
            supported_features |= SUPPORT_CLOSE_TILT

        if COMMAND_SET_ORIENTATION in self.tahoma_device.command_definitions:
            supported_features |= SUPPORT_SET_TILT_POSITION

        if (
            COMMAND_SET_POSITION in self.tahoma_device.command_definitions
            or COMMAND_SET_CLOSURE in self.tahoma_device.command_definitions
            or "setPedestrianPosition" in self.tahoma_device.command_definitions
        ):
            supported_features |= SUPPORT_SET_POSITION

        if (
            "open" in self.tahoma_device.command_definitions
            or "up" in self.tahoma_device.command_definitions
        ):
            supported_features |= SUPPORT_OPEN

            if (
                "stop" in self.tahoma_device.command_definitions
                or "my" in self.tahoma_device.command_definitions
                or "stopIdentify" in self.tahoma_device.command_definitions
            ):
                supported_features |= SUPPORT_STOP

        if (
            "close" in self.tahoma_device.command_definitions
            or "down" in self.tahoma_device.command_definitions
        ):
            supported_features |= SUPPORT_CLOSE

        return supported_features
