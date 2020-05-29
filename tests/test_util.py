"""Util tests."""
from custom_components.steam_wishlist.util import get_steam_game


def test_get_steam_game_unreleased_game():
    """Test that we get the correct return value for an unreleased game."""
    game_id = "870780"
    game = {
        "name": "Control",
        "capsule": "https://steamcdn-a.akamaihd.net/steam/apps/870780/header_292x136.jpg?t=1572428374",
        "release_date": "1556236800",
        "release_string": "Coming August 2020",
        "subs": [],
        "type": "Game",
    }
    actual = get_steam_game(game_id, game)
    expected = {
        "box_art_url": "https://steamcdn-a.akamaihd.net/steam/apps/870780/header_292x136.jpg?t=1572428374",
        "normal_price": None,
        "percent_off": 0,
        "sale_price": None,
        "steam_id": "870780",
        "title": "Control",
    }
    assert expected == actual
