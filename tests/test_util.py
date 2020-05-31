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


def test_get_steam_game_with_sale_price():
    """Test that we get the correct return value for a normal on sale game."""
    game_id = "975150"
    game = {
        "name": "Resolutiion",
        "capsule": "https://steamcdn-a.akamaihd.net/steam/apps/975150/header_292x136.jpg?t=1590678003",
        "subs": [
            {
                "id": 320073,
                "discount_block": '<div class="discount_block discount_block_large" data-price-final="1699"><div class="discount_pct">-15%</div><div class="discount_prices"><div class="discount_original_price">$19.99</div><div class="discount_final_price">$16.99</div></div></div>',
                "discount_pct": 15,
                "price": 1699,
            }
        ],
        "type": "Game",
        "added": 1590721175,
    }
    actual = get_steam_game(game_id, game)
    expected = {
        "box_art_url": "https://steamcdn-a.akamaihd.net/steam/apps/975150/header_292x136.jpg?t=1590678003",
        "normal_price": 19.99,
        "percent_off": 15,
        "sale_price": 16.99,
        "steam_id": "975150",
        "title": "Resolutiion",
    }
    assert expected == actual
