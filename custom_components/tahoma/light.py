"""TaHoma light platform that implements dimmable TaHoma lights."""
import logging
from datetime import timedelta

from homeassistant.components.light import (
    LightEntity,
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    SUPPORT_BRIGHTNESS,
    SUPPORT_EFFECT,
)

from homeassistant.const import STATE_OFF, STATE_ON

from .const import DOMAIN, TAHOMA_TYPES
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma lights from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]

    entities = []
    controller = data.get("controller")

    for device in data.get("devices"):
        if TAHOMA_TYPES[device.uiclass] == "light":
            entities.append(TahomaLight(device, controller))

    async_add_entities(entities)


class TahomaLight(TahomaDevice, LightEntity):
    """Representation of a Tahome light"""

    def __init__(self, tahoma_device, controller):
        super().__init__(tahoma_device, controller)

        self._skip_update = False
        self._effect = None
        self._brightness = None
        self._state = None

    @property
    def brightness(self) -> int:
        """Return the brightness of this light between 0..255."""
        return int(self._brightness * (255 / 100))

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._state

    @property
    def supported_features(self) -> int:
        """Flag supported features."""

        supported_features = 0

        if "setIntensity" in self.tahoma_device.command_definitions:
            supported_features |= SUPPORT_BRIGHTNESS

        if "wink" in self.tahoma_device.command_definitions:
            supported_features |= SUPPORT_EFFECT

        return supported_features

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the light on."""
        self._state = True
        self._skip_update = True

        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = int(float(kwargs[ATTR_BRIGHTNESS]) / 255 * 100)
            self.apply_action("setIntensity", self._brightness)
        elif ATTR_EFFECT in kwargs:
            self._effect = kwargs[ATTR_EFFECT]
            self.apply_action("wink", 100)
        else:
            self.apply_action("on")

        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the light off."""
        self._state = False
        self._skip_update = True
        self.apply_action("off")

        self.async_write_ha_state()

    @property
    def effect_list(self) -> list:
        """Return the list of supported effects."""
        return ["wink"]

    @property
    def effect(self) -> str:
        """Return the current effect."""
        return self._effect

    def update(self):
        """Fetch new state data for this light.
        This is the only method that should fetch new data for Home Assistant.
        """
        # Postpone the immediate state check for changes that take time.
        if self._skip_update:
            self._skip_update = False
            return

        self.controller.get_states([self.tahoma_device])

        if "core:LightIntensityState" in self.tahoma_device.active_states:
            self._brightness = self.tahoma_device.active_states.get(
                "core:LightIntensityState"
            )

        if self.tahoma_device.active_states.get("core:OnOffState") == "on":
            self._state = True
        else:
            self._state = False
