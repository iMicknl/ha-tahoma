"""Support for Somfy Heating Temperature Interface."""
import logging
from typing import Optional

from homeassistant.components.climate import SUPPORT_PRESET_MODE, ClimateEntity
from homeassistant.components.climate.const import (
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_HEAT,
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_OFF,
    PRESET_AWAY,
    PRESET_COMFORT,
    PRESET_ECO,
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
from pyoverkiz.enums import OverkizCommand, OverkizCommandParam, OverkizState

from ..coordinator import OverkizDataUpdateCoordinator
from ..entity import OverkizEntity

_LOGGER = logging.getLogger(__name__)

OVERKIZ_TO_PRESET_MODES = {
    OverkizCommandParam.SECURED: PRESET_AWAY,
    OverkizCommandParam.ECO: PRESET_ECO,
    OverkizCommandParam.COMFORT: PRESET_COMFORT,
    OverkizCommandParam.FREE: PRESET_NONE,
}

PRESET_MODES_TO_OVERKIZ = {v: k for k, v in OVERKIZ_TO_PRESET_MODES.items()}

OVERKIZ_TO_HVAC_MODES = {
    OverkizCommandParam.AUTO: HVAC_MODE_AUTO,
    OverkizCommandParam.MANU: HVAC_MODE_HEAT_COOL,
}

HVAC_MODES_TO_OVERKIZ = {v: k for k, v in OVERKIZ_TO_HVAC_MODES.items()}

OVERKIZ_TO_HVAC_ACTION = {
    OverkizCommandParam.COOLING: CURRENT_HVAC_COOL,
    OverkizCommandParam.HEATING: CURRENT_HVAC_HEAT,
}

MAP_PRESET_TEMPERATURES = {
    PRESET_COMFORT: OverkizState.CORE_COMFORT_ROOM_TEMPERATURE,
    PRESET_ECO: OverkizState.CORE_ECO_ROOM_TEMPERATURE,
    PRESET_AWAY: OverkizState.CORE_SECURED_POSITION_TEMPERATURE,
}


class SomfyHeatingTemperatureInterface(OverkizEntity, ClimateEntity):
    """Representation of Somfy Heating Temperature Interface."""

    _attr_temperature_unit = TEMP_CELSIUS
    _attr_hvac_modes = [*HVAC_MODES_TO_OVERKIZ]
    _attr_preset_modes = [*PRESET_MODES_TO_OVERKIZ]
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
        if self.device.widget != "SomfyHeatingTemperatureInterface":
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
        if (
            self.executor.select_state(OverkizState.CORE_ON_OFF)
            == OverkizCommandParam.OFF
        ):
            return HVAC_MODE_OFF

        if (
            OverkizState.OVP_HEATING_TEMPERATURE_INTERFACE_OPERATING_MODE
            in self.device.states
        ):
            return OVERKIZ_TO_HVAC_MODES[
                self.executor.select_state(
                    OverkizState.OVP_HEATING_TEMPERATURE_INTERFACE_OPERATING_MODE
                )
            ]

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        await self.executor.async_execute_command(
            OverkizCommand.SET_ACTIVE_MODE, HVAC_MODES_TO_OVERKIZ[hvac_mode]
        )

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp."""
        return OVERKIZ_TO_PRESET_MODES[
            self.executor.select_state(
                OverkizState.OVP_HEATING_TEMPERATURE_INTERFACE_SETPOINT_MODE
            )
        ]

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        await self.executor.async_execute_command(
            OverkizCommand.SET_MANU_AND_SET_POINT_MODES,
            PRESET_MODES_TO_OVERKIZ[preset_mode],
        )

    @property
    def hvac_action(self) -> str:
        """Return the current running hvac operation if supported."""
        current_operation = self.executor.select_state(
            OverkizState.OVP_HEATING_TEMPERATURE_INTERFACE_OPERATING_MODE
        )

        if current_operation in OVERKIZ_TO_HVAC_ACTION:
            return OVERKIZ_TO_HVAC_ACTION[current_operation]

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
            OverkizState.OVP_HEATING_TEMPERATURE_INTERFACE_SETPOINT_MODE
        )
        temperature = kwargs.get(ATTR_TEMPERATURE)

        if mode == OverkizCommandParam.COMFORT:
            return await self.executor.async_execute_command(
                OverkizCommand.SET_COMFORT_TEMPERATURE, temperature
            )

        if mode == OverkizCommandParam.ECO:
            return await self.executor.async_execute_command(
                OverkizCommand.SET_ECO_TEMPERATURE, temperature
            )
        if mode == OverkizCommandParam.SECURED:
            return await self.executor.async_execute_command(
                OverkizCommand.SET_SECURED_POSITION_TEMPERATURE, temperature
            )
        return None
