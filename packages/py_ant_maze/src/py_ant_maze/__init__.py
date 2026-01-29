"""Maze definition utilities."""

from .element_set import ElementSet
from .elements import MazeElement, CellElement, WallElement
from .maze import Maze
from .types import (
    OccupancyGridConfig,
    OccupancyGridLayout,
    EdgeGridConfig,
    EdgeGridLayout,
)

__all__ = [
    "Maze",
    "ElementSet",
    "MazeElement",
    "CellElement",
    "WallElement",
    "OccupancyGridConfig",
    "OccupancyGridLayout",
    "EdgeGridConfig",
    "EdgeGridLayout",
]
__version__ = "0.1.1"
