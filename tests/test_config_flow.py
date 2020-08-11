"""Test the Somfy TaHoma config flow."""
from asynctest import patch
from custom_components.tahoma import config_flow
from pyhoma.exceptions import BadCredentialsException, TooManyRequestsException

from homeassistant import config_entries, setup

from .common import MockConfigEntry


async def test_form(hass):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    
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
            result["flow_id"],
            {"username": "test@testdomain.com", "password": "test-password"},
        )

    assert result2["type"] == "create_entry"
    assert result2["title"] == "test@testdomain.com"
    assert result2["data"] == {"username": "test@testdomain.com", "password": "test-password"}

    await hass.async_block_till_done()

    assert len(mock_setup.mock_calls) == 1
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_invalid_auth(hass):
    """Test we handle invalid auth."""
    result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch("pyhoma.client.TahomaClient.login", side_effect=BadCredentialsException):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"username": "test@testdomain.com", "password": "test-password"},
        )

    assert result2["type"] == "form"
    assert result2["errors"] == {"base": "invalid_auth"}


async def test_form_too_many_requests(hass):
    """Test we handle too many requests error."""
    result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "pyhoma.client.TahomaClient.login", side_effect=TooManyRequestsException
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"username": "test@testdomain.com", "password": "test-password"},
        )

    assert result2["type"] == "form"
    assert result2["errors"] == {"base": "too_many_requests"}


async def test_form_cannot_connect(hass):
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch("pyhoma.client.TahomaClient.login", side_effect=Exception):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"username": "test@testdomain.com", "password": "test-password"},
        )

    assert result2["type"] == "form"
    assert result2["errors"] == {"base": "unknown"}


async def test_abort_on_duplicate_entry(hass):
    """Test config flow aborts Config Flow on duplicate entries."""
    MockConfigEntry(
        domain=config_flow.DOMAIN, unique_id="test@testdomain.com", data={"username": "test@testdomain.com", "password": "test-password"}
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
            result["flow_id"],
            {"username": "test@testdomain.com", "password": "test-password"},
        )

    assert result2["type"] == "abort"
    assert result2["reason"] == "already_configured"

async def test_allow_multiple_unique_entries(hass):
    """Test config flow allows Config Flow unique entries."""
    MockConfigEntry(
        domain=config_flow.DOMAIN, unique_id="test2@testdomain.com", data={"username": "test2@testdomain.com", "password": "test-password"}
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
            result["flow_id"],
            {"username": "test@testdomain.com", "password": "test-password"},
        )

    assert result2["type"] == "create_entry"
    assert result2["title"] == "test@testdomain.com"
    assert result2["data"] == {"username": "test@testdomain.com", "password": "test-password"}

async def test_import(hass):
    """Test config flow using configuration.yaml."""
    await setup.async_setup_component(hass, "persistent_notification", {})

    with patch("pyhoma.client.TahomaClient.login", return_value=True), patch(
        "custom_components.tahoma.async_setup", return_value=True
    ) as mock_setup, patch(
        "custom_components.tahoma.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        result = await hass.config_entries.flow.async_init(
            config_flow.DOMAIN,
            context={"source": config_entries.SOURCE_IMPORT},
            data={"username": "test@testdomain.nl", "password": "test-password"},
        )
        assert result["type"] == "create_entry"
        assert result["title"] == "test@testdomain.nl"
        assert result["data"] == {
            "username": "test@testdomain.nl",
            "password": "test-password",
        }

        await hass.async_block_till_done()

        assert len(mock_setup.mock_calls) == 1
        assert len(mock_setup_entry.mock_calls) == 1
