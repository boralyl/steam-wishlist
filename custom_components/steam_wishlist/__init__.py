"""The Steam Wishlist integration."""

import asyncio
import logging

from homeassistant import config_entries, core

from .const import DOMAIN
from .sensor_manager import SensorManager

_LOGGER = logging.getLogger(__name__)
DATA_CONFIGS = "steam_wishlist_config"
PLATFORMS = ("binary_sensor", "sensor")


async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up platforms from a ConfigEntry."""
    url = entry.data["url"]
    # https://store.steampowered.com/wishlist/profiles/<steam-id>/wishlistdata/
    steam_id = url.split("/")[-3]
    hass.data[DOMAIN][entry.entry_id] = SensorManager(hass, url)

    if not entry.unique_id:
        hass.config_entries.async_update_entry(
            entry,
            unique_id=f"steam_wishlist_{steam_id}",
            title=f"Steam Wishlist ({steam_id})",
        )

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the Steam wishlist component.

    This component can only be configured through the Integrations UI.
    """
    hass.data.setdefault(DOMAIN, {})
    return True
