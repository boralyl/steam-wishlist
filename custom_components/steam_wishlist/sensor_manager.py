"""Coordinator and sensor manager for the integration."""

from collections.abc import Callable
from itertools import batched
import json
import logging
from typing import Any

from homeassistant import core
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, SCAN_INTERVAL
from .entities import SteamGameEntity, SteamWishlistEntity
from .util import get_steam_game

_LOGGER = logging.getLogger(__name__)
WISHLIST_ID = -1
# The max amount of app ids to request data for in a single network request.
BATCH_SIZE = 100
DEVICE_CONFIGURATION_URL = "https://store.steampowered.com/wishlist/profiles/{}/"
GET_WISHLIST_URL = "https://api.steampowered.com/IWishlistService/GetWishlist/v1"
GET_APPS_URL = "https://api.steampowered.com/IStoreBrowseService/GetItems/v1"

SteamEntity = SteamGameEntity | SteamWishlistEntity


class SteamWishlistDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for all steam_wishlist entities.

    This class handles updating for all entities created by this component.
    Since all data required to update all sensors and binary_sensors comes
    from a single api endpoint, this will handle fetching that data.  This way
    each entity doesn't need to fetch the exact same data every time an update
    is scheduled.
    """

    def __init__(self, hass: core.HomeAssistant, api_key: str, steam_id: str) -> None:
        self.api_key = api_key
        self.steam_id = steam_id
        self.http_session = async_get_clientsession(hass)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_method=self._async_fetch_data,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_fetch_data(self) -> dict[int, dict[str, Any]]:
        """Fetch the data for the coordinator."""
        async with self.http_session.get(
            GET_WISHLIST_URL, params={"key": self.api_key, "steamid": self.steam_id}
        ) as resp:
            wishlist_data = await resp.json()
            app_ids: list[int] = [
                item["appid"] for item in wishlist_data["response"]["items"]
            ]

        data: dict[int, dict[str, Any]] = {}
        for batch in batched(app_ids, BATCH_SIZE):
            input_json = {
                "ids": [{"appid": str(app_id)} for app_id in batch],
                "context": {
                    "language": self.hass.config.language or "en",
                    "country_code": self.hass.config.country or "US",
                },
                "data_request": {
                    "include_assets": True,
                    "include_reviews": True,
                    "include_basic_info": True,
                },
            }
            async with self.http_session.get(
                GET_APPS_URL,
                params={"key": self.api_key, "input_json": json.dumps(input_json)},
            ) as resp:
                apps_data = await resp.json()
                data.update(
                    {item["id"]: item for item in apps_data["response"]["store_items"]}
                )
        return data

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for the integration."""
        unique_id = self.config_entry.unique_id
        return DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            manufacturer="Valve Corp",
            name="Steam",
            configuration_url=DEVICE_CONFIGURATION_URL.format(self.steam_id),
        )


async def async_remove_games(
    current_wishlist: dict[int, SteamEntity],
    coordinator: SteamWishlistDataUpdateCoordinator,
) -> None:
    """Remove games no longer on the wish list.

    This will delete the entity and unregister it with homeassistant.
    This method also mutates `current_wishlist`, removing games that should
    be removed.
    """
    removed_entities = []
    for game_id, entity in current_wishlist.items():
        # Never remove the sensor.steam_wishlist
        if game_id == WISHLIST_ID:
            continue

        if game_id not in coordinator.data:
            # Need to remove entity
            removed_entities.append(game_id)
            await entity.async_remove()
            ent_registry = er.async_get(coordinator.hass)
            if entity.entity_id in ent_registry.entities:
                ent_registry.async_remove(entity.entity_id)

    for game_id in removed_entities:
        del current_wishlist[game_id]


class SensorManager:
    """Class that handles registering and updating sensor/binary_sensor entities.

    NOTE: This is intended to be a singleton.
    """

    def __init__(
        self,
        hass: core.HomeAssistant,
        store_all_wishlist_items: bool,
        api_key: str,
        steam_id: str,
    ) -> None:
        """Initialize the sensor manager."""
        self.hass = hass
        self.store_all_wishlist_items = store_all_wishlist_items
        self.steam_id = steam_id
        self.api_key = api_key
        self.coordinator = SteamWishlistDataUpdateCoordinator(hass, api_key, steam_id)
        self._component_add_entities = {}
        self.cleanup_jobs = []
        self.current_wishlist: dict[int, SteamEntity] = {}

    async def async_register_component(
        self, platform: str, async_add_entities: Callable
    ):
        """Register a platform for the component."""
        self._component_add_entities[platform] = async_add_entities
        if len(self._component_add_entities) < 2:
            # Haven't registered both `sensor` and `binary_sensor` platforms yet.
            return

        # All platforms are now registered for the component.
        # Add callback to update sensors when coordinator refreshes data.
        self.coordinator.async_add_listener(self.async_update_items)
        # Fetch initial data.
        await self.coordinator.async_refresh()

    @callback
    def async_update_items(self):
        """Add or remove sensors based on coordinator data."""
        if len(self._component_add_entities) < 2:
            # Wait until both sensor and binary_sensor platforms are registered
            return

        new_sensors: list[SteamWishlistEntity] = []
        if not self.current_wishlist.get(WISHLIST_ID):
            self.current_wishlist[WISHLIST_ID] = SteamWishlistEntity(self)
            new_sensors.append(self.current_wishlist[WISHLIST_ID])

        new_binary_sensors: list[SteamGameEntity] = []

        for game_id, game in self.coordinator.data.items():
            existing = self.current_wishlist.get(game_id)
            if existing is not None:
                continue

            # Found a new game that we will need to create a new binary_sensor for.
            steam_game = get_steam_game(game_id, game)
            self.current_wishlist[game_id] = SteamGameEntity(self, steam_game)
            new_binary_sensors.append(self.current_wishlist[game_id])

        if new_sensors:
            self._component_add_entities["sensor"](new_sensors)
        if new_binary_sensors:
            self._component_add_entities["binary_sensor"](new_binary_sensors)

        # Handle removing any entities that removed from the steam wishlist.
        self.hass.async_create_task(
            async_remove_games(self.current_wishlist, self.coordinator)
        )
