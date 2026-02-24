"""Export options for geometry outputs."""

from __future__ import annotations

from dataclasses import dataclass

from .maze_geometry.models import CoordinateFrame, MazeGeometry


@dataclass(frozen=True, slots=True)
class ExportOptions:
    """Export-time controls applied to extracted geometry."""

    target_frame: CoordinateFrame = "simulation"

    def __post_init__(self) -> None:
        if self.target_frame not in ("config", "simulation"):
            raise ValueError(
                "target_frame must be one of ('config', 'simulation')"
            )

    def apply_to_geometry(self, geometry: MazeGeometry) -> MazeGeometry:
        if not isinstance(geometry, MazeGeometry):
            raise TypeError("geometry must be MazeGeometry")
        return geometry.to_frame(self.target_frame)
