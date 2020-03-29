import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional

from homeassistant import config_entries, core
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity

from . import SteamWishlistDataUpdateCoordinator
from .const import DOMAIN
from .types import SteamGame


SCAN_INTERVAL = timedelta(minutes=10)
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = [SteamWishlistEntity(hass, coordinator)]
    _LOGGER.info("%s: Setting up sensor...", DOMAIN)
    async_add_entities(entities, True)


class SteamWishlistEntity(Entity):
    """Representation of a STEAM wishlist."""

    def __init__(
        self, hass: core.HomeAssistant, coordinator: SteamWishlistDataUpdateCoordinator
    ):
        super().__init__()
        self.hass = hass
        self.coordinator = coordinator
        self._attrs = {}

    @property
    def on_sale(self):
        return [game for game in self.games if game["sale_price"]]

    @property
    def games(self) -> List[SteamGame]:
        """Return all games on the STEAM wishlist."""
        games: List[SteamGame] = []
        for game_id, game in self.coordinator.data.items():
            try:
                discount: Dict[str, Any] = game["subs"][0]
            except IndexError:
                _LOGGER.warning(
                    "STEAM game unexpectedly had no pricing information (this is likely a pre-release): %s",
                    game,
                )
                continue
            normal_price: float = round(
                discount["price"] / (100 - discount["discount_pct"]), 2
            )
            sale_price: Optional[float] = None
            if discount["discount_pct"]:
                # Price is an integer so $6.00 is 600.
                sale_price = discount["price"] * 0.01
            games.append(
                {
                    "box_art_url": game["capsule"],
                    "normal_price": normal_price,
                    "percent_off": discount["discount_pct"],
                    "sale_price": sale_price,
                    "steam_id": game_id,
                    "title": game["name"],
                }
            )
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

    # async def async_update(self) -> None:
    #    """Get the latest data and updates the state."""
    #    _LOGGER.info("%s: updating the state", DOMAIN)
    #    http_session = async_get_clientsession(self.hass)
    #    async with http_session.get(self.url) as resp:
    #        data = await resp.json()
    #        _LOGGER.info("%s: Fetched data: %s", DOMAIN, data)
    #        on_sale: List[dict] = []
    #        for game_id, game in data.items():
    #            discount: Optional[Dict[str, Any]] = None
    #            # Check if there is any discount
    #            for sub in game["subs"]:
    #                if sub["discount_pct"] > 0:
    #                    discount = sub
    #                    break
    #            if discount is not None:
    #                on_sale.append(
    #                    {
    #                        "box_art_url": game["capsule"],
    #                        "normal_price": round(
    #                            discount["price"] / (100 - discount["discount_pct"]), 2
    #                        ),
    #                        "sale_price": discount["price"] * 0.01,
    #                        "steam_id": game_id,
    #                        "percent_off": discount["discount_pct"],
    #                        "title": game["name"],
    #                    }
    #                )
    #        self._state = len(on_sale)
    #        self._attrs["on_sale"] = on_sale
