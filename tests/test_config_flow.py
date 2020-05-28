from unittest import mock

from custom_components.steam_wishlist import config_flow

from .async_mock import patch


async def test_flow_init(hass):
    result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": "user"}
    )

    expected = {
        "data_schema": config_flow.DATA_SCHEMA,
        "description_placeholders": None,
        "errors": {},
        "flow_id": mock.ANY,
        "handler": "steam_wishlist",
        "step_id": "user",
        "type": "form",
    }
    assert expected == result


async def test_flow_user_step_no_input(hass):
    _result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": "user"}
    )
    result = await hass.config_entries.flow.async_configure(
        _result["flow_id"], user_input={}
    )
    assert {"base": "missing"} == result["errors"]


async def test_flow_user_step_steam_account_name_invalid(hass):
    _result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": "user"}
    )
    with patch("custom_components.steam_wishlist.config_flow.async_get_user_url") as p:
        p.side_effect = ValueError
        result = await hass.config_entries.flow.async_configure(
            _result["flow_id"], user_input={"steam_account_name": "bad"}
        )
    assert {"base": "invalid_user"} == result["errors"]
