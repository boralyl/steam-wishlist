import aiohttp
import logging
import re

import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
WISHLIST_URL = "https://store.steampowered.com/wishlist/id/{username}/"
URI = "https://store.steampowered.com/wishlist/profiles/{user_id}/wishlistdata/"


class SteamWishlistConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """STEAM wishlist config flow."""

    async def async_step_user(self, user_input):
        """Handle a flow initialized by the user interface."""
        if user_input is not None:
            # validate input...
            session = aiohttp.ClientSession()
            url = WISHLIST_URL.format(username=user_input["steam_account_name"])
            async with aiohttp.ClientSession() as session:
                async with (session.get(url)) as resp:
                    html = await resp.text()
                    _LOGGER.warning(
                        "re findall: %s",
                        re.findall("wishlist\\\/profiles\\\/([0-9]+)", html),
                    )
                    matches = re.findall("wishlist\\\/profiles\\\/([0-9]+)", html)
                    if not matches:
                        # do something
                        _LOGGER.error("Did not find user id.")
                    user_id = matches[0]
                    _LOGGER.warning("Found user: %s", user_id)
                    user_url = URI.format(user_id=user_id)
            return self.async_create_entry(
                title="STEAM Wishlist", data={"url": user_url}
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("steam_account_name"): str}),
        )

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return await self.async_step_user(import_config)
