"""Test the entity classes."""
from custom_components.steam_wishlist import util
from custom_components.steam_wishlist.entities import (
    SteamGameEntity,
    SteamWishlistEntity,
)


def test_steamwishlistentity_games_property(manager_mock):
    """Test the games property works properly."""
    entity = SteamWishlistEntity(manager_mock)
    expected = [
        {
            "box_art_url": "https://steamcdn-a.akamaihd.net/steam/apps/870780/header_292x136.jpg?t=1572428374",
            "normal_price": None,
            "percent_off": 0,
            "review_desc": "No user reviews",
            "reviews_percent": 0,
            "reviews_total": "0",
            "sale_price": None,
            "steam_id": "870780",
            "title": "Control",
        },
        {
            "box_art_url": "https://steamcdn-a.akamaihd.net/steam/apps/952060/header_292x136.jpg?t=1590098547",
            "normal_price": 59.99,
            "percent_off": 0,
            "review_desc": "Mostly Positive",
            "reviews_percent": 73,
            "reviews_total": "17,331",
            "sale_price": None,
            "steam_id": "952060",
            "title": "RESIDENT EVIL 3",
        },
        {
            "box_art_url": "https://steamcdn-a.akamaihd.net/steam/apps/975150/header_292x136.jpg?t=1590678003",
            "normal_price": 19.99,
            "percent_off": 15,
            "review_desc": "3 user reviews",
            "reviews_percent": 100,
            "reviews_total": "3",
            "sale_price": 16.99,
            "steam_id": "975150",
            "title": "Resolutiion",
        },
    ]
    assert expected == entity.games


def test_steamwishlistentity_games_property_empty_wishlist(manager_mock):
    """Test the games property returns an empty list for an empty wishlist."""
    manager_mock.coordinator.data = {"success": {}}
    entity = SteamWishlistEntity(manager_mock)
    assert [] == entity.games


def test_steamwishlistentity_state(manager_mock):
    """Test the state property of the entity."""
    entity = SteamWishlistEntity(manager_mock)
    assert 1 == entity.state


def test_steamgameentity_unique_id_property(manager_mock):
    """Test the unique_id property of the entity."""
    game_id = "975150"
    game = util.get_steam_game(game_id, manager_mock.coordinator.data[game_id])
    entity = SteamGameEntity(manager_mock, game)
    assert "steam_wishlist_resolutiion" == entity.unique_id


def test_steamgameentity_is_on_property(manager_mock):
    """Test the is_on property of the entity."""
    # Game on sale
    game_id = "975150"
    game = util.get_steam_game(game_id, manager_mock.coordinator.data[game_id])
    entity = SteamGameEntity(manager_mock, game)
    assert entity.is_on is True

    # Game not on sale
    game_id = "952060"
    game = util.get_steam_game(game_id, manager_mock.coordinator.data[game_id])
    entity = SteamGameEntity(manager_mock, game)
    assert entity.is_on is False

    # Game with no pricing information (unreleased)
    game_id = "870780"
    game = util.get_steam_game(game_id, manager_mock.coordinator.data[game_id])
    entity = SteamGameEntity(manager_mock, game)
    assert entity.is_on is False


def test_steamgameentity_name_property(manager_mock):
    """Test the name property of the entity."""
    game_id = "975150"
    game = util.get_steam_game(game_id, manager_mock.coordinator.data[game_id])
    entity = SteamGameEntity(manager_mock, game)
    assert "Resolutiion" == entity.name


def test_steamgameentity_extra_state_attributes_property(manager_mock):
    """Test the device_state_attributes property."""
    game_id = "975150"
    game = util.get_steam_game(game_id, manager_mock.coordinator.data[game_id])
    entity = SteamGameEntity(manager_mock, game)
    expected = {
        "box_art_url": "https://steamcdn-a.akamaihd.net/steam/apps/975150/header_292x136.jpg?t=1590678003",
        "normal_price": 19.99,
        "percent_off": 15,
        "review_desc": "3 user reviews",
        "reviews_percent": 100,
        "reviews_total": "3",
        "sale_price": 16.99,
        "steam_id": "975150",
        "title": "Resolutiion",
    }
    assert expected == entity.extra_state_attributes
