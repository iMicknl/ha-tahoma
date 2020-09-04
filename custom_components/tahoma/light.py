"""TaHoma light platform that implements dimmable TaHoma lights."""
import logging

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_HS_COLOR,
    DOMAIN as LIGHT,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR,
    SUPPORT_EFFECT,
    LightEntity,
)
from homeassistant.const import STATE_ON
from homeassistant.helpers import entity_platform
import homeassistant.util.color as color_util

from .const import COMMAND_OFF, COMMAND_ON, CORE_ON_OFF_STATE, DOMAIN
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

COMMAND_MY = "my"
COMMAND_SET_INTENSITY = "setIntensity"
COMMAND_SET_RGB = "setRGB"
COMMAND_WINK = "wink"

CORE_BLUE_COLOR_INTENSITY_STATE = "core:BlueColorIntensityState"
CORE_GREEN_COLOR_INTENSITY_STATE = "core:GreenColorIntensityState"
CORE_LIGHT_INTENSITY_STATE = "core:LightIntensityState"
CORE_RED_COLOR_INTENSITY_STATE = "core:RedColorIntensityState"

SERVICE_LIGHT_MY_POSITION = "set_light_my_position"

SUPPORT_MY = 512


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma lights from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities = [
        TahomaLight(device.deviceurl, coordinator)
        for device in data["entities"].get(LIGHT)
    ]

    async_add_entities(entities)

    platform = entity_platform.current_platform.get()
    platform.async_register_entity_service(
        SERVICE_LIGHT_MY_POSITION, {}, "async_my", [SUPPORT_MY]
    )


class TahomaLight(TahomaDevice, LightEntity):
    """Representation of a TaHoma Light."""

    def __init__(self, tahoma_device, controller):
        """Initialize a device."""
        super().__init__(tahoma_device, controller)
        self._effect = None

    @property
    def brightness(self) -> int:
        """Return the brightness of this light between 0..255."""
        brightness = self.select_state(CORE_LIGHT_INTENSITY_STATE)
        return int(brightness * 255 / 100)

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self.select_state(CORE_ON_OFF_STATE) == STATE_ON

    @property
    def hs_color(self):
        """Return the hue and saturation color value [float, float]."""
        r = self.select_state(CORE_RED_COLOR_INTENSITY_STATE)
        g = self.select_state(CORE_GREEN_COLOR_INTENSITY_STATE)
        b = self.select_state(CORE_BLUE_COLOR_INTENSITY_STATE)
        return None if None in [r, g, b] else color_util.color_RGB_to_hs(r, g, b)

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        supported_features = 0

        if self.has_command(COMMAND_SET_INTENSITY):
            supported_features |= SUPPORT_BRIGHTNESS

        if self.has_command(COMMAND_WINK):
            supported_features |= SUPPORT_EFFECT

        if self.has_command(COMMAND_SET_RGB):
            supported_features |= SUPPORT_COLOR

        if self.has_command(COMMAND_MY):
            supported_features |= SUPPORT_MY

        return supported_features

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the light on."""
        if ATTR_HS_COLOR in kwargs:
            await self.async_execute_command(
                COMMAND_SET_RGB,
                *[
                    int(float(c))
                    for c in color_util.color_hs_to_RGB(*kwargs[ATTR_HS_COLOR])
                ],
            )

        if ATTR_BRIGHTNESS in kwargs:
            brightness = int(float(kwargs[ATTR_BRIGHTNESS]) / 255 * 100)
            await self.async_execute_command(COMMAND_SET_INTENSITY, brightness)

        elif ATTR_EFFECT in kwargs:
            self._effect = kwargs[ATTR_EFFECT]
            await self.async_execute_command(self._effect, 100)

        else:
            await self.async_execute_command(COMMAND_ON)

    async def async_turn_off(self, **_) -> None:
        """Turn the light off."""
        await self.async_execute_command(COMMAND_OFF)

    async def async_my(self, **_):
        """Set light to preset position."""
        await self.async_execute_command(COMMAND_MY)

    @property
    def effect_list(self) -> list:
        """Return the list of supported effects."""
        return [COMMAND_WINK] if self.has_command(COMMAND_WINK) else None

    @property
    def effect(self) -> str:
        """Return the current effect."""
        return self._effect
