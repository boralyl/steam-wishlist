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
        normal_price = round(pricing["price"] / (100 - discount_pct), 2)

    sale_price: Optional[float] = None
    if pricing and discount_pct:
        # Price is an integer so $6.00 is 600.
        sale_price = round(pricing["price"] * 0.01, 2)

    game: SteamGame = {
        "box_art_url": game["capsule"],
        "normal_price": normal_price,
        "percent_off": discount_pct,
        "sale_price": sale_price,
        "steam_id": game_id,
        "title": game["name"],
    }
    return game
