"""Util tests."""

from custom_components.steam_wishlist.util import get_steam_game


def test_get_steam_game_on_sale(game_on_sale_response_item) -> None:
    """Verify we get the expected result when a game is on sale."""
    actual = get_steam_game(
        game_on_sale_response_item["id"], game_on_sale_response_item
    )
    expected = {
        "airdate": "unknown",
        "box_art_url": "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/1220150/capsule_616x353.jpg?t=1655302580",
        "deep_link": "https://store.steampowered.com/app/1220150",
        "fanart": "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/1220150/capsule_616x353.jpg?t=1655302580",
        "genres": "",
        "normal_price": "$19.99",
        "percent_off": 75,
        "poster": "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/1220150/capsule_616x353.jpg?t=1655302580",
        "price": "$̶1̶9̶.̶9̶9 $4.99 (75% off)&nbsp;&nbsp;🎫",
        "rating": "Reviews:&nbsp;&nbsp;84% (Very Positive)",
        "release": "",
        "review_desc": "Very Positive",
        "reviews_percent": 84,
        "reviews_total": 1623,
        "sale_price": "$4.99",
        "steam_id": "1220150",
        "title": "Blue Fire",
    }
    assert expected == actual


def test_get_steam_game_not_on_sale(game_response_item) -> None:
    """Verify we get the expected result when a game is not on sale."""
    actual = get_steam_game(game_response_item["id"], game_response_item)
    expected = {
        "airdate": "unknown",
        "box_art_url": "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/2215430/capsule_616x353.jpg?t=1717622497",
        "deep_link": "https://store.steampowered.com/app/2215430",
        "fanart": "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/2215430/capsule_616x353.jpg?t=1717622497",
        "genres": "",
        "normal_price": "$59.99",
        "percent_off": 0,
        "poster": "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/2215430/capsule_616x353.jpg?t=1717622497",
        "price": "Price:&nbsp;&nbsp;$59.99",
        "rating": "Reviews:&nbsp;&nbsp;93% (Very Positive)",
        "release": "",
        "review_desc": "Very Positive",
        "reviews_percent": 93,
        "reviews_total": 33897,
        "sale_price": None,
        "steam_id": "2215430",
        "title": "Ghost of Tsushima DIRECTOR'S CUT",
    }
    assert expected == actual
