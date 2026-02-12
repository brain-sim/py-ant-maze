"""Shared models for image-to-maze reconstruction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

SUPPORTED_MAZE_TYPES: Tuple[str, ...] = ("auto", "occupancy_grid", "edge_grid")


@dataclass(frozen=True)
class GridEstimate:
    maze_type: str
    rows: int
    cols: int
    period_x: float
    period_y: float


@dataclass(frozen=True)
class MazeReconstruction:
    maze_type: str
    rows: int
    cols: int
    occupancy_grid: Optional[List[List[int]]] = None
    cells: Optional[List[List[int]]] = None
    vertical_walls: Optional[List[List[int]]] = None
    horizontal_walls: Optional[List[List[int]]] = None
