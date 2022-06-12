import logging
from typing import Any, Dict, Optional

from .types import SteamGame

_LOGGER = logging.getLogger(__name__)


def get_steam_game(game_id: int, game: Dict[str, Any]) -> SteamGame:
    """Get a SteamGame from a game dict."""
    pricing: Optional[Dict[str, Any]] = None
    try:
        pricing: Dict[str, Any] = game["subs"][0]
        discount_pct = pricing["discount_pct"]
    except IndexError:
        # This typically means this game is not yet released so pricing is not known.
        pricing = None
        discount_pct = 0

    normal_price: Optional[float] = None
    if pricing:
        if discount_pct == 100:
            normal_price = pricing["price"]
        else:
            normal_price = round(pricing["price"] / (100 - discount_pct), 2)

    sale_price: Optional[float] = None
    if pricing and discount_pct:
        # Price is an integer so $6.00 is 600.
        sale_price = round(pricing["price"] * 0.01, 2)

    game: SteamGame = {
        "box_art_url": game["capsule"],
        "normal_price": normal_price,
        "percent_off": discount_pct,
        "review_desc": game.get("review_desc", "No user reviews"),
        "reviews_percent": game.get("reviews_percent", 0),
        "reviews_total": game.get("reviews_total", "0"),
        "sale_price": sale_price,
        "steam_id": game_id,
        "title": game["name"],
    }
    return game
