"""Config Flow."""

import logging

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
PROFILE_ID_URL = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
DATA_SCHEMA = vol.Schema(
    {vol.Required("steam_id"): str, vol.Required("steam_web_api_key"): str}
)


class InvalidAPIKey(Exception):
    """Exception raised when api key is invalid."""


class InvalidSteamID(Exception):
    """Exception raised when steam id is invalid."""


async def async_verify_steam_id(api_key: str, steam_id: str) -> None:
    """Verify the provided steam id is valid."""
    async with (
        aiohttp.ClientSession() as session,
        session.get(
            PROFILE_ID_URL, params={"key": api_key, "steamids": steam_id}
        ) as resp,
    ):
        if resp.status == 403:
            raise InvalidAPIKey
        data = await resp.json()

        try:
            return data["response"]["players"][0]["steamid"]
        except (IndexError, KeyError) as err:
            raise InvalidSteamID from err


class SteamWishlistConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Steam wishlist config flow."""

    async def async_step_user(self, user_input):
        """Handle a flow initialized by the user interface."""
        errors = {}
        if user_input is not None:
            steam_id = user_input["steam_id"]
            api_key = user_input["steam_web_api_key"]
            try:
                await async_verify_steam_id(api_key, steam_id)
            except InvalidSteamID:
                errors["base"] = "invalid_steam_id"
            except InvalidAPIKey:
                errors["base"] = "invalid_api_key"

            if not errors:
                return self.async_create_entry(
                    title="Steam Wishlist", data={"steam_id": steam_id, "key": api_key}
                )

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "show_all_wishlist_items",
                        default=self.config_entry.options.get(
                            "show_all_wishlist_items", False
                        ),
                    ): bool
                }
            ),
        )
