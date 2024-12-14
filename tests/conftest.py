"""pytest fixtures."""

from unittest.mock import Mock

from aioresponses import aioresponses
import pytest


@pytest.fixture
def mock_aioresponse():
    """Fixture to mock aiohttp calls."""
    with aioresponses() as m:
        yield m


@pytest.fixture
def game_on_sale_response_item():
    """Fixture to return an on sale steam game response item."""
    return {
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
            "publishers": [
                {"name": "Graffiti Games", "creator_clan_account_id": 35843170}
            ],
            "developers": [
                {"name": "Robi Studios", "creator_clan_account_id": 44788856}
            ],
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


@pytest.fixture
def game_response_item():
    """Fixture to return a steam game response item."""
    return {
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
                {
                    "name": "PlayStation Publishing LLC",
                    "creator_clan_account_id": 40425349,
                }
            ],
            "developers": [
                {
                    "name": "Sucker Punch Productions",
                    "creator_clan_account_id": 40425349,
                },
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


@pytest.fixture
def coordinator_mock(hass, game_response_item, game_on_sale_response_item):
    """Fixture to mock the update data coordinator."""
    coordinator = Mock(data={}, hass=hass)
    coordinator.data = {
        str(game_on_sale_response_item["id"]): game_on_sale_response_item,
        str(game_response_item["id"]): game_response_item,
    }
    yield coordinator


@pytest.fixture
def manager_mock(coordinator_mock):
    """Pytest fixture mocking the sensor manager class."""
    manager = Mock(coordinator=coordinator_mock)
    yield manager
