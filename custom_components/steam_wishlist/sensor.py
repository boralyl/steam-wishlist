import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional

from homeassistant import config_entries, core
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity

from .const import DOMAIN


DEFAULT_NAME = "Nintendo Wishlist Sensor"
SCAN_INTERVAL = timedelta(minutes=10)
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    url: str = config_entry.data["url"]
    _LOGGER.info("%s: Setting up sensor: %s", DOMAIN, url)
    entities: List[SteamWishlistEntity] = [SteamWishlistEntity(hass, url)]
    async_add_entities(entities, True)


class SteamWishlistEntity(Entity):
    """Representation of a STEAM wishlist."""

    def __init__(self, hass: core.HomeAssistant, url: str):
        super().__init__()
        self.hass = hass
        self.url = url
        self._state = 0
        self._attrs = {}

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
        return self._state

    @property
    def device_state_attributes(self):
        return self._attrs

    async def async_update(self) -> None:
        """Get the latest data and updates the state."""
        _LOGGER.info("%s: updating the state", DOMAIN)
        http_session = async_get_clientsession(self.hass)
        async with http_session.get(self.url) as resp:
            data = await resp.json()
            _LOGGER.info("%s: Fetched data: %s", DOMAIN, data)
            on_sale: List[dict] = []
            for game_id, game in data.items():
                discount: Optional[Dict[str, Any]] = None
                # Check if there is any discount
                for sub in game["subs"]:
                    if sub["discount_pct"] > 0:
                        discount = sub
                        break
                if discount is not None:
                    on_sale.append(
                        {
                            "box_art_url": game["capsule"],
                            "normal_price": round(
                                discount["price"] / (100 - discount["discount_pct"]), 2
                            ),
                            "sale_price": discount["price"] * 0.01,
                            "percent_off": discount["discount_pct"],
                            "title": game["name"],
                        }
                    )
            self._state = len(on_sale)
            self._attrs["on_sale"] = on_sale
