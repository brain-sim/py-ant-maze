"""Top-level USD stage writer."""

from __future__ import annotations

from pathlib import Path

from pxr import Usd, UsdGeom

from ..maze_geometry.models import MazeGeometry
from ..maze_materials.color import MaterialMap
from ..maze_materials.source import MaterialSource, texture_name_requests_stretch
from .material_library import MaterialLibrary
from .wall_writers import (
    CompoundBoxColliderWriter,
    MergedWallWriter,
)


def write_usd(
    geometry: MazeGeometry,
    output_path: str,
    *,
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
    maze_root = UsdGeom.Xform.Define(stage, "/Maze")
    stage.SetDefaultPrim(maze_root.GetPrim())
    UsdGeom.Xform.Define(stage, "/Maze/Walls")
    UsdGeom.Xform.Define(stage, "/Maze/Materials")

    materials = MaterialLibrary(material_map=material_map, material_source=material_source).create(
        stage,
        geometry.element_names,
    )
    stretch_elements = _stretch_texture_elements(geometry, material_source)

    MergedWallWriter().write(
        stage,
        geometry.walls,
        materials,
        stretch_elements=stretch_elements,
    )
    CompoundBoxColliderWriter().write(stage, geometry.walls)

    stage.GetRootLayer().Save()
    if not output.is_file():
        raise RuntimeError(f"USD file was not written: {output}")


def _stretch_texture_elements(
    geometry: MazeGeometry,
    material_source: MaterialSource | None,
) -> set[str]:
    if material_source is None:
        return set()

    stretch_elements: set[str] = set()
    for element_name in geometry.element_names:
        _, texture_path = material_source.resolve_for_usd(element_name)
        if texture_path is not None and texture_name_requests_stretch(texture_path):
            stretch_elements.add(element_name)
    return stretch_elements
