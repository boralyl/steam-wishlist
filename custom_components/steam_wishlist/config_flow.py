import logging
import re

import aiohttp
import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
PROFILE_ID_URL = "https://store.steampowered.com/wishlist/profiles/{steam_profile_id}/"
WISHLIST_URL = "https://store.steampowered.com/wishlist/id/{username}/"
WISHLIST_JSON_URL = (
    "https://store.steampowered.com/wishlist/profiles/{user_id}/wishlistdata/"
)

ONE_PROFILE_ERROR_MSG = "Enter either a steam account name or a steam profile id."
DATA_SCHEMA = vol.Schema(
    {vol.Optional("steam_account_name"): str, vol.Optional("steam_profile_id"): str}
)


async def async_get_user_url(steam_account_name: str):
    """Get URL for a user's wishlist.

    :raises ValueError: If the steam account name appears to be invalid.
    """
    url = WISHLIST_URL.format(username=steam_account_name)
    async with aiohttp.ClientSession() as session:
        async with (session.get(url)) as resp:
            html = await resp.text()
            matches = re.findall(r"wishlist\\\/profiles\\\/([0-9]+)", html)
            if not matches:
                _LOGGER.error(
                    "Error setting up steam-wishlist component.  Did not find user id."
                )
                raise ValueError
            user_id = matches[0]
            return WISHLIST_JSON_URL.format(user_id=user_id)


async def async_check_profile_id_valid(steam_profile_id: str) -> bool:
    url = PROFILE_ID_URL.format(steam_profile_id=steam_profile_id)
    async with aiohttp.ClientSession() as session:
        async with (session.get(url)) as resp:
            if resp.status > 200:
                return False
    return True


class SteamWishlistConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Steam wishlist config flow."""

    async def async_step_user(self, user_input):
        """Handle a flow initialized by the user interface."""
        errors = {}
        if user_input is not None:
            if not user_input.get("steam_account_name") and not user_input.get(
                "steam_profile_id"
            ):
                errors["base"] = "missing"
            if user_input.get("steam_account_name"):
                # Validate the account name is valid.
                try:
                    user_url = await async_get_user_url(
                        user_input["steam_account_name"]
                    )
                except ValueError:
                    errors["base"] = "invalid_user"
            elif user_input.get("steam_profile_id"):
                # Validate the profile id is valid.
                if await async_check_profile_id_valid(user_input["steam_profile_id"]):
                    user_url = WISHLIST_JSON_URL.format(
                        user_id=user_input["steam_profile_id"]
                    )
                else:
                    errors["base"] = "invalid_profile_id"

            if not errors:
                return self.async_create_entry(
                    title="Steam Wishlist", data={"url": user_url}
                )

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors,
        )
