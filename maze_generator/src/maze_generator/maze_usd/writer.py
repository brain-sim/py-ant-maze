"""Top-level USD stage writer."""

from __future__ import annotations

from pathlib import Path

from pxr import Usd, UsdGeom

from ..maze_geometry.models import MazeGeometry
from ..maze_materials.color import MaterialMap
from ..maze_materials.source import MaterialSource
from .material_library import MaterialLibrary
from .wall_writers import IndividualWallWriter, MergedWallWriter, WallWriter


def write_usd(
    geometry: MazeGeometry,
    output_path: str,
    *,
    merge: bool = False,
    material_map: MaterialMap | None = None,
    material_source: MaterialSource | None = None,
) -> None:
    if not isinstance(geometry, MazeGeometry):
        raise TypeError("geometry must be MazeGeometry")
    if not output_path:
        raise ValueError("output_path must be non-empty")

    output = Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    stage = Usd.Stage.CreateNew(str(output))
    if stage is None:
        raise RuntimeError(f"Failed to create USD stage: {output}")

    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    UsdGeom.Xform.Define(stage, "/Maze")
    UsdGeom.Xform.Define(stage, "/Maze/Walls")
    UsdGeom.Xform.Define(stage, "/Maze/Materials")

    materials = MaterialLibrary(material_map=material_map, material_source=material_source).create(
        stage,
        geometry.element_names,
    )

    wall_writer: WallWriter = MergedWallWriter() if merge else IndividualWallWriter()
    wall_writer.write(stage, geometry.walls, materials)

    stage.GetRootLayer().Save()
    if not output.is_file():
        raise RuntimeError(f"USD file was not written: {output}")
