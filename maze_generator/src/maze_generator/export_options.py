"""Export options for geometry outputs."""

from __future__ import annotations

from dataclasses import dataclass

from .maze_geometry.models import CoordinateFrame, MazeGeometry, normalize_coordinate_frame


@dataclass(frozen=True, slots=True)
class ExportOptions:
    """Export-time controls applied to extracted geometry."""

    target_frame: CoordinateFrame = "simulation_genesis"

    def __post_init__(self) -> None:
        normalized = normalize_coordinate_frame(self.target_frame)
        object.__setattr__(self, "target_frame", normalized)

    def apply_to_geometry(self, geometry: MazeGeometry) -> MazeGeometry:
        if not isinstance(geometry, MazeGeometry):
            raise TypeError("geometry must be MazeGeometry")
        return geometry.to_frame(self.target_frame)
