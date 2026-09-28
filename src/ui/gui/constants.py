from .models import Swatch, RGB
from src.models import Zone

PALETTE: dict[str, Swatch] = {
    "red": Swatch(fill=(255, 106, 106), ring=(255, 166, 166)),
    "orange": Swatch(fill=(255, 158, 64), ring=(255, 197, 140)),
    "yellow": Swatch(fill=(232, 230, 116), ring=(241, 240, 172)),
    "green": Swatch(fill=(126, 217, 126), ring=(178, 232, 178)),
    "cyan": Swatch(fill=(110, 210, 240), ring=(168, 228, 246)),
    "blue": Swatch(fill=(114, 168, 255), ring=(170, 203, 255)),
    "purple": Swatch(fill=(186, 142, 246), ring=(214, 187, 250)),
    "pink": Swatch(fill=(250, 150, 186), ring=(252, 192, 214)),
    "white": Swatch(fill=(238, 242, 250), ring=(245, 247, 252)),
}


ZONE_STYLE: dict[Zone, tuple[RGB, int]] = {
    Zone.NORMAL: ((180, 180, 190), 2),
    Zone.PRIORITY: ((120, 230, 150), 3),
    Zone.RESTRICTED: ((255, 140, 60), 4),
    Zone.BLOCKED: ((90, 90, 100), 2),
}
