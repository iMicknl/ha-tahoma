"""Support for Atlantic Electrical Heater."""
import logging
from typing import Optional

from homeassistant.components.climate import SUPPORT_PRESET_MODE, ClimateEntity
from homeassistant.components.climate.const import (
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_HEAT,
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_OFF,
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_AWAY,
    PRESET_NONE,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    EVENT_HOMEASSISTANT_START,
    STATE_UNKNOWN,
    TEMP_CELSIUS,
)
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_change

from ..coordinator import OverkizDataUpdateCoordinator
from ..entity import OverkizEntity

_LOGGER = logging.getLogger(__name__)

COMMAND_SET_HEATING_LEVEL = "setHeatingLevel"

CORE_OPERATING_MODE_STATE = "ovp:HeatingTemperatureInterfaceActiveModeState"
CORE_TARGET_TEMPERATURE_STATE = "core:TargetTemperatureState"
CORE_ON_OFF_STATE = "core:OnOffState"
IO_TARGET_HEATING_LEVEL_STATE = "io:TargetHeatingLevelState"

# PRESET_FROST_PROTECTION = "frost_protection"

TAHOMA_TO_PRESET_MODES = {
    "secured": PRESET_AWAY,
    "eco": PRESET_ECO,
    "comfort": PRESET_COMFORT,
    "free": PRESET_NONE,
}

PRESET_MODES_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_PRESET_MODES.items()}

TAHOMA_TO_HVAC_MODES = {
    "auto": HVAC_MODE_AUTO,
    "manu": HVAC_MODE_HEAT_COOL,
}

HVAC_MODES_TO_TAHOMA = {v: k for k, v in TAHOMA_TO_HVAC_MODES.items()}

TAHOMA_TO_HVAC_ACTION = {"cooling": CURRENT_HVAC_COOL, "heating": CURRENT_HVAC_HEAT}

MAP_PRESET_TEMPERATURES = {
    PRESET_COMFORT: "core:ComfortRoomTemperatureState",
    PRESET_ECO: "core:EcoRoomTemperatureState",
    PRESET_AWAY: "core:SecuredPositionTemperatureState",
}


class SomfyHeatingTemperatureInterface(OverkizEntity, ClimateEntity):
    """Representation of Somfy Heating Temperature Interface."""

    _attr_temperature_unit = TEMP_CELSIUS
    _attr_hvac_modes = [*HVAC_MODES_TO_TAHOMA]
    _attr_preset_modes = [*PRESET_MODES_TO_TAHOMA]
    _attr_supported_features = SUPPORT_PRESET_MODE

    def __init__(self, device_url: str, coordinator: OverkizDataUpdateCoordinator):
        """Init method."""
        super().__init__(device_url, coordinator)
        self._temp_sensor_entity_id = None
        self._current_temperature = None

    async def async_added_to_hass(self):
        """Register temperature sensor after added to hass."""
        await super().async_added_to_hass()

        # Only the AtlanticElectricarHeater WithAdjustableTemperatureSetpoint has a separate temperature sensor
        if (
            self.device.widget
            != "SomfyHeatingTemperatureInterface"
        ):
            _LOGGER.error("No somfy heating widget !")
            return

        entity_registry = await self.hass.helpers.entity_registry.async_get_registry()
        self._temp_sensor_entity_id = next(
            (
                entity_id
                for entity_id, entry in entity_registry.entities.items()
                if entry.unique_id == f"{self.base_device_url}#2-core:TemperatureState"
            ),
            None,
        )

        if self._temp_sensor_entity_id:
            async_track_state_change(
                self.hass, self._temp_sensor_entity_id, self._async_temp_sensor_changed
            )

        else:
            _LOGGER.warning(
                "Temperature sensor could not be found for entity %s", self.name
            )

        @callback
        def _async_startup(event):
            """Init on startup."""
            if self._temp_sensor_entity_id:
                temp_sensor_state = self.hass.states.get(self._temp_sensor_entity_id)
                if temp_sensor_state and temp_sensor_state.state != STATE_UNKNOWN:
                    self.update_temp(temp_sensor_state)

        self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, _async_startup)

        self.schedule_update_ha_state(True)

    async def _async_temp_sensor_changed(self, entity_id, old_state, new_state) -> None:
        """Handle temperature changes."""
        if new_state is None or old_state == new_state:
            return

        self.update_temp(new_state)
        self.schedule_update_ha_state()

    @callback
    def update_temp(self, state):
        """Update thermostat with latest state from sensor."""
        if state is None or state.state == STATE_UNKNOWN:
            return

        try:
            self._current_temperature = float(state.state)
        except ValueError as ex:
            _LOGGER.error("Unable to update from sensor: %s", ex)

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        if CORE_ON_OFF_STATE in self.device.states:
            if self.executor.select_state(CORE_ON_OFF_STATE) == "off":
                return HVAC_MODE_OFF

        if CORE_OPERATING_MODE_STATE in self.device.states:
            return TAHOMA_TO_HVAC_MODES[
                self.executor.select_state(CORE_OPERATING_MODE_STATE)
            ]

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        await self.executor.async_execute_command(
            "setActiveMode", HVAC_MODES_TO_TAHOMA[hvac_mode]
        )

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp."""
        return TAHOMA_TO_PRESET_MODES[
            self.executor.select_state(
                "ovp:HeatingTemperatureInterfaceSetPointModeState"
            )
        ]

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        await self.executor.async_execute_command(
            "setManuAndSetPointModes", PRESET_MODES_TO_TAHOMA[preset_mode]
        )

    @property
    def hvac_action(self) -> str:
        """Return the current running hvac operation if supported."""
        current_operation = self.executor.select_state(
            "ovp:HeatingTemperatureInterfaceOperatingModeState"
        )

        if current_operation in TAHOMA_TO_HVAC_ACTION:
            return TAHOMA_TO_HVAC_ACTION[current_operation]

    @property
    def target_temperature(self) -> Optional[float]:
        """Return the temperature."""
        if self.hvac_mode == HVAC_MODE_AUTO:
            if self.preset_mode == PRESET_NONE:
                return None
            return self.executor.select_state(MAP_PRESET_TEMPERATURES[self.preset_mode])
        return None

    @property
    def current_temperature(self) -> Optional[float]:
        """Return the current temperature."""
        return self._current_temperature

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new temperature."""

        mode = self.executor.select_state(
            "ovp:HeatingTemperatureInterfaceSetPointModeState"
        )
        temperature = kwargs.get(ATTR_TEMPERATURE)

        if mode == "comfort":
            return await self.executor.async_execute_command(
                "setComfortTemperature", temperature
            )

        if mode == "eco":
            return await self.executor.async_execute_command(
                "setEcoTemperature", temperature
            )
        if mode == "secured":
            return await self.executor.async_execute_command(
                "setSecuredPositionTemperature", temperature
            )
        return None
