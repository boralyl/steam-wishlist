"""config_flow tests."""
from unittest import mock
from unittest.mock import patch

import pytest

from custom_components.steam_wishlist import config_flow
from homeassistant import config_entries


async def test_flow_init(hass):
    """Test the initial flow."""
    result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": "user"}
    )

    expected = {
        "data_schema": config_flow.DATA_SCHEMA,
        "description_placeholders": None,
        "errors": {},
        "flow_id": mock.ANY,
        "handler": "steam_wishlist",
        "last_step": None,
        "step_id": "user",
        "type": "form",
    }
    assert expected == result


async def test_flow_user_step_no_input(hass):
    """Test appropriate error when no input is provided."""
    _result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": "user"}
    )
    result = await hass.config_entries.flow.async_configure(
        _result["flow_id"], user_input={}
    )
    assert {"base": "missing"} == result["errors"]


async def test_flow_user_step_steam_account_name_invalid(hass):
    """Test appropriate error when steam account name is invalid."""
    _result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": "user"}
    )
    with patch("custom_components.steam_wishlist.config_flow.async_get_user_url") as p:
        p.side_effect = ValueError
        result = await hass.config_entries.flow.async_configure(
            _result["flow_id"], user_input={"steam_account_name": "bad"}
        )
    assert {"base": "invalid_user"} == result["errors"]


async def test_flow_user_step_steam_account_name_success(hass):
    """Test flow success for a valid steam account name."""
    _result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": "user"}
    )
    with patch("custom_components.steam_wishlist.config_flow.async_get_user_url") as p:
        p.return_value = config_flow.WISHLIST_JSON_URL.format(user_id="1234567890")
        result = await hass.config_entries.flow.async_configure(
            _result["flow_id"], user_input={"steam_account_name": "good"}
        )
    expected = {
        "version": 1,
        "type": "create_entry",
        "flow_id": mock.ANY,
        "handler": "steam_wishlist",
        "title": "Steam Wishlist",
        "data": {"url": config_flow.WISHLIST_JSON_URL.format(user_id="1234567890")},
        "description": None,
        "description_placeholders": None,
        "options": {},
        "result": mock.ANY,
    }
    assert expected == result
    actual_config_entry: config_entries.ConfigEntry = result["result"]
    assert "steam_wishlist" == actual_config_entry.unique_id


async def test_flow_user_step_steam_profile_id_invalid(hass):
    """Test appropriate error when steam profile id is invalid."""
    _result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": "user"}
    )
    with patch(
        "custom_components.steam_wishlist.config_flow.async_check_profile_id_valid"
    ) as p:
        p.return_value = False
        result = await hass.config_entries.flow.async_configure(
            _result["flow_id"], user_input={"steam_profile_id": "0"}
        )
    assert {"base": "invalid_profile_id"} == result["errors"]


async def test_flow_user_step_steam_profile_id_success(hass):
    """Test flow success for a valid steam profile id."""
    _result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": "user"}
    )
    with patch(
        "custom_components.steam_wishlist.config_flow.async_check_profile_id_valid"
    ) as p:
        p.return_value = True
        result = await hass.config_entries.flow.async_configure(
            _result["flow_id"], user_input={"steam_profile_id": "1234567890"}
        )
    expected = {
        "version": 1,
        "type": "create_entry",
        "flow_id": mock.ANY,
        "handler": "steam_wishlist",
        "title": "Steam Wishlist",
        "data": {"url": config_flow.WISHLIST_JSON_URL.format(user_id="1234567890")},
        "description": None,
        "description_placeholders": None,
        "options": {},
        "result": mock.ANY,
    }
    assert expected == result
    actual_config_entry: config_entries.ConfigEntry = result["result"]
    assert "steam_wishlist" == actual_config_entry.unique_id


async def test_async_check_profile_id_valid_is_valid(mock_aioresponse):
    """Test return value when profile id is valid."""
    profile_id = "123"
    mock_aioresponse.get(config_flow.PROFILE_ID_URL.format(steam_profile_id=profile_id))

    assert await config_flow.async_check_profile_id_valid(profile_id) is True


async def test_async_check_profile_id_valid_is_invalid(mock_aioresponse):
    """Test return value when profile id is invalid."""
    profile_id = "123"
    mock_aioresponse.get(
        config_flow.PROFILE_ID_URL.format(steam_profile_id=profile_id), status=500
    )

    assert await config_flow.async_check_profile_id_valid(profile_id) is False


async def test_async_get_user_url_invalid_raises_valueerror(mock_aioresponse):
    """Test ValueError raised when username is invalid."""
    username = "bad"
    mock_aioresponse.get(
        config_flow.WISHLIST_URL.format(username=username), body="<html></html>"
    )
    with pytest.raises(ValueError):
        await config_flow.async_get_user_url(username)


async def test_async_get_user_url_returns_json_url(mock_aioresponse):
    """Test json url returned on success."""
    username = "bad"
    body = r"""
    <html>
      <head>
      <script>
	    var g_strWishlistBaseURL = "https:\/\/store.steampowered.com\/wishlist\/profiles\/1234567890\/";
      </script>
      </head>
    </html>"""  # noqa
    mock_aioresponse.get(config_flow.WISHLIST_URL.format(username=username), body=body)
    actual = await config_flow.async_get_user_url(username)
    expected = config_flow.WISHLIST_JSON_URL.format(user_id="1234567890")
    assert expected == actual
