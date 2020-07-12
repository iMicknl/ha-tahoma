"""TaHoma light platform that implements dimmable TaHoma lights."""
from datetime import timedelta
import logging

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_HS_COLOR,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR,
    SUPPORT_EFFECT,
    LightEntity,
)
from homeassistant.const import STATE_ON
import homeassistant.util.color as color_util

from .const import COMMAND_OFF, COMMAND_ON, CORE_ON_OFF_STATE, DOMAIN, TAHOMA_TYPES
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)

COMMAND_SET_INTENSITY = "setIntensity"
COMMAND_WINK = "wink"
COMMAND_SET_RGB = "setRGB"

CORE_BLUE_COLOR_INTENSITY_STATE = "core:BlueColorIntensityState"
CORE_GREEN_COLOR_INTENSITY_STATE = "core:GreenColorIntensityState"
CORE_LIGHT_INTENSITY_STATE = "core:LightIntensityState"
CORE_RED_COLOR_INTENSITY_STATE = "core:RedColorIntensityState"


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma lights from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]
    controller = data.get("controller")

    entities = [
        TahomaLight(device, controller)
        for device in data.get("devices")
        if TAHOMA_TYPES[device.uiclass] == "light"
    ]

    async_add_entities(entities)


class TahomaLight(TahomaDevice, LightEntity):
    """Representation of a Tahome light."""

    def __init__(self, tahoma_device, controller):
        """Initialize a device."""
        super().__init__(tahoma_device, controller)
        self._effect = None

    @property
    def brightness(self) -> int:
        """Return the brightness of this light between 0..255."""
        states = self.tahoma_device.active_states
        brightness = states.get(CORE_LIGHT_INTENSITY_STATE)
        return int(brightness * 255 / 100)

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        states = self.tahoma_device.active_states
        return states.get(CORE_ON_OFF_STATE) == STATE_ON

    @property
    def hs_color(self):
        """Return the hue and saturation color value [float, float]."""
        states = self.tahoma_device.active_states

        [r, g, b] = [
            states.get(CORE_RED_COLOR_INTENSITY_STATE),
            states.get(CORE_GREEN_COLOR_INTENSITY_STATE),
            states.get(CORE_BLUE_COLOR_INTENSITY_STATE),
        ]
        return None if None in [r, g, b] else color_util.color_RGB_to_hs(r, g, b)

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        supported_features = 0

        if COMMAND_SET_INTENSITY in self.tahoma_device.command_definitions:
            supported_features |= SUPPORT_BRIGHTNESS

        if COMMAND_WINK in self.tahoma_device.command_definitions:
            supported_features |= SUPPORT_EFFECT

        if COMMAND_SET_RGB in self.tahoma_device.command_definitions:
            supported_features |= SUPPORT_COLOR

        return supported_features

    def turn_on(self, **kwargs) -> None:
        """Turn the light on."""
        if ATTR_HS_COLOR in kwargs:
            self.apply_action(
                COMMAND_SET_RGB,
                *[
                    int(float(c))
                    for c in color_util.color_hs_to_RGB(*kwargs[ATTR_HS_COLOR])
                ],
            )

        if ATTR_BRIGHTNESS in kwargs:
            brightness = int(float(kwargs[ATTR_BRIGHTNESS]) / 255 * 100)
            self.apply_action(COMMAND_SET_INTENSITY, brightness)

        elif ATTR_EFFECT in kwargs:
            self._effect = kwargs[ATTR_EFFECT]
            self.apply_action(self._effect, 100)

        else:
            self.apply_action(COMMAND_ON)

        self.async_write_ha_state()

    def turn_off(self, **kwargs) -> None:
        """Turn the light off."""
        self.apply_action(COMMAND_OFF)

    @property
    def effect_list(self) -> list:
        """Return the list of supported effects."""
        return [COMMAND_WINK]

    @property
    def effect(self) -> str:
        """Return the current effect."""
        return self._effect
