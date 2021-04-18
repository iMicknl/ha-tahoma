"""Config flow for TaHoma integration."""
import logging

from aiohttp import ClientError
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from pyhoma.client import TahomaClient
from pyhoma.exceptions import (
    BadCredentialsException,
    MaintenanceException,
    TooManyRequestsException,
)
import voluptuous as vol

from .const import (
    CONF_HUB,
    CONF_UPDATE_INTERVAL,
    DEFAULT_HUB,
    DEFAULT_UPDATE_INTERVAL,
    MIN_UPDATE_INTERVAL,
    SUPPORTED_ENDPOINTS,
)
from .const import DOMAIN  # pylint: disable=unused-import

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Somfy TaHoma."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Start the Somfy TaHoma config flow."""
        self._reauth_entry = None
        self._username = None
        self._password = None
        self._hub = DEFAULT_HUB

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Handle the flow."""
        return OptionsFlowHandler(config_entry)

    async def async_validate_input(self, user_input):
        """Validate user credentials."""
        username = user_input.get(CONF_USERNAME)
        password = user_input.get(CONF_PASSWORD)

        hub = user_input.get(CONF_HUB, DEFAULT_HUB)
        endpoint = SUPPORTED_ENDPOINTS[hub]

        async with TahomaClient(username, password, api_url=endpoint) as client:
            await client.login()

            if not self._reauth_entry:
                return self.async_create_entry(
                    title=username,
                    data=user_input,
                )

            self.hass.config_entries.async_update_entry(
                self._reauth_entry,
                data=user_input,
                unique_id=user_input.get(CONF_USERNAME),
            )

            # Reload the config entry otherwise devices will remain unavailable
            self.hass.async_create_task(
                self.hass.config_entries.async_reload(self._reauth_entry.entry_id)
            )
            return self.async_abort(reason="reauth_successful")

    async def async_step_user(self, user_input=None):
        """Handle the initial step via config flow."""
        errors = {}

        if user_input:
            self._username = user_input[CONF_USERNAME]
            self._hub = user_input[CONF_HUB]

            await self.async_set_unique_id(user_input.get(CONF_USERNAME))

            if not self._reauth_entry:
                self._abort_if_unique_id_configured()

            try:
                return await self.async_validate_input(user_input)
            except TooManyRequestsException:
                errors["base"] = "too_many_requests"
            except BadCredentialsException:
                errors["base"] = "invalid_auth"
            except (TimeoutError, ClientError):
                errors["base"] = "cannot_connect"
            except MaintenanceException:
                errors["base"] = "server_in_maintenance"
            except Exception as exception:  # pylint: disable=broad-except
                errors["base"] = "unknown"
                _LOGGER.exception(exception)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME, default=self._username): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(CONF_HUB, default=self._hub): vol.In(
                        SUPPORTED_ENDPOINTS.keys()
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_import(self, import_config: dict):
        """Handle the initial step via YAML configuration."""
        if not import_config:
            return

        try:
            return await self.async_validate_input(import_config)
        except TooManyRequestsException:
            _LOGGER.error("too_many_requests")
            return self.async_abort(reason="too_many_requests")
        except BadCredentialsException:
            _LOGGER.error("invalid_auth")
            return self.async_abort(reason="invalid_auth")
        except (TimeoutError, ClientError):
            _LOGGER.error("cannot_connect")
            return self.async_abort(reason="cannot_connect")
        except MaintenanceException:
            _LOGGER.error("server_in_maintenance")
            return self.async_abort(reason="server_in_maintenance")
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.exception(exception)
            return self.async_abort(reason="unknown")

    async def async_step_reauth(self, user_input=None):
        """Perform reauth if the user credentials have changed."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        self._username = user_input[CONF_USERNAME]
        self._hub = user_input[CONF_HUB]

        return await self.async_step_user()


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a option flow for Somfy TaHoma."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the Somfy TaHoma options."""
        return await self.async_step_update_interval()

    async def async_step_update_interval(self, user_input=None):
        """Manage the options regarding interval updates."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="update_interval",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_UPDATE_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                        ),
                    ): vol.All(cv.positive_int, vol.Clamp(min=MIN_UPDATE_INTERVAL))
                }
            ),
        )
