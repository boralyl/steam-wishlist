import logging
from typing import List

from homeassistant import config_entries, core
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .util import get_steam_game
from .types import SteamGame


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    await hass.data[DOMAIN][config_entry.entry_id].async_register_component(
        "sensor", async_add_entities
    )


class SteamWishlistEntity(Entity):
    """Representation of a STEAM wishlist."""

    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.coordinator = manager.coordinator
        self._attrs = {}

    @property
    def on_sale(self):
        return [game for game in self.games if game["sale_price"]]

    @property
    def games(self) -> List[SteamGame]:
        """Return all games on the STEAM wishlist."""
        games: List[SteamGame] = []
        for game_id, game in self.coordinator.data.items():
            games.append(get_steam_game(game_id, game))
        return games

    @property
    def entity_id(self) -> str:
        """Return the entity id of the sensor."""
        return "sensor.steam_wishlist"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "STEAM Wishlist"

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity, if any."""
        return "on sale"

    @property
    def icon(self) -> str:
        """Icon to use in the frontend."""
        return "mdi:steam"

    @property
    def state(self) -> int:
        """Return the state of the sensor."""
        return len(self.on_sale)

    @property
    def device_state_attributes(self):
        return {"on_sale": self.on_sale}

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Disconnect from update signal."""
        self.coordinator.async_remove_listener(self.async_write_ha_state)
