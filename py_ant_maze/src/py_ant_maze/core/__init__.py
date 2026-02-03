"""Core maze data structures and grid utilities."""

from .handlers import MazeTypeHandler
from .structures.elements import MazeElement, CellElement, WallElement
from .structures.element_set import ElementSet, FrozenElementSet
from .structures.grid import parse_grid, format_grid

__all__ = [
    "MazeElement",
    "CellElement",
    "WallElement",
    "ElementSet",
    "FrozenElementSet",
    "MazeTypeHandler",
    "parse_grid",
    "format_grid",
]
