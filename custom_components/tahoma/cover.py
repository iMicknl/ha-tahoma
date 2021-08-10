"""Support for TaHoma cover - shutters etc."""
from homeassistant.components.cover import ATTR_POSITION, DOMAIN as COVER
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import voluptuous as vol

from .const import DOMAIN
from .cover_devices.awning import Awning
from .cover_devices.vertical_cover import VerticalCover

SERVICE_COVER_MY_POSITION = "set_cover_my_position"
SERVICE_COVER_POSITION_LOW_SPEED = "set_cover_position_low_speed"

SUPPORT_MY = 512
SUPPORT_COVER_POSITION_LOW_SPEED = 1024


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up the TaHoma covers from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    # Includes fix for #486, which is waiting on Somfy back-end deployment
    # Remove when DeploymentState will be returned for AwningValance
    entities = [
        Awning(device.deviceurl, coordinator)
        for device in data["platforms"].get(COVER)
        if device.ui_class == "Awning" and device.widget != "AwningValance"
    ]

    entities += [
        VerticalCover(device.deviceurl, coordinator)
        for device in data["platforms"].get(COVER)
        if device.ui_class != "Awning" or device.widget == "AwningValance"
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
