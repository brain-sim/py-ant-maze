"""Shared types and rendering constants for config-to-image conversion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal, Tuple

RGB = Tuple[int, int, int]
Layer = Literal["cell", "wall", "corner"]


@dataclass(frozen=True)
class RenderSizing:
    min_cell_size: int = 24
    max_cell_size: int = 48
    target_dimension: int = 600
    occupancy_gap: int = 2
    occupancy_padding: int = 2
    edge_container_padding: int = 8
    frame_padding: int = 8


@dataclass(frozen=True)
class RenderPalette:
    image_background: RGB = (30, 41, 59)
    occupancy_container: RGB = (48, 59, 78)
    edge_container: RGB = (23, 32, 51)
    cell: Dict[str, RGB] = None  # type: ignore[assignment]
    wall: Dict[str, RGB] = None  # type: ignore[assignment]
    legacy: Dict[str, RGB] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        default_cell = {
            "wall": (51, 65, 85),
            "open": (248, 250, 252),
            "start": (16, 185, 129),
            "goal": (244, 63, 94),
        }
        default_wall = {
            "wall": (71, 85, 105),
            "open": (226, 232, 240),
            "empty": (226, 232, 240),
        }
        default_legacy = {
            **default_cell,
            "empty": (226, 232, 240),
        }

        if self.cell is None:
            object.__setattr__(self, "cell", default_cell)
        if self.wall is None:
            object.__setattr__(self, "wall", default_wall)
        if self.legacy is None:
            object.__setattr__(self, "legacy", default_legacy)
