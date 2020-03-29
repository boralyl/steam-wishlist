"""The STEAM Wishlist integration."""

import asyncio
import logging

from homeassistant import config_entries, core
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)
DATA_CONFIGS = "steam_wishlist_config"
PLATFORMS = ("binary_sensor", "sensor")


async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    url = entry.data["url"]
    _LOGGER.info("async_setup_entry: setup url %s", url)

    coordinator = SteamWishlistDataUpdateCoordinator(hass, url)
    await coordinator.async_refresh()
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

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
    """Set up the STEAM wishlist component."""
    hass.data.setdefault(DOMAIN, {})
    conf = config.get(DOMAIN)
    if conf is None:
        return True

    hass.data[DATA_CONFIGS] = conf

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_IMPORT}, data=conf
        )
    )

    return True


class SteamWishlistDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: core.HomeAssistant, url: str):
        self.url = url
        self.http_session = async_get_clientsession(hass)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_method=self._async_fetch_data,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_fetch_data(self):
        """Fetch the data for the coordinator."""
        async with self.http_session.get(self.url) as resp:
            data = await resp.json()
        return data
