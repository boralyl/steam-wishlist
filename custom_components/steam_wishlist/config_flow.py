import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN


class SteamWishlistConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """STEAM wishlist config flow."""

    async def async_step_user(self, user_input):
        """Handle a flow initialized by the user interface."""
        if user_input is not None:
            return self.async_create_entry(title="STEAM Wishlist", data=user_input,)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required("url", default=self.config_entry.options.get("url")): str}
            ),
        )

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return await self.async_step_user(import_config)
