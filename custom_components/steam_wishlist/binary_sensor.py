import logging


from homeassistant import config_entries, core
from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import slugify

from .const import DOMAIN
from .types import SteamGame
from .util import get_steam_game


_LOGGER = logging.getLogger(__name__)


class GameRemovedException(HomeAssistantError):
    """Exception raised when a game was removed from a wishlist."""

    pass


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Defer sensor setup to the shared sensor module."""
    await hass.data[DOMAIN][config_entry.entry_id].async_register_component(
        "binary_sensor", async_add_entities
    )
    # coordinator = hass.data[DOMAIN][config_entry.entry_id]
    # entities = []
    # for game_id, game in coordinator.data.items():
    #    steam_game: SteamGame = get_steam_game(game_id, game)
    #    entities.append(SteamGameEntity(hass, coordinator, steam_game))

    # async_add_entities(entities, True)


class SteamGameEntity(BinarySensorDevice):
    """Representation of a STEAM game."""

    def __init__(
        self, manager, game: SteamGame,
    ):
        super().__init__()
        self.game = game
        self.manager = manager
        self.coordinator = manager.coordinator

    @property
    def is_on(self):
        """Return True if the binary sensor is on."""
        if self.game["steam_id"] not in self.coordinator.data:

            async def _async_remove():
                await self.async_remove()

            return False

        pricing = self.coordinator.data[self.game["steam_id"]]
        try:
            pricing: dict = self.coordinator.data[self.game["steam_id"]]["subs"][0]
            discount_pct = pricing["discount_pct"]
        except IndexError:
            discount_pct = 0
        return discount_pct > 0

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
        return self.is_on

    @property
    def device_state_attributes(self):
        return get_steam_game(
            self.game["steam_id"], self.coordinator.data[self.game["steam_id"]]
        )

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Disconnect from update signal."""
        self.coordinator.async_remove_listener(self.async_write_ha_state)
