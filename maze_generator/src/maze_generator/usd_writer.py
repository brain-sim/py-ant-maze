"""Write MazeGeometry to a USD file."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from .types import MazeGeometry, WallBox
from .materials import MaterialMap, resolve_color, create_preview_material


def write_usd(
    geometry: MazeGeometry,
    output_path: str,
    *,
    merge: bool = False,
    material_map: Optional[MaterialMap] = None,
) -> None:
    """Write maze wall geometry to a USD file.

    Args:
        geometry: Extracted MazeGeometry.
        output_path: File path for the output .usda/.usd file.
        merge: If True, merge walls sharing the same element_name into
            one mesh each. If False, each wall is a separate mesh prim.
        material_map: Optional dict mapping element_name -> (r, g, b).
    """
    from pxr import Usd, UsdGeom, Gf, Sdf

    stage = Usd.Stage.CreateNew(output_path)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)

    root = UsdGeom.Xform.Define(stage, "/Maze")
    walls_group = UsdGeom.Xform.Define(stage, "/Maze/Walls")
    materials_group = UsdGeom.Xform.Define(stage, "/Maze/Materials")

    # Create materials for each unique element_name
    element_names = set(w.element_name for w in geometry.walls)
    created_materials = {}
    for name in sorted(element_names):
        color = resolve_color(name, material_map)
        mat_path = f"/Maze/Materials/{_sanitize(name)}"
        mat = create_preview_material(stage, mat_path, name, color)
        created_materials[name] = mat

    if merge:
        _write_merged(stage, geometry.walls, created_materials)
    else:
        _write_individual(stage, geometry.walls, created_materials)

    stage.GetRootLayer().Save()


def _write_individual(stage, walls: List[WallBox], materials: dict) -> None:
    """Write each wall as a separate mesh prim."""
    from pxr import UsdGeom, UsdShade

    for i, wall in enumerate(walls):
        prim_path = f"/Maze/Walls/{_sanitize(wall.element_name)}_{i:04d}"
        mesh = UsdGeom.Mesh.Define(stage, prim_path)
        points, face_counts, face_indices = _box_mesh(wall.center, wall.size)
        mesh.CreatePointsAttr(points)
        mesh.CreateFaceVertexCountsAttr(face_counts)
        mesh.CreateFaceVertexIndicesAttr(face_indices)
        mesh.CreateDoubleSidedAttr(True)

        if wall.element_name in materials:
            UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(
                materials[wall.element_name]
            )


def _write_merged(stage, walls: List[WallBox], materials: dict) -> None:
    """Merge all walls with the same element_name into one mesh each."""
    from pxr import UsdGeom, UsdShade, Gf

    groups: Dict[str, List[WallBox]] = defaultdict(list)
    for wall in walls:
        groups[wall.element_name].append(wall)

    for name, group in sorted(groups.items()):
        prim_path = f"/Maze/Walls/{_sanitize(name)}"
        mesh = UsdGeom.Mesh.Define(stage, prim_path)

        all_points = []
        all_face_counts = []
        all_face_indices = []
        vertex_offset = 0

        for wall in group:
            points, face_counts, face_indices = _box_mesh(wall.center, wall.size)
            all_points.extend(points)
            all_face_counts.extend(face_counts)
            all_face_indices.extend([idx + vertex_offset for idx in face_indices])
            vertex_offset += len(points)

        mesh.CreatePointsAttr(all_points)
        mesh.CreateFaceVertexCountsAttr(all_face_counts)
        mesh.CreateFaceVertexIndicesAttr(all_face_indices)
        mesh.CreateDoubleSidedAttr(True)

        if name in materials:
            UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(materials[name])


def _box_mesh(
    center: Tuple[float, float, float],
    size: Tuple[float, float, float],
) -> Tuple[list, list, list]:
    """Generate box mesh data (8 vertices, 6 quad faces)."""
    from pxr import Gf

    cx, cy, cz = center
    hw, hd, hh = size[0] / 2.0, size[1] / 2.0, size[2] / 2.0

    points = [
        Gf.Vec3f(cx - hw, cy - hd, cz - hh),  # 0: bottom-left-front
        Gf.Vec3f(cx + hw, cy - hd, cz - hh),  # 1: bottom-right-front
        Gf.Vec3f(cx + hw, cy + hd, cz - hh),  # 2: bottom-right-back
        Gf.Vec3f(cx - hw, cy + hd, cz - hh),  # 3: bottom-left-back
        Gf.Vec3f(cx - hw, cy - hd, cz + hh),  # 4: top-left-front
        Gf.Vec3f(cx + hw, cy - hd, cz + hh),  # 5: top-right-front
        Gf.Vec3f(cx + hw, cy + hd, cz + hh),  # 6: top-right-back
        Gf.Vec3f(cx - hw, cy + hd, cz + hh),  # 7: top-left-back
    ]

    face_vertex_counts = [4, 4, 4, 4, 4, 4]
    face_vertex_indices = [
        0, 3, 2, 1,  # bottom (-Z)
        4, 5, 6, 7,  # top (+Z)
        0, 1, 5, 4,  # front (-Y)
        2, 3, 7, 6,  # back (+Y)
        0, 4, 7, 3,  # left (-X)
        1, 2, 6, 5,  # right (+X)
    ]

    return points, face_vertex_counts, face_vertex_indices


def _sanitize(name: str) -> str:
    """Make a string safe for use as a USD prim name."""
    return name.replace(" ", "_").replace("-", "_")
