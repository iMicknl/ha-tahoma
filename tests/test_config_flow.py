"""Test the Somfy TaHoma config flow."""
from asynctest import patch
from custom_components.tahoma import config_flow
from pyhoma.exceptions import BadCredentialsException, TooManyRequestsException

from homeassistant import config_entries, setup


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
            {"username": "test-username", "password": "test-password"},
        )

    print(result2)

    assert result2["type"] == "create_entry"
    assert result2["title"] == "test-username"
    assert result2["data"] == {"username": "test-username", "password": "test-password"}
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
            {"username": "test-username", "password": "test-password"},
        )

    assert result2["type"] == "form"
    assert result2["errors"] == {"base": "invalid_auth"}


async def test_form_too_many_requests(hass):
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "pyhoma.client.TahomaClient.login", side_effect=TooManyRequestsException
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"username": "test-username", "password": "test-password"},
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
            {"username": "test-username", "password": "test-password"},
        )

    assert result2["type"] == "form"
    assert result2["errors"] == {"base": "unknown"}
