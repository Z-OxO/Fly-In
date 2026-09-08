from typing import TypeAlias

Move: TypeAlias = tuple[int, str]
Turn: TypeAlias = tuple[Move, ...]
Plan: TypeAlias = tuple[Turn, ...]
