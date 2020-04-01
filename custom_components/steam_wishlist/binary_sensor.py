from homeassistant import config_entries, core

from .const import DOMAIN


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Defer sensor setup to the sensor manager."""
    await hass.data[DOMAIN][config_entry.entry_id].async_register_component(
        "binary_sensor", async_add_entities
    )
