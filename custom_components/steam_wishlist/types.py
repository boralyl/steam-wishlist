from typing import Optional

from typing_extensions import TypedDict


class SteamGame(TypedDict):
    box_art_url: str
    normal_price: Optional[float]
    percent_off: float
    sale_price: Optional[float]
    steam_id: int
    title: str
