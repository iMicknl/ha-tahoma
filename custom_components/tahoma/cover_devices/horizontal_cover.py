"""Support for TaHoma cover - shutters etc."""
from homeassistant.components.cover import ATTR_POSITION, DEVICE_CLASS_AWNING

from custom_components.tahoma.cover_devices.tahoma_cover import TahomaCover

COMMAND_DEPLOY = "deploy"
COMMAND_SET_DEPLOYMENT = "setDeployment"
COMMAND_UNDEPLOY = "undeploy"

CORE_DEPLOYMENT_STATE = "core:DeploymentState"


class TahomaHorizontalCover(TahomaCover):
    """Representation of a TaHoma Cover."""

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
