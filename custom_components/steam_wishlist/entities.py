import logging
from typing import List

from homeassistant.helpers.entity import Entity
from homeassistant.util import slugify

from .types import SteamGame
from .util import get_steam_game

try:
    from homeassistant.components.binary_sensor import BinarySensorEntity
except ImportError:
    # Prior to HA v0.110
    from homeassistant.components.binary_sensor import (
        BinarySensorDevice as BinarySensorEntity,
    )


_LOGGER = logging.getLogger(__name__)


class SteamWishlistEntity(Entity):
    """Representation of a Steam wishlist."""

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.coordinator = manager.coordinator
        self._attrs = {}

    @property
    def unique_id(self) -> str:
        return "steam_wishlist"

    @property
    def on_sale(self):
        return [game for game in self.games if game["sale_price"]]

    @property
    def games(self) -> List[SteamGame]:
        """Return all games on the Steam wishlist."""
        games: List[SteamGame] = []
        for game_id, game in self.coordinator.data.items():
            # This indicates an empty wishlist, just return an empty list.
            if game_id == "success":
                break
            games.append(get_steam_game(game_id, game))
        return games

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Steam Wishlist"

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity, if any."""
        return "on sale"

    @property
    def icon(self) -> str:
        """Icon to use in the frontend."""
        return "mdi:format-list-bulleted-square"

    @property
    def state(self) -> int:
        """Return the state of the sensor."""
        return len(self.on_sale)

    @property
    def device_state_attributes(self):
        return {"on_sale": self.on_sale}

    async def async_update(self):
        """Update the entity.

        This is only used by the generic entity update service. Normal updates
        happen via the coordinator.
        """
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )


class SteamGameEntity(BinarySensorEntity):
    """Representation of a Steam game."""

    entity_id = None

    def __init__(
        self, manager, game: SteamGame,
    ):
        super().__init__()
        self.game = game
        self.manager = manager
        self.coordinator = manager.coordinator
        self.slug = slugify(self.game["title"])
        self.entity_id = f"binary_sensor.{self.unique_id}"

    @property
    def unique_id(self) -> str:
        return f"steam_wishlist_{self.slug}"

    @property
    def is_on(self):
        """Return True if the binary sensor is on."""
        pricing = self.coordinator.data[self.game["steam_id"]]
        try:
            pricing: dict = self.coordinator.data[self.game["steam_id"]]["subs"][0]
            discount_pct = pricing["discount_pct"]
        except IndexError:
            discount_pct = 0
        return discount_pct > 0

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.game["title"]

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity, if any."""
        return "on sale"

    @property
    def icon(self) -> str:
        """Icon to use in the frontend."""
        return "mdi:steam"

    @property
    def state(self) -> bool:
        """Return the state of the sensor."""
        return self.is_on

    @property
    def device_state_attributes(self):
        return get_steam_game(
            self.game["steam_id"], self.coordinator.data[self.game["steam_id"]]
        )

    async def async_update(self):
        """Update the entity.

        This is only used by the generic entity update service. Normal updates
        happen via the coordinator.
        """
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
