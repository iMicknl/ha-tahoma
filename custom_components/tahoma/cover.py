"""Support for Tahoma cover - shutters etc."""
from datetime import timedelta
import logging

from homeassistant.components.cover import (
    ATTR_POSITION,
    DEVICE_CLASS_AWNING,
    DEVICE_CLASS_BLIND,
    DEVICE_CLASS_CURTAIN,
    DEVICE_CLASS_GARAGE,
    DEVICE_CLASS_SHUTTER,
    DEVICE_CLASS_WINDOW,
    CoverEntity,
    SUPPORT_OPEN,
    SUPPORT_CLOSE,
    SUPPORT_SET_POSITION,
    SUPPORT_STOP,
    SUPPORT_OPEN_TILT,
    SUPPORT_CLOSE_TILT,
    SUPPORT_STOP_TILT,
    SUPPORT_SET_TILT_POSITION
)
from homeassistant.util.dt import utcnow

from .tahoma_device import TahomaDevice

from .const import (
    DOMAIN,
    TAHOMA_TYPES,
    TAHOMA_COVER_DEVICE_CLASSES,
    ATTR_MEM_POS,
    ATTR_LOCK_START_TS,
    ATTR_LOCK_END_TS,
    ATTR_LOCK_LEVEL,
    ATTR_LOCK_ORIG,
    CORE_CLOSURE_STATE,
    CORE_DEPLOYMENT_STATE,
    CORE_PRIORITY_LOCK_TIMER_STATE,
    CORE_SLATS_ORIENTATION_STATE,
    CORE_MEMORIZED_1_POSITION_STATE,
    IO_PRIORITY_LOCK_LEVEL_STATE,
    IO_PRIORITY_LOCK_ORIGINATOR_STATE,
    COMMAND_SET_CLOSURE,
    COMMAND_SET_POSITION,
    COMMAND_SET_ORIENTATION
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Tahoma covers from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]

    entities = []
    controller = data.get("controller")

    for device in data.get("devices"):
        if TAHOMA_TYPES[device.uiclass] == "cover":
            entities.append(TahomaCover(device, controller))

    async_add_entities(entities)


