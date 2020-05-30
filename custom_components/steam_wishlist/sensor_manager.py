import logging
from typing import Callable, Dict, List, Union

from homeassistant import core
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_registry import async_get_registry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, SCAN_INTERVAL
from .entities import SteamGameEntity, SteamWishlistEntity
from .util import get_steam_game

_LOGGER = logging.getLogger(__name__)
WISHLIST_ID = -1

SteamEntity = Union[SteamGameEntity, SteamWishlistEntity]


class SteamWishlistDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for all steam_wishlist entities.

    This class handles updating for all entities created by this component.
    Since all data required to update all sensors and binary_sensors comes
    from a single api endpoint, this will handle fetching that data.  This way
    each entity doesn't need to fetch the exact same data every time an update
    is scheduled.
    """

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

    @callback
    def async_add_listener(
        self, update_callback: core.CALLBACK_TYPE
    ) -> Callable[[], None]:
        """Listen for data updates.

        @NOTE: this is copied from an unreleased version of HA (v0.108.0).  After that
        Release we may be able to use this (and set the minimum version in hacs.json to
        0.108.0)
        """
        schedule_refresh = not self._listeners

        self._listeners.append(update_callback)

        # This is the first listener, set up interval.
        if schedule_refresh:
            self._schedule_refresh()

        @callback
        def remove_listener() -> None:
            """Remove update listener."""
            self.async_remove_listener(update_callback)

        return remove_listener


async def async_remove_games(
    current_wishlist: Dict[int, SteamEntity],
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
            ent_registry = await async_get_registry(coordinator.hass)
            if entity.entity_id in ent_registry.entities:
                ent_registry.async_remove(entity.entity_id)

    for game_id in removed_entities:
        del current_wishlist[game_id]


class SensorManager:
    """Class that handles registering and updating sensor/binary_sensor entities.

    NOTE: This is intended to be a singleton.
    """

    def __init__(self, hass: core.HomeAssistant, url: str):
        self.hass = hass
        self.coordinator = SteamWishlistDataUpdateCoordinator(hass, url)
        self._component_add_entities = {}
        self.cleanup_jobs = []
        self.current_wishlist: Dict[int, SteamEntity] = {}

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
            # Haven't registered both `sensor` and `binary_sensor` platforms yet.
            return

        new_sensors: List[SteamWishlistEntity] = []
        if not self.current_wishlist.get(WISHLIST_ID):
            self.current_wishlist[WISHLIST_ID] = SteamWishlistEntity(self)
            new_sensors.append(self.current_wishlist[WISHLIST_ID])

        new_binary_sensors: List[SteamGameEntity] = []
        # {"success": 2} This indicates an empty wishlist.
        if "success" not in self.coordinator.data:
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
