import aiohttp
import logging
import re

import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
WISHLIST_URL = "https://store.steampowered.com/wishlist/id/{username}/"
WISHLIST_JSON_URL = (
    "https://store.steampowered.com/wishlist/profiles/{user_id}/wishlistdata/"
)


async def async_get_user_url(steam_account_name: str):
    """Get URL for a user's wishlist.

    :raises ValueError: If the steam account name appears to be invalid.
    """
    session = aiohttp.ClientSession()
    url = WISHLIST_URL.format(username=steam_account_name)
    async with aiohttp.ClientSession() as session:
        async with (session.get(url)) as resp:
            html = await resp.text()
            matches = re.findall("wishlist\\\/profiles\\\/([0-9]+)", html)
            if not matches:
                _LOGGER.error("Did not find user id.")
                raise ValueError
            user_id = matches[0]
            return WISHLIST_JSON_URL.format(user_id=user_id)


class SteamWishlistConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Steam wishlist config flow."""

    async def async_step_user(self, user_input):
        """Handle a flow initialized by the user interface."""
        errors = {}
        if user_input is not None:
            # Valdate the account name is valid.
            try:
                user_url = await async_get_user_url(user_input["steam_account_name"])
            except ValueError:
                errors["base"] = "invalid_user"

            if not errors:
                return self.async_create_entry(
                    title="Steam Wishlist", data={"url": user_url}
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("steam_account_name"): str}),
            errors=errors,
        )

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return await self.async_step_user(import_config)
