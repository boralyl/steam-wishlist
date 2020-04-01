import logging
from typing import Any, Callable, Dict, List

from homeassistant import core
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, SCAN_INTERVAL
from .types import SteamGame
from .util import get_steam_game

_LOGGER = logging.getLogger(__name__)
WISHLIST_SENSOR = -1


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


class SensorManager:
    """Class that handles registering and updating Hue sensor entities.

    Note: This is intended to be a singleton.
    """

    def __init__(self, hass: core.HomeAssistant, url: str):
        self.hass = hass
        self.coordinator = SteamWishlistDataUpdateCoordinator(hass, url)
        self._component_add_entities = {}
        self.cleanup_jobs = []
        # Actually: Dict[int, Union[SteamWishlistEntity, SteamGameEntity]]
        self.current_wishlist: Dict[int, Any] = {}

    async def async_register_component(
        self, platform: str, async_add_entities: Callable
    ):
        self._component_add_entities[platform] = async_add_entities
        if len(self._component_add_entities) < 2:
            # Haven't registered both `sensor` and `binary_sensor` platforms yet.
            return

        # All platforms registered for the component.
        # Add callback to update sensors.
        self.coordinator.async_add_listener(self.async_update_items)
        # Fetch initial data.
        await self.coordinator.async_refresh()

    @callback
    def async_update_items(self):
        """Update sensors based on coordinator data."""
        from .binary_sensor import SteamGameEntity
        from .sensor import SteamWishlistEntity

        if len(self._component_add_entities) < 2:
            # Haven't registered both `sensor` and `binary_sensor` platforms yet.
            return

        new_binary_sensors: List[SteamGameEntity] = []
        new_sensors: List[SteamWishlistEntity] = []

        if not self.current_wishlist.get(WISHLIST_SENSOR):
            self.current_wishlist[WISHLIST_SENSOR] = SteamWishlistEntity(self)
            new_sensors.append(self.current_wishlist[WISHLIST_SENSOR])
        for game_id, game in self.coordinator.data.items():
            existing = self.current_wishlist.get(game_id)
            if existing is not None:
                continue

            steam_game = get_steam_game(game_id, game)
            self.current_wishlist[game_id] = SteamGameEntity(self, steam_game)
            new_binary_sensors.append(self.current_wishlist[game_id])

        # Look in current for removed games
        # self.hass.async_create_task(
        #     # logic to unregister entities...
        # )
        if new_sensors:
            self._component_add_entities["sensor"](new_sensors)
        if new_binary_sensors:
            self._component_add_entities["binary_sensor"](new_binary_sensors)
