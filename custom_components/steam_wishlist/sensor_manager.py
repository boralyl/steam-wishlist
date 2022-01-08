import logging
from typing import Any, Callable, Dict, List, Union

from homeassistant import core
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_registry import async_get_registry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, SCAN_INTERVAL
from .entities import SteamGameEntity, SteamWishlistEntity
from .util import get_steam_game

_LOGGER = logging.getLogger(__name__)
WISHLIST_ID = -1
DEVICE_CONFIGURATION_URL = "https://store.steampowered.com/wishlist/profiles/{}/"

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
        # https://store.steampowered.com/wishlist/profiles/<steam-id>/wishlistdata/
        self.steam_id = self.url.split("/")[-3]
        self.http_session = async_get_clientsession(hass)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_method=self._async_fetch_data,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_fetch_data(self) -> Dict[str, Dict[str, Any]]:
        """Fetch the data for the coordinator."""
        data: Dict[str, Dict[str, Any]] = {}
        # Attempt to look up to 10 pages of data. There does not appear to be a static
        # number of results returned, it seems random. There also isn't any indication
        # in the response that to let us know there are more pages to fetch. An empty
        # array will be returned if we request a page of results when a user doesn't
        # have that many.
        for page in range(10):
            url = f"{self.url}?p={page}"
            async with self.http_session.get(url) as resp:
                result = await resp.json()
                if not isinstance(result, dict):
                    # An empty array will be returned if we request a page of results
                    # when a user doesn't have that many. e.g. requesting page 2 when
                    # they only have 1 page of results.
                    break
                data.update(result)
                if len(result) <= 50:
                    # Even though we don't know the number of results per page, it seems
                    # to be well over 50, likely between 70-100. So don't bother a 2nd
                    # request if the result is this small.
                    break

        return data

    @property
    def device_info(self) -> DeviceInfo:
        unique_id = self.config_entry.unique_id
        return DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            manufacturer="Valve Corp",
            name="Steam",
            configuration_url=DEVICE_CONFIGURATION_URL.format(self.steam_id),
        )


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

        process_data = True
        if not isinstance(self.coordinator.data, dict):
            # This seems to happen when we get an unexpected response.  This typically
            # means an intermittent request failure. Data is then an empty dict. Should
            # something different happen here?
            _LOGGER.warning(
                "Coordinator data unexpectedly not a dict: %s", self.coordinator.data
            )
            process_data = False
        # {"success": 2} This CAN (but not always) indicate an empty wishlist.
        if "success" not in self.coordinator.data and process_data:
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
