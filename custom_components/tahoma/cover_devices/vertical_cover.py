"""Support for TaHoma cover - shutters etc."""
from homeassistant.components.cover import ATTR_POSITION

from custom_components.tahoma.cover_devices.tahoma_cover import TahomaCover

COMMAND_CYCLE = "cycle"
COMMAND_CLOSE = "close"
COMMAND_DOWN = "down"
COMMAND_OPEN = "open"
COMMAND_SET_CLOSURE = "setClosure"

COMMAND_UP = "up"

COMMANDS_OPEN = [COMMAND_OPEN, COMMAND_UP, COMMAND_CYCLE]
COMMANDS_CLOSE = [COMMAND_CLOSE, COMMAND_DOWN, COMMAND_CYCLE]

CORE_CLOSURE_STATE = "core:ClosureState"
CORE_CLOSURE_OR_ROCKER_POSITION_STATE = "core:ClosureOrRockerPositionState"
# io:DiscreteGateOpenerIOComponent
CORE_PEDESTRIAN_POSITION_STATE = "core:PedestrianPositionState"


SERVICE_COVER_POSITION_LOW_SPEED = "set_cover_position_low_speed"

SUPPORT_COVER_POSITION_LOW_SPEED = 1024


class TahomaVerticalCover(TahomaCover):
    """Representation of a TaHoma Cover."""

    @property
    def current_cover_position(self):
        """
        Return current position of cover.

        None is unknown, 0 is closed, 100 is fully open.
        """
        position = self.select_state(
            CORE_CLOSURE_STATE,
            CORE_CLOSURE_OR_ROCKER_POSITION_STATE,
            CORE_PEDESTRIAN_POSITION_STATE,
        )

        # Uno devices can have a position not in 0 to 100 range when unknown
        if position is None or position < 0 or position > 100:
            return None

        return 100 - position

    async def async_set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = 100 - kwargs.get(ATTR_POSITION, 0)
        await self.async_execute_command(COMMAND_SET_CLOSURE, position)

    async def async_open_cover(self, **_):
        """Open the cover."""
        await self.async_execute_command(self.select_command(*COMMANDS_OPEN))

    async def async_close_cover(self, **_):
        """Close the cover."""
        await self.async_execute_command(self.select_command(*COMMANDS_CLOSE))
