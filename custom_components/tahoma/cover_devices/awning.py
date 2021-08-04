"""Support for TaHoma Awnings."""
from homeassistant.components.cover import (
    ATTR_POSITION,
    DEVICE_CLASS_AWNING,
    SUPPORT_CLOSE,
    SUPPORT_OPEN,
    SUPPORT_SET_POSITION,
    SUPPORT_STOP,
)

from custom_components.tahoma.cover_devices.tahoma_cover import (
    COMMANDS_STOP,
    TahomaGenericCover,
)

COMMAND_DEPLOY = "deploy"
COMMAND_SET_DEPLOYMENT = "setDeployment"
COMMAND_UNDEPLOY = "undeploy"

CORE_DEPLOYMENT_STATE = "core:DeploymentState"


class Awning(TahomaGenericCover):
    """Representation of a TaHoma Awning."""

    @property
    def supported_features(self):
        """Flag supported features."""
        supported_features = super().supported_features

        if self.has_command(COMMAND_SET_DEPLOYMENT):
            supported_features |= SUPPORT_SET_POSITION

        if self.has_command(COMMAND_DEPLOY):
            supported_features |= SUPPORT_OPEN

            if self.has_command(*COMMANDS_STOP):
                supported_features |= SUPPORT_STOP

        if self.has_command(COMMAND_UNDEPLOY):
            supported_features |= SUPPORT_CLOSE

        return supported_features

    @property
    def device_class(self):
        """Return the class of the device."""
        return DEVICE_CLASS_AWNING

    @property
    def current_cover_position(self):
        """
        Return current position of cover.

        None is unknown, 0 is closed, 100 is fully open.
        """
        return self.select_state(CORE_DEPLOYMENT_STATE)

    async def async_set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = kwargs.get(ATTR_POSITION, 0)
        await self.async_execute_command(COMMAND_SET_DEPLOYMENT, position)

    async def async_open_cover(self, **_):
        """Open the cover."""
        await self.async_execute_command(COMMAND_DEPLOY)

    async def async_close_cover(self, **_):
        """Close the cover."""
        await self.async_execute_command(COMMAND_UNDEPLOY)
