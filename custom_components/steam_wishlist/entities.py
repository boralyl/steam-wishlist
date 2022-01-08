import logging
from typing import List

from homeassistant.helpers.update_coordinator import CoordinatorEntity
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


class SteamWishlistEntity(CoordinatorEntity):
    """Representation of a Steam wishlist."""

    def __init__(self, manager):
        super().__init__(coordinator=manager.coordinator)
        self.manager = manager
        self._attrs = {}

    @property
    def unique_id(self) -> str:
        return f"steam_wishlist_{self.coordinator.steam_id}"

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
        return f"Steam Wishlist ({self.coordinator.steam_id})"

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
    def extra_state_attributes(self):
        return {"on_sale": self.on_sale}

    @property
    def device_info(self):
        return self.coordinator.device_info


class SteamGameEntity(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Steam game."""

    entity_id = None

    def __init__(
        self,
        manager,
        game: SteamGame,
    ):
        super().__init__(coordinator=manager.coordinator)
        self.game = game
        self.manager = manager
        self.slug = slugify(self.game["title"])
        self.entity_id = f"binary_sensor.{self.unique_id}"

    @property
    def unique_id(self) -> str:
        return f"steam_wishlist_{self.slug}"

    @property
    def is_on(self):
        """Return True if the binary sensor is on."""
        try:
            pricing = self.coordinator.data[self.game["steam_id"]]
        except KeyError:
            # This can happen when a game is removed from your wishlist and the entity
            # has not yet been removed from HA.
            _LOGGER.warning(
                "%s not found in self.coordinator.data keys (%s), assuming False. Data was %s",
                self.game,
                list(self.coordinator.data.keys()),
                self.coordinator.data,
            )
            return False
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
    def extra_state_attributes(self):
        return get_steam_game(
            self.game["steam_id"], self.coordinator.data[self.game["steam_id"]]
        )
