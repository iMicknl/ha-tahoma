"""Support for AtlanticHeatRecoveryVentilation."""

import logging
from typing import List, Optional

from homeassistant.components.climate import (
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    SUPPORT_FAN_MODE,
    SUPPORT_PRESET_MODE,
    ClimateEntity,
)
from homeassistant.components.climate.const import (
    FAN_AUTO,
    FAN_HIGH,
    PRESET_COMFORT,
    PRESET_ECO,
)
from homeassistant.const import EVENT_HOMEASSISTANT_START, STATE_UNKNOWN, TEMP_CELSIUS
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_change

from ..coordinator import TahomaDataUpdateCoordinator
from ..tahoma_entity import TahomaEntity

FAN_BOOST = "boost"
FAN_AWAY = "away"

PRESET_PROG = "prog"
PRESET_MANUAL = "manual"

COMMAND_SET_AIR_DEMAND_MODE = "setAirDemandMode"
COMMAND_SET_VENTILATION_CONFIGURATION_MODE = "setVentilationConfigurationMode"
COMMAND_SET_VENTILATION_MODE = "setVentilationMode"

IO_AIR_DEMAND_MODE_STATE = "io:AirDemandModeState"

FAN_MODE_TO_TAHOMA = {
    FAN_AUTO: "auto",
    FAN_BOOST: "boost",
    FAN_HIGH: "high",
    FAN_AWAY: "away",
}

TAHOMA_TO_FAN_MODE = {v: k for k, v in FAN_MODE_TO_TAHOMA.items()}

HVAC_MODES = [HVAC_MODE_COOL, HVAC_MODE_HEAT]
PRESET_MODES = [PRESET_COMFORT, PRESET_ECO, PRESET_PROG, PRESET_MANUAL]
_LOGGER = logging.getLogger(__name__)


class AtlanticHeatRecoveryVentilation(TahomaEntity, ClimateEntity):
    """Representation of a AtlanticHeatRecoveryVentilation device."""

    def __init__(self, device_url: str, coordinator: TahomaDataUpdateCoordinator):
        """Init method."""
        super().__init__(device_url, coordinator)

        self._temp_sensor_entity_id = None
        self._current_temperature = None

    async def async_added_to_hass(self):
        """Register temperature sensor after added to hass."""
        await super().async_added_to_hass()

        base_url = self.get_base_device_url()
        entity_registry = await self.hass.helpers.entity_registry.async_get_registry()
        self._temp_sensor_entity_id = next(
            (
                entity_id
                for entity_id, entry in entity_registry.entities.items()
                if entry.unique_id == f"{base_url}#4"
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
    def current_temperature(self) -> Optional[float]:
        """Return the current temperature."""
        return self._current_temperature

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return SUPPORT_PRESET_MODE | SUPPORT_FAN_MODE

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        state = self.select_state("io:VentilationModeState")
        _LOGGER.debug(state)
        cooling = state.get("cooling")

        if cooling == "on":
            return HVAC_MODE_COOL
        else:
            return HVAC_MODE_HEAT

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return HVAC_MODES

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVAC_MODE_COOL:
            await self.async_execute_command(
                COMMAND_SET_VENTILATION_MODE, {"cooling": "on"}
            )

        if hvac_mode == HVAC_MODE_HEAT:
            await self.async_execute_command(
                COMMAND_SET_VENTILATION_MODE, {"cooling": "off"}
            )

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., auto, smart, interval, favorite."""
        state_ventilation_configuration = self.select_state(
            "io:VentilationConfigurationModeState"
        )
        state_ventilation_mode = self.select_state("io:VentilationModeState")
        state_prog = state_ventilation_mode.get("prog")

        if state_prog == "on":
            return PRESET_PROG

        if state_ventilation_configuration == "comfort":
            return PRESET_COMFORT

        if state_ventilation_configuration == "manual":
            return PRESET_MANUAL

        if state_ventilation_configuration == "eco":
            return PRESET_ECO

        return None

    @property
    def preset_modes(self) -> Optional[List[str]]:
        """Return a list of available preset modes."""
        return PRESET_MODES

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""

        if preset_mode == PRESET_COMFORT:
            await self.async_execute_command(
                COMMAND_SET_VENTILATION_CONFIGURATION_MODE, "comfort"
            )
            await self.async_execute_command(
                COMMAND_SET_VENTILATION_MODE, {"prog": "off"}
            )

        if preset_mode == PRESET_PROG:
            await self.async_execute_command(
                COMMAND_SET_VENTILATION_CONFIGURATION_MODE, "standard"
            )
            await self.async_execute_command(
                COMMAND_SET_VENTILATION_MODE, {"prog": "on"}
            )

        if preset_mode == PRESET_MANUAL:
            await self.async_execute_command(
                COMMAND_SET_VENTILATION_CONFIGURATION_MODE, "standard"
            )
            await self.async_execute_command(
                COMMAND_SET_VENTILATION_MODE, {"prog": "off"}
            )

        if preset_mode == PRESET_ECO:
            await self.async_execute_command(
                COMMAND_SET_VENTILATION_CONFIGURATION_MODE, "eco"
            )
            await self.async_execute_command(
                COMMAND_SET_VENTILATION_MODE, {"prog": "off"}
            )

    @property
    def fan_mode(self) -> Optional[str]:
        """Return the fan setting."""
        return TAHOMA_TO_FAN_MODE[self.select_state(IO_AIR_DEMAND_MODE_STATE)]

    @property
    def fan_modes(self) -> Optional[List[str]]:
        """Return the list of available fan modes."""
        return [*FAN_MODE_TO_TAHOMA]

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        await self.async_execute_command(
            COMMAND_SET_AIR_DEMAND_MODE, FAN_MODE_TO_TAHOMA[fan_mode]
        )
