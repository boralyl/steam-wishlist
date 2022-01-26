from typing import Optional, TypedDict


class SteamGame(TypedDict):
    box_art_url: str
    normal_price: Optional[float]
    percent_off: float
    reviews_desc: str
    reviews_percent: int
    reviews_total: str
    sale_price: Optional[float]
    steam_id: int
    title: str
