"""Support for TaHoma climate devices."""
import logging
from typing import List, Optional

from homeassistant.components.climate import (
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_PRESET_MODE,
    ClimateEntity,
)
from homeassistant.components.climate.const import (
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_NONE,
)
from homeassistant.const import TEMP_CELSIUS

from .const import DOMAIN, TAHOMA_TYPES
from .tahoma_device import TahomaDevice

_LOGGER = logging.getLogger(__name__)

AEH = "AtlanticElectricalHeater"
SUPPORTED_CLIMATE_DEVICES = [AEH]

#  AEH constants
COMMAND_SET_HEATING_LEVEL = "setHeatingLevel"

IO_TARGET_HEATING_LEVEL_STATE = "io:TargetHeatingLevelState"

PRESET_FREEZE = "freeze"
PRESET_FROST_PROTECTION = "frostprotection"
PRESET_OFF = "off"


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the TaHoma climate from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]
    controller = data.get("controller")

    climate_devices = [
        d for d in data.get("devices") if TAHOMA_TYPES[d.uiclass] == "climate"
    ]

    entities = []
    for device in climate_devices:
        if device.widget == AEH:
            entities.append(AtlanticElectricalHeater(device, controller))

    async_add_entities(entities)


class AtlanticElectricalHeater(TahomaDevice, ClimateEntity):
    """Representation of a Tahome climate entity."""

    def __init__(self, device, controller):
        """Init method."""
        super().__init__(device, controller)
        self._preset_mode = None
        self._hvac_mode = None

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_PRESET_MODE

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        return self._hvac_mode

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return [HVAC_MODE_HEAT, HVAC_MODE_OFF]

    def set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        modes = {HVAC_MODE_HEAT: PRESET_COMFORT, HVAC_MODE_OFF: PRESET_OFF}
        self.apply_action(COMMAND_SET_HEATING_LEVEL, modes[hvac_mode])
        self._hvac_mode = hvac_mode
        self._preset_mode = (
            PRESET_NONE if hvac_mode == HVAC_MODE_OFF else PRESET_COMFORT
        )

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp."""
        return self._preset_mode

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes."""
        return [PRESET_NONE, PRESET_FREEZE, PRESET_ECO, PRESET_COMFORT]

    def set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        modes = {
            PRESET_NONE: PRESET_OFF,
            PRESET_FREEZE: PRESET_FROST_PROTECTION,
            PRESET_ECO: PRESET_ECO,
            PRESET_COMFORT: PRESET_COMFORT,
        }
        self.apply_action(COMMAND_SET_HEATING_LEVEL, modes[preset_mode])
        self._hvac_mode = (
            HVAC_MODE_OFF if preset_mode == PRESET_NONE else HVAC_MODE_HEAT
        )
        self._preset_mode = preset_mode

    def turn_off(self) -> None:
        """Turn off the device."""
        self.apply_action(COMMAND_SET_HEATING_LEVEL, PRESET_OFF)
        self._hvac_mode = HVAC_MODE_OFF
        self._preset_mode = PRESET_NONE
