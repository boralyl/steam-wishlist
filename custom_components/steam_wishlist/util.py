from datetime import datetime, timedelta, timezone
import logging
from typing import Any, Dict, Optional

from .types import SteamGame

_LOGGER = logging.getLogger(__name__)

def get_release_date(game: dict[str, Any]) -> str:
    release_date = game.get("release_date", "0")
    if str(release_date).isdigit():
        release_date_datetime = datetime.fromtimestamp(int(release_date), timezone.utc)
        if datetime.now(timezone.utc) < release_date_datetime + timedelta(days=1):
            return "Release date:&nbsp;&nbsp;" + release_date_datetime.strftime("%b %d, %Y") + "&nbsp;&nbsp;🆕"
        else:
            return "Released:&nbsp;&nbsp;" + release_date_datetime.strftime("%b %d, %Y")
    else:
        return "Unknown"

def get_steam_game(game_id: int, game: Dict) -> SteamGame:
    """Get a SteamGame from a game dict."""
    pricing: Optional[Dict[str, Any]] = None
    try:
        pricing: Dict[str, Any] = game["subs"][0]
        discount_pct = pricing["discount_pct"] or 0
    except IndexError:
        # This typically means this game is not yet released so pricing is not known.
        pricing = None
        discount_pct = 0

    normal_price: Optional[float] = None
    if pricing:
        price = int(pricing["price"])
        if discount_pct == 100:
            normal_price = price
        else:
            normal_price = round(price / (100 - discount_pct), 2)

    sale_price: Optional[float] = None
    if pricing and discount_pct:
        # Price is an integer so $6.00 is 600.
        sale_price = round(int(pricing["price"]) * 0.01, 2)

    reviews_percent = game.get('reviews_percent', 'N/A')
    review_desc = game.get('review_desc', 'No reviews')
    rating_info = f"Reviews:&nbsp;&nbsp;{reviews_percent}% ({review_desc})"

    try:
        original_price = float(normal_price if normal_price is not None else 0)
        sale_price_val = float(sale_price if sale_price is not None else original_price)
        discount_percentage = int(discount_pct) if discount_pct is not None else 0
        if original_price == 0:
            price_info = "Price:&nbsp;&nbsp;TBD"
        else:
            original_price_formatted = f"{original_price:.2f}"
            if sale_price is not None:
                strikethrough_price = ''.join(ch + "\u0336" for ch in original_price_formatted[:-1]) + original_price_formatted[-1]
                price_info = f"{strikethrough_price} ${sale_price_val:.2f} ({discount_percentage}% off)&nbsp;&nbsp;🎫"
            else:
                price_info = f"Price:&nbsp;&nbsp;${original_price:.2f}"
    except (ValueError, TypeError):
        price_info = "Price information unavailable"

    game: SteamGame = {
        "title": game["name"],
        "rating": rating_info,
        "price": price_info,
        "genres": ", ".join(game.get("tags", [])),
        "release": get_release_date(game),
        "airdate": game.get("release_date", ""),
        "normal_price": str(normal_price),
        "percent_off": str(discount_pct),
        "review_desc": game.get("review_desc", "No user reviews"),
        "reviews_percent": game.get("reviews_percent", 0),
        "reviews_total": game.get("reviews_total", "0"),
        "sale_price": sale_price,
        "steam_id": str(game_id),
        "box_art_url": game["capsule"],
        "fanart": game.get("capsule"),
        "poster": game.get("capsule"),
        "deep_link": f"https://store.steampowered.com/app/{game_id}",
    }
    return game
