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
            "title": "Blue Fire",
            "rating": "Reviews:&nbsp;&nbsp;84% (Very Positive)",
            "price": "$̶1̶9̶.̶9̶9 $4.99 (75% off)&nbsp;&nbsp;🎫",
            "genres": "",
            "release": "",
            "airdate": "unknown",
            "normal_price": "$19.99",
            "percent_off": 75,
            "review_desc": "Very Positive",
            "reviews_percent": 84,
            "reviews_total": 1623,
            "sale_price": "$4.99",
            "steam_id": "1220150",
            "box_art_url": "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/1220150/capsule_616x353.jpg?t=1655302580",
            "fanart": "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/1220150/capsule_616x353.jpg?t=1655302580",
            "poster": "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/1220150/capsule_616x353.jpg?t=1655302580",
            "deep_link": "https://store.steampowered.com/app/1220150",
        },
        {
            "title": "Ghost of Tsushima DIRECTOR'S CUT",
            "rating": "Reviews:&nbsp;&nbsp;93% (Very Positive)",
            "price": "Price:&nbsp;&nbsp;$59.99",
            "genres": "",
            "release": "",
            "airdate": "unknown",
            "normal_price": "$59.99",
            "percent_off": 0,
            "review_desc": "Very Positive",
            "reviews_percent": 93,
            "reviews_total": 33897,
            "sale_price": None,
            "steam_id": "2215430",
            "box_art_url": "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/2215430/capsule_616x353.jpg?t=1717622497",
            "fanart": "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/2215430/capsule_616x353.jpg?t=1717622497",
            "poster": "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/2215430/capsule_616x353.jpg?t=1717622497",
            "deep_link": "https://store.steampowered.com/app/2215430",
        },
    ]
    assert expected == entity.games


def test_steamwishlistentity_games_property_empty_wishlist(manager_mock):
    """Test the games property returns an empty list for an empty wishlist."""
    manager_mock.coordinator.data = {}
    entity = SteamWishlistEntity(manager_mock)
    assert entity.games == []


def test_steamwishlistentity_state(manager_mock):
    """Test the state property of the entity."""
    entity = SteamWishlistEntity(manager_mock)
    assert 1 == entity.state


def test_steamgameentity_unique_id_property(manager_mock):
    """Test the unique_id property of the entity."""
    manager_mock.coordinator.steam_id = "12345"
    game_id = "1220150"
    game = util.get_steam_game(game_id, manager_mock.coordinator.data[game_id])
    entity = SteamGameEntity(manager_mock, game)
    assert "steam_wishlist_12345_blue_fire" == entity.unique_id


def test_steamgameentity_is_on_property(manager_mock):
    """Test the is_on property of the entity."""
    # Game on sale
    game_id = "1220150"
    game = util.get_steam_game(game_id, manager_mock.coordinator.data[game_id])
    entity = SteamGameEntity(manager_mock, game)
    assert entity.is_on is True

    # Game not on sale
    game_id = "2215430"
    game = util.get_steam_game(game_id, manager_mock.coordinator.data[game_id])
    entity = SteamGameEntity(manager_mock, game)
    assert entity.is_on is False


def test_steamgameentity_name_property(manager_mock):
    """Test the name property of the entity."""
    game_id = "1220150"
    game = util.get_steam_game(game_id, manager_mock.coordinator.data[game_id])
    entity = SteamGameEntity(manager_mock, game)
    assert entity.name == "Blue Fire"


def test_steamgameentity_extra_state_attributes_property(manager_mock):
    """Test the device_state_attributes property."""
    game_id = "1220150"
    game = util.get_steam_game(game_id, manager_mock.coordinator.data[game_id])
    entity = SteamGameEntity(manager_mock, game)
    expected = {
        "title": "Blue Fire",
        "rating": "Reviews:&nbsp;&nbsp;84% (Very Positive)",
        "price": "$̶1̶9̶.̶9̶9 $4.99 (75% off)&nbsp;&nbsp;🎫",
        "genres": "",
        "release": "",
        "airdate": "unknown",
        "normal_price": "$19.99",
        "percent_off": 75,
        "review_desc": "Very Positive",
        "reviews_percent": 84,
        "reviews_total": 1623,
        "sale_price": "$4.99",
        "steam_id": "1220150",
        "box_art_url": "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/1220150/capsule_616x353.jpg?t=1655302580",
        "fanart": "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/1220150/capsule_616x353.jpg?t=1655302580",
        "poster": "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/1220150/capsule_616x353.jpg?t=1655302580",
        "deep_link": "https://store.steampowered.com/app/1220150",
    }
    assert entity.extra_state_attributes == expected
