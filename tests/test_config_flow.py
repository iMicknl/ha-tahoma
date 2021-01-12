"""Test the Somfy TaHoma config flow."""
from aiohttp import ClientError
from asynctest import patch
from homeassistant import config_entries
from homeassistant.config_entries import ENTRY_STATE_LOADED
from pyhoma.exceptions import BadCredentialsException, TooManyRequestsException
import pytest

from custom_components.tahoma import config_flow
from custom_components.tahoma.const import DOMAIN

from .common import MockConfigEntry

TEST_EMAIL = "test@testdomain.com"
TEST_PASSWORD = "test-password"
DEFAULT_HUB = "Somfy TaHoma"


async def test_form(hass):
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == "form"
    assert result["errors"] == {}

    with patch("pyhoma.client.TahomaClient.login", return_value=True), patch(
        "custom_components.tahoma.async_setup", return_value=True
    ) as mock_setup, patch(
        "custom_components.tahoma.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"username": TEST_EMAIL, "password": TEST_PASSWORD, "hub": DEFAULT_HUB},
        )

    assert result2["type"] == "create_entry"
    assert result2["title"] == TEST_EMAIL
    assert result2["data"] == {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "hub": DEFAULT_HUB
    }

    await hass.async_block_till_done()

    assert len(mock_setup.mock_calls) == 1
    assert len(mock_setup_entry.mock_calls) == 1


@pytest.mark.parametrize(
    "side_effect, error",
    [
        (BadCredentialsException, "invalid_auth"),
        (TooManyRequestsException, "too_many_requests"),
        (TimeoutError, "cannot_connect"),
        (ClientError, "cannot_connect"),
        (Exception, "unknown"),
    ],
)
async def test_form_invalid(hass, side_effect, error):
    """Test we handle invalid auth."""
    result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch("pyhoma.client.TahomaClient.login", side_effect=side_effect):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"username": TEST_EMAIL, "password": TEST_PASSWORD, "hub": DEFAULT_HUB},
        )

    assert result2["type"] == "form"
    assert result2["errors"] == {"base": error}


async def test_abort_on_duplicate_entry(hass):
    """Test config flow aborts Config Flow on duplicate entries."""
    MockConfigEntry(
        domain=config_flow.DOMAIN,
        unique_id=TEST_EMAIL,
        data={"username": TEST_EMAIL, "password": TEST_PASSWORD, "hub": DEFAULT_HUB},
    ).add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch("pyhoma.client.TahomaClient.login", return_value=True), patch(
        "custom_components.tahoma.async_setup", return_value=True
    ) as mock_setup, patch(
        "custom_components.tahoma.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"username": TEST_EMAIL, "password": TEST_PASSWORD, "hub": DEFAULT_HUB},
        )

    assert result2["type"] == "abort"
    assert result2["reason"] == "already_configured"


async def test_allow_multiple_unique_entries(hass):
    """Test config flow allows Config Flow unique entries."""
    MockConfigEntry(
        domain=config_flow.DOMAIN,
        unique_id="test2@testdomain.com",
        data={"username": "test2@testdomain.com", "password": TEST_PASSWORD, "hub": DEFAULT_HUB},
    ).add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch("pyhoma.client.TahomaClient.login", return_value=True), patch(
        "custom_components.tahoma.async_setup", return_value=True
    ) as mock_setup, patch(
        "custom_components.tahoma.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"username": TEST_EMAIL, "password": TEST_PASSWORD, "hub": DEFAULT_HUB},
        )

    assert result2["type"] == "create_entry"
    assert result2["title"] == TEST_EMAIL
    assert result2["data"] == {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "hub": DEFAULT_HUB
    }


async def test_import(hass):
    """Test config flow using configuration.yaml."""
    with patch("pyhoma.client.TahomaClient.login", return_value=True), patch(
        "custom_components.tahoma.async_setup", return_value=True
    ) as mock_setup, patch(
        "custom_components.tahoma.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        result = await hass.config_entries.flow.async_init(
            config_flow.DOMAIN,
            context={"source": config_entries.SOURCE_IMPORT},
            data={"username": TEST_EMAIL, "password": TEST_PASSWORD, "hub": DEFAULT_HUB},
        )
        assert result["type"] == "create_entry"
        assert result["title"] == TEST_EMAIL
        assert result["data"] == {
            "username": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "hub": DEFAULT_HUB
        }

        await hass.async_block_till_done()

        assert len(mock_setup.mock_calls) == 1
        assert len(mock_setup_entry.mock_calls) == 1


@pytest.mark.parametrize(
    "side_effect, error",
    [
        (BadCredentialsException, "invalid_auth"),
        (TooManyRequestsException, "too_many_requests"),
        (TimeoutError, "cannot_connect"),
        (ClientError, "cannot_connect"),
        (Exception, "unknown"),
    ],
)
async def test_import_failing(hass, side_effect, error):
    """Test failing config flow using configuration.yaml."""
    with patch("pyhoma.client.TahomaClient.login", side_effect=side_effect):
        await hass.config_entries.flow.async_init(
            config_flow.DOMAIN,
            context={"source": config_entries.SOURCE_IMPORT},
            data={"username": TEST_EMAIL, "password": TEST_PASSWORD, "hub": DEFAULT_HUB},
        )

    # Should write Exception to the log


async def test_options_flow(hass):
    """Test options flow."""

    entry = MockConfigEntry(
        domain=config_flow.DOMAIN,
        unique_id=TEST_EMAIL,
        data={"username": TEST_EMAIL, "password": TEST_PASSWORD, "hub": DEFAULT_HUB},
    )

    with patch("pyhoma.client.TahomaClient.login", return_value=True), patch(
        "custom_components.tahoma.async_setup", return_value=True
    ) as mock_setup, patch(
        "custom_components.tahoma.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
    assert entry.state == ENTRY_STATE_LOADED

    result = await hass.config_entries.options.async_init(
        entry.entry_id, context={"source": "test"}, data=None
    )
    assert result["type"] == "form"
    assert result["step_id"] == "update_interval"

    assert entry.options == {}

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"update_interval": 12000,},
    )

    assert entry.options == {"update_interval": 12000}
