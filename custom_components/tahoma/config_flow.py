"""Config flow for TaHoma integration."""
import copy
import logging

from requests.exceptions import RequestException
import voluptuous as vol

from homeassistant import config_entries, core, exceptions
from homeassistant.components.climate.const import (
    PRESET_AWAY,
    PRESET_COMFORT,
    PRESET_ECO,
)
from homeassistant.const import (
    CONF_ENTITY_ID,
    CONF_PASSWORD,
    CONF_USERNAME,
    DEVICE_CLASS_TEMPERATURE,
)
from homeassistant.core import callback

from .const import DOMAIN
from .tahoma_api import TahomaApi

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {vol.Required(CONF_USERNAME): str, vol.Required(CONF_PASSWORD): str}
)


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    username = data.get(CONF_USERNAME)
    password = data.get(CONF_PASSWORD)

    try:
        controller = await hass.async_add_executor_job(TahomaApi, username, password)

    except RequestException:
        _LOGGER.exception("Error when trying to log in to the TaHoma API")
        raise CannotConnect

    return_dict = {"title": username}
    await hass.async_add_executor_job(controller.get_setup)
    devices = await hass.async_add_executor_job(controller.get_devices)
    for key, device in devices.items():
        if device.uiclass == TAHOMA_TYPE_HEATING_SYSTEM:
            if TAHOMA_TYPE_HEATING_SYSTEM not in return_dict:
                return_dict[TAHOMA_TYPE_HEATING_SYSTEM] = {}
            return_dict[TAHOMA_TYPE_HEATING_SYSTEM][device.url] = device.label

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return return_dict


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TaHoma."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the option flow."""
        return ThermoOptionsFlowHandler(config_entry)

    def __init__(self):
        """Initialize the config flow."""
        self._user_input = {}
        self._thermos = {}

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            unique_id = user_input.get(CONF_USERNAME)
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            try:
                info = await validate_input(self.hass, user_input)
                if TAHOMA_TYPE_HEATING_SYSTEM in info:
                    user_input[TAHOMA_TYPE_HEATING_SYSTEM] = info[
                        TAHOMA_TYPE_HEATING_SYSTEM
                    ]
                return self.async_create_entry(title=info["title"], data=user_input)

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


async def validate_options_input(hass: core.HomeAssistant, data):
    """Validate the options user input."""
    for k, v in data.items():
        if k not in [
            "freeze",
            PRESET_AWAY,
            PRESET_ECO,
            PRESET_COMFORT,
        ] and not str.startswith(v, "sensor"):
            _LOGGER.exception("Please select a valid sensor from the list")
            raise InvalidSensor


TAHOMA_TYPE_HEATING_SYSTEM = "HeatingSystem"


class ThermoOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Tahoma options for thermostat."""

    def __init__(self, config_entry):
        """Initialize Tahoma options flow."""
        self.config_entry = config_entry
        self.options = copy.deepcopy(dict(config_entry.options))

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            if not user_input or "no-climate" in user_input:
                return self.async_create_entry(
                    title="", data=dict(self.config_entry.data)
                )
            try:
                await validate_options_input(self.hass, user_input)
                self.options[DEVICE_CLASS_TEMPERATURE] = user_input
                return self.async_create_entry(title="", data=self.options)

            except InvalidSensor:
                errors["base"] = "invalid_sensor"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        if TAHOMA_TYPE_HEATING_SYSTEM in self.config_entry.data:
            available_sensors = []
            for k, v in self.hass.data["entity_registry"].entities.items():
                if (
                    str.startswith(k, "sensor")
                    and v.device_class == DEVICE_CLASS_TEMPERATURE
                ):
                    available_sensors.append(k)
            options = dict(self.config_entry.options)
            schema = {}
            for k, v in self.config_entry.data[TAHOMA_TYPE_HEATING_SYSTEM].items():
                if DEVICE_CLASS_TEMPERATURE not in options:
                    default = None
                else:
                    default = options.get(DEVICE_CLASS_TEMPERATURE).get(k)
                if default is None:
                    default = v
                key = vol.Required(
                    k, default=default, msg="temperature sensor for " + v
                )
                value = vol.In([v] + available_sensors)
                schema[key] = value
            default = {
                "freeze": "",
                PRESET_AWAY: "",
                PRESET_ECO: "",
                PRESET_COMFORT: "",
            }
            if DEVICE_CLASS_TEMPERATURE in options:
                for k, v in options[DEVICE_CLASS_TEMPERATURE].items():
                    if k in default:
                        default[k] = v
            for k, v in default.items():
                schema[vol.Optional(k, default=default[k])] = str

            return self.async_show_form(
                step_id="init", data_schema=vol.Schema(schema), errors=errors
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({vol.Optional("no_climate"): str}),
            errors=errors,
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""


class InvalidSensor(exceptions.HomeAssistantError):
    """Error to indicate the selection is not a sensor."""