class TahomaCover(TahomaDevice, CoverEntity):
    """Representation a Tahoma Cover."""

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
                CORE_CLOSURE_STATE)

            # TODO Check if this offset is really necessary
            if self._position <= 5:
                self._position = 0
            if self._position >= 95:
                self._position = 100

        # Set position for horizontal covers
        if CORE_DEPLOYMENT_STATE in self.tahoma_device.active_states:
            self._closure = self.tahoma_device.active_states.get(
                CORE_DEPLOYMENT_STATE)

            self._position = 100 - self.tahoma_device.active_states.get(
                CORE_CLOSURE_STATE)

            # TODO Check if this offset is really necessary
            if self._position <= 5:
                self._position = 0
            if self._position >= 95:
                self._position = 100

        # Set position for covers with slats
        if CORE_SLATS_ORIENTATION_STATE in self.tahoma_device.active_states:
            self._tilt_position = 100 - self.tahoma_device.active_states.get(
                CORE_SLATS_ORIENTATION_STATE
            )

            # TODO Check if this offset is really necessary
            if self._tilt_position <= 5:
                self._tilt_position = 0
            if self._tilt_position >= 95:
                self._tilt_position = 100

        # Set Lock Timers
        if CORE_PRIORITY_LOCK_TIMER_STATE in self.tahoma_device.active_states:
            old_lock_timer = self._lock_timer
            self._lock_timer = self.tahoma_device.active_states[
                CORE_PRIORITY_LOCK_TIMER_STATE
            ]

            # Derive timestamps from _lock_timer, only if not already set or something has changed
            if self._lock_timer > 0:
                _LOGGER.debug("Update %s, lock_timer: %d",
                              self._name, self._lock_timer)
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

        if COMMAND_SET_POSITION in self.tahoma_device.command_definitions:
            return self.apply_action(COMMAND_SET_POSITION, 100 - kwargs.get(ATTR_POSITION, 0))

        if COMMAND_SET_CLOSURE in self.tahoma_device.command_definitions:
            return self.apply_action(COMMAND_SET_CLOSURE, 100 - kwargs.get(ATTR_POSITION, 0))

        # TODO See if above code needs to be reversed for HorizontalAwningIO component
        # if self.tahoma_device.type == "io:HorizontalAwningIOComponent":
        #     self.apply_action(command, kwargs.get(ATTR_POSITION, 0))

    def set_cover_tilt_position(self, **kwargs):
        """Move the cover tilt to a specific position."""
        self.apply_action(COMMAND_SET_ORIENTATION, 100 -
                          kwargs.get(ATTR_POSITION, 0))

    @property
    def is_closed(self):
        """Return if the cover is closed."""

        if "core:OpenClosedState" in self.tahoma_device.active_states:
            return self.tahoma_device.active_states.get("core:OpenClosedState") == "closed"

        if "core:SlatsOpenClosedState" in self.tahoma_device.active_states:
            return self.tahoma_device.active_states.get("core:SlatsOpenClosedState") == "closed"

        if "core:OpenClosedPartialState" in self.tahoma_device.active_states:
            return self.tahoma_device.active_states.get("core:OpenClosedPartialState") == "closed"

        if getattr(self, "_position", None) is not None:
            return self._position == 0

        if getattr(self, "_tilt_position", None) is not None:
            return self._tilt_position == 0

        return None

    @property
    def device_class(self):
        """Return the class of the device."""
        return TAHOMA_COVER_DEVICE_CLASSES.get(self.tahoma_device.widget) or TAHOMA_COVER_DEVICE_CLASSES.get(self.tahoma_device.uiclass) or DEVICE_CLASS_BLIND

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
        self.apply_action("open")

    def close_cover(self, **kwargs):
        """Close the cover."""
        self.apply_action("close")

    def stop_cover(self, **kwargs):
        """Stop the cover."""

        if "stop" in self.tahoma_device.command_definitions:
            return self.apply_action("stop")

        if "my" in self.tahoma_device.command_definitions:
            return self.apply_action("my")

        if "stopIdentify" in self.tahoma_device.command_definitions:
            return self.apply_action("stopIdentify")

    def stop_cover_tilt(self, **kwargs):
        """Stop the cover."""
        self.apply_action("stop")

    @property
    def supported_features(self):
        """Flag supported features."""

        supported_features = 0

        if "openSlats" in self.tahoma_device.command_definitions:
            supported_features |= (
                SUPPORT_OPEN_TILT
            )

            if "stop" in self.tahoma_device.command_definitions:
                supported_features |= (
                    SUPPORT_STOP_TILT
                )

        if "closeSlats" in self.tahoma_device.command_definitions:
            supported_features |= (
                SUPPORT_CLOSE_TILT
            )

        if COMMAND_SET_ORIENTATION in self.tahoma_device.command_definitions:
            supported_features |= (
                SUPPORT_SET_TILT_POSITION
            )

        if COMMAND_SET_POSITION in self.tahoma_device.command_definitions or COMMAND_SET_CLOSURE in self.tahoma_device.command_definitions:
            supported_features |= (
                SUPPORT_SET_POSITION
            )

        if "open" in self.tahoma_device.command_definitions:
            supported_features |= (
                SUPPORT_OPEN
            )

            if "stop" in self.tahoma_device.command_definitions or "my" in self.tahoma_device.command_definitions or "stopIdentify" in self.tahoma_device.command_definitions:
                supported_features |= (
                    SUPPORT_STOP
                )

        if "close" in self.tahoma_device.command_definitions:
            supported_features |= (
                SUPPORT_CLOSE
            )

        return supported_features
