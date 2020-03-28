"""The STEAM Wishlist integration."""

import logging

from homeassistant import config_entries, core

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
DATA_CONFIGS = "steam_wishlist_config"


async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    _LOGGER.info("async_setup_entry: setup url %s", entry["url"])
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the STEAM wishlist platform."""
    conf = config.get(DOMAIN)
    if conf is None:
        conf = {}

    hass.data[DOMAIN] = {}
    hass.data[DATA_CONFIGS] = conf

    if conf is not None:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_IMPORT}, data=conf
            )
        )

    return True
