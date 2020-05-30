"""pytest fixtures."""
from aioresponses import aioresponses
import pytest
from pytest_homeassistant.async_mock import Mock


@pytest.fixture
def mock_aioresponse():
    """Fixture to mock aiohttp calls."""
    with aioresponses() as m:
        yield m


@pytest.fixture
def coordinator_mock(hass):
    """Fixture to mock the update data coordinator."""
    coordinator = Mock(data={}, hass=hass)
    coordinator.data = {
        "870780": {
            "name": "Control",
            "capsule": "https://steamcdn-a.akamaihd.net/steam/apps/870780/header_292x136.jpg?t=1572428374",
            "review_score": 0,
            "review_desc": "No user reviews",
            "reviews_total": "0",
            "reviews_percent": 0,
            "release_date": "1556236800",
            "release_string": "Coming August 2020",
            "platform_icons": '<span class="platform_img win"></span>',
            "subs": [],
            "type": "Game",
            "screenshots": [
                "ss_4cd872ed17a77fee5ddfff766f56a152968030cf.jpg",
                "ss_5a4d1a304f214a47ca110ceb1172cccaaf997608.jpg",
                "ss_6b486bb45eea618c0a7fd0781202f3ae3315aa91.jpg",
                "ss_91b9bb3feeac710f9497de84392b1f7487989669.jpg",
            ],
            "review_css": "no_reviews",
            "priority": 0,
            "added": 1584991718,
            "background": "https://steamcdn-a.akamaihd.net/steam/apps/274520/page_bg_generated_v6b.jpg?t=1568727996",
            "rank": 1000,
            "tags": [],
            "is_free_game": False,
            "win": 1,
        },
        "952060": {
            "name": "RESIDENT EVIL 3",
            "capsule": "https://steamcdn-a.akamaihd.net/steam/apps/952060/header_292x136.jpg?t=1590098547",
            "review_score": 6,
            "review_desc": "Mostly Positive",
            "reviews_total": "17,331",
            "reviews_percent": 73,
            "release_date": "1585886220",
            "release_string": "Apr 2",
            "platform_icons": '<span class="platform_img win"></span>',
            "subs": [
                {
                    "id": 437203,
                    "discount_block": '<div class="discount_block discount_block_large no_discount" data-price-final="5999"><div class="discount_prices"><div class="discount_final_price">$59.99</div></div></div>',
                    "discount_pct": 0,
                    "price": 5999,
                }
            ],
            "type": "Game",
            "screenshots": [
                "ss_77eda710487b89293f109cf7dcf96b4ffab0d1a1.jpg",
                "ss_34f01910d65fb171a27e058cb74623c0eb53ba69.jpg",
                "ss_bec8b7cef716135ea5bbd726a3342ed9ca475b31.jpg",
                "ss_4f6eaac14b8e02c0a68a9c9f7627dd84cde1abb8.jpg",
            ],
            "review_css": "positive",
            "priority": 0,
            "added": 1585503915,
            "background": "https://steamcdn-a.akamaihd.net/steam/apps/952060/page_bg_generated_v6b.jpg?t=1590098547",
            "rank": 713,
            "tags": [],
            "is_free_game": False,
            "win": 1,
        },
        "975150": {
            "name": "Resolutiion",
            "capsule": "https://steamcdn-a.akamaihd.net/steam/apps/975150/header_292x136.jpg?t=1590678003",
            "review_score": 0,
            "review_desc": "3 user reviews",
            "reviews_total": "3",
            "reviews_percent": 100,
            "release_date": "1590677842",
            "release_string": "May 28",
            "platform_icons": '<span class="platform_img win"></span><span class="platform_img mac"></span><span class="platform_img linux"></span>',
            "subs": [
                {
                    "id": 320073,
                    "discount_block": '<div class="discount_block discount_block_large" data-price-final="1699"><div class="discount_pct">-15%</div><div class="discount_prices"><div class="discount_original_price">$19.99</div><div class="discount_final_price">$16.99</div></div></div>',
                    "discount_pct": 15,
                    "price": 1699,
                }
            ],
            "type": "Game",
            "screenshots": [
                "ss_08e312cea81092226c8e20c57b4d578ecd4ffa3a.jpg",
                "ss_66d6693d1e84b2a0932ec3b88f54901eebdac68f.jpg",
                "ss_e11b14c5e5e6e55bf8fbd064e4a9a8e1b49e528f.jpg",
                "ss_3405c0136e4c11538c54a0675bea60196aaf66e3.jpg",
            ],
            "review_css": "not_enough_reviews",
            "priority": 0,
            "added": 1590721175,
            "background": "https://steamcdn-a.akamaihd.net/steam/apps/1057090/page_bg_generated_v6b.jpg?t=1588789337",
            "rank": 830,
            "tags": [],
            "is_free_game": False,
            "win": 1,
            "mac": 1,
            "linux": 1,
        },
    }
    yield coordinator


@pytest.fixture
def manager_mock(coordinator_mock):
    """Pytest fixture mocking the sensor manager class."""
    manager = Mock(coordinator=coordinator_mock)
    yield manager
