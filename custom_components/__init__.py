"""The STEAM Wishlist integration."""

import logging

from homeassistant import config_entries, core


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    _LOGGER.info("async_setup_entry: setup url %s", entry["url"])
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True
