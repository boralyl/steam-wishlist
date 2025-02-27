import logging
from typing import Any

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

    def __init__(self, manager) -> None:
        super().__init__(coordinator=manager.coordinator)
        self.manager = manager
        self._attrs = {}

        self._attr_device_info = manager.coordinator.device_info

    @property
    def unique_id(self) -> str:
        return f"steam_wishlist_{self.coordinator.steam_id}"

    @property
    def on_sale(self) -> list[SteamGame]:
        """Return all games on sale."""
        return [game for game in self.games if game["percent_off"] > 0]

    def _is_price_valid(self, price):
        # Ensures compatibility with 'sale_price' being dynamically typed as string or numeric
        # to accommodate boolean 'show_all_wishlist_items' option
        if not price:
            return False
        try:
            return float(price) > 0
        except ValueError:
            return False

    @property
    def games(self) -> list[SteamGame]:
        """Return all games on the Steam wishlist."""
        games: list[SteamGame] = []
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
    def extra_state_attributes(self) -> dict[str, Any]:
        # Added Upcoming Media Card compatibility
        placeholders = {
            "title_default": "$title",
            "line1_default": "$rating",
            "line2_default": "$price",
            "line3_default": "$release",
            "line4_default": "$genres",
            "icon": "mdi:arrow-down-bold",
        }
        if self.manager.store_all_wishlist_items:
            games = self.games
        else:
            games = [game for game in self.games if game["sale_price"] is not None]
        data_list = [placeholders, *games]
        return {"data": data_list, "on_sale": self.on_sale}


class SteamGameEntity(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Steam game."""

    entity_id = None

    def __init__(self, manager, game: SteamGame) -> None:
        super().__init__(coordinator=manager.coordinator)
        self.game = game
        self.manager = manager
        self.slug = slugify(self.game["title"])

        self._attr_unique_id = f"steam_wishlist_{self.coordinator.steam_id}_{self.slug}"
        self._attr_device_info = manager.coordinator.device_info

        self.entity_id = f"binary_sensor.{self._attr_unique_id}"

    @property
    def is_on(self):
        """Return True if the binary sensor is on."""
        return self.game["percent_off"] > 0

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.game["title"]

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
        return self.game
