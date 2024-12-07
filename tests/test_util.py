"""Util tests."""

from custom_components.steam_wishlist.util import get_steam_game

not_on_sale = {
    "item_type": 0,
    "id": 2215430,
    "success": 1,
    "visible": True,
    "name": "Ghost of Tsushima DIRECTOR'S CUT",
    "store_url_path": "app/2215430/Ghost_of_Tsushima_DIRECTORS_CUT",
    "appid": 2215430,
    "type": 0,
    "content_descriptorids": [1, 2, 5],
    "categories": {
        "supported_player_categoryids": [2, 1, 9, 38],
        "feature_categoryids": [22, 62],
        "controller_categoryids": [28],
    },
    "reviews": {
        "summary_filtered": {
            "review_count": 33897,
            "percent_positive": 93,
            "review_score": 8,
            "review_score_label": "Very Positive",
        }
    },
    "basic_info": {
        "short_description": "A storm is coming. Venture into the complete Ghost of Tsushima DIRECTOR’S CUT on PC; forge your own path through this open-world action adventure and uncover its hidden wonders. Brought to you by Sucker Punch Productions, Nixxes Software and PlayStation Studios.",
        "publishers": [
            {"name": "PlayStation Publishing LLC", "creator_clan_account_id": 40425349}
        ],
        "developers": [
            {"name": "Sucker Punch Productions", "creator_clan_account_id": 40425349},
            {"name": "Nixxes Software", "creator_clan_account_id": 40425349},
        ],
        "franchises": [
            {"name": "PlayStation Studios", "creator_clan_account_id": 40425349}
        ],
    },
    "assets": {
        "asset_url_format": "steam/apps/2215430/${FILENAME}?t=1717622497",
        "main_capsule": "capsule_616x353.jpg",
        "small_capsule": "capsule_231x87.jpg",
        "header": "header.jpg",
        "page_background": "page_bg_generated_v6b.jpg",
        "hero_capsule": "hero_capsule.jpg",
        "library_capsule": "library_600x900.jpg",
        "library_capsule_2x": "library_600x900_2x.jpg",
        "library_hero": "library_hero.jpg",
        "library_hero_2x": "library_hero_2x.jpg",
        "community_icon": "e87b8cbe31f7bc5f40ee6ed94ccfa18f59f04fbc",
    },
    "best_purchase_option": {
        "packageid": 793537,
        "purchase_option_name": "Ghost of Tsushima DIRECTOR'S CUT",
        "final_price_in_cents": "5999",
        "formatted_final_price": "$59.99",
        "user_can_purchase_as_gift": True,
        "hide_discount_pct_for_compliance": False,
        "included_game_count": 1,
    },
}

on_sale = {
    "item_type": 0,
    "id": 1220150,
    "success": 1,
    "visible": True,
    "name": "Blue Fire",
    "store_url_path": "app/1220150/Blue_Fire",
    "appid": 1220150,
    "type": 0,
    "categories": {
        "supported_player_categoryids": [2],
        "feature_categoryids": [22, 23, 43, 62],
        "controller_categoryids": [28],
    },
    "reviews": {
        "summary_filtered": {
            "review_count": 1623,
            "percent_positive": 84,
            "review_score": 8,
            "review_score_label": "Very Positive",
        }
    },
    "basic_info": {
        "short_description": "Embark on an extraordinary adventure through the perished world of Penumbra to explore unique temples filled with increasingly difficult 3D platforming challenges, diverse enemies, quests, collectibles, and more. Slash daunting adversaries, leap through deadly traps and master the art of movement.",
        "publishers": [{"name": "Graffiti Games", "creator_clan_account_id": 35843170}],
        "developers": [{"name": "Robi Studios", "creator_clan_account_id": 44788856}],
        "franchises": [
            {"name": "Blue Fire", "creator_clan_account_id": 44788856},
            {"name": "Graffiti Games", "creator_clan_account_id": 35843170},
        ],
    },
    "assets": {
        "asset_url_format": "steam/apps/1220150/${FILENAME}?t=1655302580",
        "main_capsule": "capsule_616x353.jpg",
        "small_capsule": "capsule_231x87.jpg",
        "header": "header.jpg",
        "page_background": "page_bg_generated_v6b.jpg",
        "library_capsule": "library_600x900.jpg",
        "library_capsule_2x": "library_600x900_2x.jpg",
        "library_hero": "library_hero.jpg",
        "community_icon": "db04631967d673b165ca802969706557cdbc2d84",
    },
    "best_purchase_option": {
        "packageid": 422570,
        "purchase_option_name": "Blue Fire",
        "final_price_in_cents": "499",
        "original_price_in_cents": "1999",
        "formatted_final_price": "$4.99",
        "formatted_original_price": "$19.99",
        "discount_pct": 75,
        "active_discounts": [
            {
                "discount_amount": "1500",
                "discount_description": "#discount_desc_preset_special",
                "discount_end_date": 1734544800,
            }
        ],
        "user_can_purchase_as_gift": True,
        "hide_discount_pct_for_compliance": False,
        "included_game_count": 1,
    },
}


def test_get_steam_game_on_sale(steam_game) -> None:
    """Verify we get the expected result when a game is on sale."""
    actual = get_steam_game(on_sale["id"], on_sale)
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


def test_get_steam_game_not_on_sale(steam_game) -> None:
    """Verify we get the expected result when a game is not on sale."""
    actual = get_steam_game(not_on_sale["id"], not_on_sale)
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
