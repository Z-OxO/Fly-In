from typing import Any

FONT = {"name": "noto_sans", "size": "22"}
ITEM = {
    "font": FONT,
    "misc": {
        "text_horiz_alignment": "left",
        "text_horiz_alignment_padding": "10",
    },
}
THEME: dict[str, Any] = {
    "drop_down_menu.button": ITEM,
    "drop_down_menu.selection_list.button": ITEM,
    "drop_down_menu.selection_list": {"misc": {"list_item_height": "36"}},
}
