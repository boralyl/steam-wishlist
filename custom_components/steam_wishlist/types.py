from typing import TypedDict


class SteamGame(TypedDict):
    """Represents a Steam Game."""

    box_art_url: str
    normal_price: str | None
    percent_off: float
    reviews_desc: str
    reviews_percent: int
    reviews_total: int
    sale_price: str | None
    steam_id: int
    title: str
