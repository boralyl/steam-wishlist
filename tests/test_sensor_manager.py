"""Tests for the SensorManager class."""
from typing import Dict

from custom_components.steam_wishlist import sensor_manager
from custom_components.steam_wishlist.entities import (
    SteamGameEntity,
    SteamWishlistEntity,
)
from custom_components.steam_wishlist.sensor_manager import SteamEntity
from custom_components.steam_wishlist.types import SteamGame
from custom_components.steam_wishlist.util import get_steam_game

from .async_mock import AsyncMock, call


async def test_async_remove_games(manager_mock):
    """Test game entities are removed when removed from the wishlist."""
    wishlist_entity = SteamWishlistEntity(manager_mock)
    entities = [
        SteamGameEntity(
            manager_mock,
            get_steam_game(game_id, manager_mock.coordinator.data[game_id]),
        )
        for game_id in manager_mock.coordinator.data
    ]
    wishlist: Dict[int, SteamEntity] = {
        entity.game["steam_id"]: entity for entity in entities
    }
    # add a game to the current wishlist that will not be in the coordinator.data
    # to simulate a user removing a game from their wishlist.
    removed_game: SteamGame = {
        "box_art_url": "url",
        "normal_price": 49.99,
        "percent_off": 0,
        "sale_price": None,
        "steam_id": 12345,
        "title": "Removed",
    }
    removed_game_entity = SteamGameEntity(manager_mock, removed_game)
    # Need to mock this method as the entity platform isn't run so self.hass isn't set.
    removed_game_entity.async_remove = AsyncMock()
    wishlist[removed_game["steam_id"]] = removed_game_entity
    wishlist[sensor_manager.WISHLIST_ID] = wishlist_entity
    await sensor_manager.async_remove_games(wishlist, manager_mock.coordinator)
    # Verify the game was removed from the wishlist.
    assert removed_game["steam_id"] not in wishlist
    # Assert entity removed from HA
    assert removed_game_entity.async_remove.called is True


async def test_sensormanager_async_register_component_hasnt_registered_all(
    hass, coordinator_mock
):
    """Test that we abort setup if both platforms haven't been registered yet."""
    manager = sensor_manager.SensorManager(hass, url="http://fake.com")
    manager.coordinator = coordinator_mock
    mock_async_add_entities = AsyncMock()
    await manager.async_register_component("sensor", mock_async_add_entities)
    assert coordinator_mock.async_add_listener.called is False
    assert manager._component_add_entities["sensor"] == mock_async_add_entities


async def test_sensormanager_async_register_component_registered_all(
    hass, coordinator_mock
):
    """Test that we add listeners and referesh data if all platforms were registered."""
    manager = sensor_manager.SensorManager(hass, url="http://fake.com")
    manager.coordinator = coordinator_mock
    coordinator_mock.async_refresh = AsyncMock()
    mock_async_add_entities = AsyncMock()
    manager._component_add_entities["binary_sensor"] = mock_async_add_entities
    await manager.async_register_component("sensor", mock_async_add_entities)
    assert coordinator_mock.async_add_listener.called is True
    assert coordinator_mock.async_refresh.called is True
    assert {
        "binary_sensor": mock_async_add_entities,
        "sensor": mock_async_add_entities,
    } == manager._component_add_entities


async def test_sensormanager_async_update_items_hasnt_registered_all(
    hass, coordinator_mock
):
    """Test that we abort updating if both platforms haven't been registered yet."""
    manager = sensor_manager.SensorManager(hass, url="http://fake.com")
    manager.coordinator = coordinator_mock
    manager.async_update_items()
    assert [] == manager.hass._pending_tasks


async def test_sensormanager_async_update_items_success(hass, coordinator_mock):
    """Test that we add all new entities."""
    manager = sensor_manager.SensorManager(hass, url="http://fake.com")
    manager.coordinator = coordinator_mock
    mock_async_add_entities = AsyncMock()
    manager._component_add_entities = {
        "binary_sensor": mock_async_add_entities,
        "sensor": mock_async_add_entities,
    }
    manager.async_update_items()

    import pprint

    pprint.pprint(mock_async_add_entities.call_args_list)
    expected_add_entities_calls = [
        # Wishlist entity
        call([manager.current_wishlist[sensor_manager.WISHLIST_ID]]),
        # Steam game entities
        call(
            [
                manager.current_wishlist["870780"],
                manager.current_wishlist["952060"],
                manager.current_wishlist["975150"],
            ]
        ),
    ]
    assert expected_add_entities_calls == mock_async_add_entities.call_args_list
    # Verify our task to remove games was created.
    assert 1 == len(manager.hass._pending_tasks)
