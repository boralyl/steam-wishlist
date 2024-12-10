"""Utilities for the integration."""

import logging
from typing import Any

from .types import SteamGame

_LOGGER = logging.getLogger(__name__)
ASSET_BASE_URL = "https://shared.cloudflare.steamstatic.com/store_item_assets/"


def get_steam_game(game_id: int, game: dict[str, Any]) -> SteamGame:
    """Get a SteamGame from a game dict."""
    pricing: dict[str, Any] | None = None
    discount_pct: float = 0
    normal_price: str | None = None
    sale_price: str | None = None
    if (pricing := game.get("best_purchase_option")) is not None:
        discount_pct = pricing.get("discount_pct", 0)
        if not discount_pct:
            normal_price = pricing["formatted_final_price"]
        else:
            normal_price = pricing["formatted_original_price"]
            sale_price = pricing["formatted_final_price"]

    reviews = game.get("reviews", {}).get("summary_filtered", {})
    reviews_percent = reviews.get("percent_positive", "N/A")
    review_desc = reviews.get("review_score_label", "No reviews")
    rating_info = f"Reviews:&nbsp;&nbsp;{reviews_percent}% ({review_desc})"
    review_count = reviews.get("review_count", 0)

    try:
        if normal_price is None:
            price_info = "Price:&nbsp;&nbsp;TBD"
        elif sale_price is not None:
            strikethrough_price = (
                "".join(ch + "\u0336" for ch in normal_price[:-1]) + normal_price[-1]
            )
            price_info = f"{strikethrough_price} {sale_price} ({discount_pct}% off)&nbsp;&nbsp;🎫"
        else:
            price_info = f"Price:&nbsp;&nbsp;{normal_price}"
    except (ValueError, TypeError):
        price_info = "Price information unavailable"

    try:
        image_url_format = game["assets"]["asset_url_format"]
        capsule = game["assets"]["main_capsule"]
        image_path = image_url_format.replace("${FILENAME}", capsule)
        image_url = f"{ASSET_BASE_URL}{image_path}"
    except KeyError:
        image_url = None

    game: SteamGame = {
        "title": game["name"],
        "rating": rating_info,
        "price": price_info,
        "genres": "",
        "release": "",
        "airdate": "unknown",
        "normal_price": normal_price,
        "percent_off": discount_pct,
        "review_desc": review_desc,
        "reviews_percent": reviews_percent,
        "reviews_total": review_count,
        "sale_price": sale_price,
        "steam_id": str(game_id),
        "box_art_url": image_url,
        "fanart": image_url,
        "poster": image_url,
        "deep_link": f"https://store.steampowered.com/app/{game_id}",
    }
    return game
