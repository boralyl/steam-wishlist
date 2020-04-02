import aiohttp
import logging
import re

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
WISHLIST_URL = "https://store.steampowered.com/wishlist/id/{username}/"


class SteamWishlistConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """STEAM wishlist config flow."""

    async def async_step_user(self, user_input):
        """Handle a flow initialized by the user interface."""
        if user_input is not None:
            # validate input...
            session = aiohttp.ClientSession()
            url = WISHLIST_URL.format(username=user_input["steam_account_name"])
            async with (session.get(url)) as resp:
                html = await resp.text()
                _LOGGER.warning("User input html was: %s")
                _LOGGER.warning(
                    "re findall: %s",
                    re.findall("wishlist\\\/profiles\\\/([0-9]+)", html),
                )
            return self.async_create_entry(title="STEAM Wishlist", data=user_input,)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("steam_account_name"): str}),
        )

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return await self.async_step_user(import_config)
