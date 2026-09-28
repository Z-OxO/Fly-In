from .models import Swatch, RGB
from src.models import Zone

PALETTE: dict[str, Swatch] = {
    "white": Swatch(fill=(238, 242, 250), ring=(245, 247, 252)),
    "red": Swatch(fill=(255, 106, 106), ring=(255, 166, 166)),
    "orange": Swatch(fill=(255, 158, 64), ring=(255, 197, 140)),
    "yellow": Swatch(fill=(232, 230, 116), ring=(241, 240, 172)),
    "blue": Swatch(fill=(114, 168, 255), ring=(170, 203, 255)),
    "cyan": Swatch(fill=(110, 210, 240), ring=(168, 228, 246)),
    "green": Swatch(fill=(126, 217, 126), ring=(178, 232, 178)),
    "purple": Swatch(fill=(186, 142, 246), ring=(214, 187, 250)),
    "pink": Swatch(fill=(250, 150, 186), ring=(252, 192, 214)),
    "black": Swatch(fill=(64, 68, 78), ring=(140, 143, 149)),
    "brown": Swatch(fill=(196, 140, 98), ring=(220, 186, 161)),
    "maroon": Swatch(fill=(170, 72, 92), ring=(204, 145, 157)),
    "gold": Swatch(fill=(246, 200, 72), ring=(250, 222, 145)),
    "darkred": Swatch(fill=(196, 58, 58), ring=(220, 137, 137)),
    "crimson": Swatch(fill=(240, 78, 112), ring=(246, 149, 169)),
    "magenta": Swatch(fill=(238, 96, 226), ring=(245, 160, 238)),
    "violet": Swatch(fill=(232, 156, 240), ring=(241, 196, 246)),
    "lime": Swatch(fill=(170, 240, 90), ring=(204, 246, 156)),
}

ZONE_STYLE: dict[Zone, tuple[RGB, int]] = {
    Zone.NORMAL: ((180, 180, 190), 2),
    Zone.PRIORITY: ((120, 230, 150), 3),
    Zone.RESTRICTED: ((255, 140, 60), 4),
    Zone.BLOCKED: ((90, 90, 100), 2),
}
