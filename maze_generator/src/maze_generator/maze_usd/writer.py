"""Top-level USD stage writer."""

from __future__ import annotations

from pathlib import Path

from pxr import Usd, UsdGeom

from ..maze_geometry.models import MazeGeometry
from ..maze_materials.color import MaterialMap
from ..maze_materials.source import FaceSide, MaterialSource, texture_name_requests_stretch
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

    material_requests = _material_requests(geometry, material_source)
    materials = MaterialLibrary(material_map=material_map, material_source=material_source).create(
        stage,
        material_requests,
    )
    face_override_elements = _face_override_elements(geometry, material_source)
    uv_modes = _material_request_uv_modes(material_requests, material_source)

    MergedWallWriter().write(
        stage,
        geometry.walls,
        materials,
        face_override_elements=face_override_elements,
        uv_modes=uv_modes,
    )
    CompoundBoxColliderWriter().write(stage, geometry.walls)

    stage.GetRootLayer().Save()
    if not output.is_file():
        raise RuntimeError(f"USD file was not written: {output}")


def _face_override_elements(
    geometry: MazeGeometry,
    material_source: MaterialSource | None,
) -> set[str]:
    if material_source is None:
        return set()

    face_override_elements: set[str] = set()
    for element_name in geometry.element_names:
        if material_source.has_face_override(element_name):
            face_override_elements.add(element_name)
    return face_override_elements


def _material_requests(
    geometry: MazeGeometry,
    material_source: MaterialSource | None,
) -> tuple[tuple[str, FaceSide | None], ...]:
    requests: list[tuple[str, FaceSide | None]] = []
    for element_name in geometry.element_names:
        if material_source is not None and material_source.has_face_override(element_name):
            requests.append((element_name, "left"))
            requests.append((element_name, "right"))
            continue
        requests.append((element_name, None))
    return tuple(requests)


def _material_request_uv_modes(
    material_requests: tuple[tuple[str, FaceSide | None], ...],
    material_source: MaterialSource | None,
) -> dict[tuple[str, FaceSide | None], str]:
    uv_modes: dict[tuple[str, FaceSide | None], str] = {}
    for element_name, face in material_requests:
        if material_source is None:
            uv_modes[(element_name, face)] = "repeat"
            continue
        _, texture_path = material_source.resolve_for_usd(element_name, face=face)
        uv_modes[(element_name, face)] = (
            "stretch"
            if texture_path is not None and texture_name_requests_stretch(texture_path)
            else "repeat"
        )
    return uv_modes
