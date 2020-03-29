import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional


from homeassistant import config_entries, core
from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.util import slugify

from .const import DOMAIN
from .types import SteamGame


SCAN_INTERVAL = timedelta(minutes=10)
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    url: str = config_entry.data["url"]
    _LOGGER.info("%s: Setting up binary sensors: %s", DOMAIN, url)
    entities: List[SteamGameEntity] = []
    http_session = async_get_clientsession(hass)
    async with http_session.get(url) as resp:
        data = await resp.json()
        for game_id, game in data.items():
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
            steam_game: SteamGame = {
                "box_art_url": game["capsule"],
                "normal_price": normal_price,
                "percent_off": discount["discount_pct"],
                "sale_price": sale_price,
                "steam_id": game_id,
                "title": game["name"],
            }
            entities.append(SteamGameEntity(hass, url, steam_game))
    async_add_entities(entities, True)


class SteamGameEntity(BinarySensorDevice):
    """Representation of a STEAM game."""

    def __init__(self, hass: core.HomeAssistant, url: str, game: SteamGame):
        super().__init__()
        self.game = game
        self.hass = hass
        self.url = url
        self._state = True if game["sale_price"] is not None else False
        self._attrs = game

    @property
    def is_on(self):
        """Return True if the binary sensor is on."""
        return self._state

    @property
    def entity_id(self) -> str:
        """Return the entity id of the sensor."""
        slug = slugify(self.game["title"])
        return f"binary_sensor.steam_wishlist_{slug}"

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
        return self._state

    @property
    def device_state_attributes(self):
        return self._attrs

    async def async_update(self) -> None:
        """Get the latest data and updates the state."""
        _LOGGER.info("%s: updating the state", DOMAIN)
        state = False
        http_session = async_get_clientsession(self.hass)
        async with http_session.get(self.url) as resp:
            data = await resp.json()
            _LOGGER.info("%s: Fetched data: %s", DOMAIN, data)
            try:
                game = data[self.game["steam_id"]]
            except KeyError:
                raise UpdateFailed("Could not find game in wishlist. %s", self.game)
            discount: Optional[Dict[str, Any]] = None
            # Check if there is any discount
            for sub in game["subs"]:
                if sub["discount_pct"] > 0:
                    discount = sub
                    break
            if discount is not None:
                state = True
                steam_game: SteamGame = {
                    "box_art_url": game["capsule"],
                    "normal_price": round(
                        discount["price"] / (100 - discount["discount_pct"]), 2
                    ),
                    "sale_price": discount["price"] * 0.01,
                    "percent_off": discount["discount_pct"],
                    "title": game["name"],
                }
                self._attrs = steam_game

            self._state = state
