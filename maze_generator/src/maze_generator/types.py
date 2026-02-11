"""Data types for maze geometry."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class WallBox:
    """A wall rendered as an axis-aligned box in world space.

    Attributes:
        center: (x, y, z) center position in meters.
        size: (width, depth, height) extents in meters.
        element_name: The element name from the maze config
            (e.g. "wall", "door"), matching MazeElement.name.
    """

    center: Tuple[float, float, float]
    size: Tuple[float, float, float]
    element_name: str


@dataclass
class MazeGeometry:
    """Extracted wall geometry for an entire maze.

    Attributes:
        walls: List of wall boxes in world space.
        bounds: Overall (width, depth, height) bounding box.
    """

    walls: List[WallBox] = field(default_factory=list)
    bounds: Tuple[float, float, float] = (0.0, 0.0, 0.0)
