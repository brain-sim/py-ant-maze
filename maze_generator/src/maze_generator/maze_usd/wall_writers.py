"""Wall writer implementations for USD output."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from pxr import Sdf, UsdGeom, UsdPhysics, UsdShade

from ..maze_boolean.union import (
    boolean_union_boxes,
    convex_segment_boxes,
    mesh_face_sides,
    trimesh_to_usd_data,
)
from ..maze_geometry.models import WallBox
from .mesh_primitives import box_mesh, sanitize_prim_name

MaterialKey = tuple[str, str | None]


@dataclass(frozen=True, slots=True)
class MergedWallWriter:
    def write(
        self,
        stage,
        walls: tuple[WallBox, ...],
        materials: dict[MaterialKey, object],
        *,
        face_override_elements: set[str] | None = None,
        uv_modes: dict[MaterialKey, str] | None = None,
    ) -> None:
        if not walls:
            return
        self._write_boolean_merged(
            stage,
            walls,
            materials,
            face_override_elements=face_override_elements or set(),
            uv_modes=uv_modes or {},
        )

    def _write_boolean_merged(
        self,
        stage,
        walls: tuple[WallBox, ...],
        materials: dict[MaterialKey, object],
        *,
        face_override_elements: set[str],
        uv_modes: dict[MaterialKey, str],
    ) -> None:
        grouped: dict[str, list[tuple[tuple[float, float, float], tuple[float, float, float]]]] = defaultdict(list)
        for wall in walls:
            grouped[wall.element_name].append((wall.center, wall.size))

        mesh = UsdGeom.Mesh.Define(stage, "/Maze/Walls/merged_walls")
        all_points = []
        all_face_counts: list[int] = []
        all_face_indices: list[int] = []
        all_uvs = []
        vertex_offset = 0
        face_offset = 0
        material_faces: dict[MaterialKey, list[int]] = defaultdict(list)

        for element_name, box_specs in sorted(grouped.items()):
            union_mesh = boolean_union_boxes(box_specs)
            if element_name in face_override_elements:
                face_sides = mesh_face_sides(union_mesh)
                face_uv_modes = [
                    uv_modes.get((element_name, face_side), "repeat")
                    for face_side in face_sides
                ]
                vertices, face_counts, face_indices, uvs = trimesh_to_usd_data(
                    union_mesh,
                    face_uv_modes=face_uv_modes,
                )
            else:
                face_sides = [None] * len(union_mesh.faces)
                vertices, face_counts, face_indices, uvs = trimesh_to_usd_data(
                    union_mesh,
                    uv_mode=uv_modes.get((element_name, None), "repeat"),
                )

            all_points.extend(vertices)
            all_face_counts.extend(face_counts)
            all_face_indices.extend(index + vertex_offset for index in face_indices)
            all_uvs.extend(uvs)

            for local_face_index, face_side in enumerate(face_sides):
                material_faces[(element_name, face_side)].append(face_offset + local_face_index)

            vertex_offset += len(vertices)
            face_offset += len(face_counts)

        mesh.CreatePointsAttr(all_points)
        mesh.CreateFaceVertexCountsAttr(all_face_counts)
        mesh.CreateFaceVertexIndicesAttr(all_face_indices)
        mesh.CreateDoubleSidedAttr(True)

        uv_attr = UsdGeom.PrimvarsAPI(mesh).CreatePrimvar(
            "st",
            Sdf.ValueTypeNames.TexCoord2fArray,
            UsdGeom.Tokens.faceVarying,
        )
        uv_attr.Set(all_uvs)

        for material_key, indices in sorted(material_faces.items(), key=_material_key_sort_key):
            element_name, face_side = material_key
            subset = UsdGeom.Subset.Define(
                stage,
                f"/Maze/Walls/merged_walls/material_{_material_request_name(element_name, face_side)}",
            )
            subset.CreateElementTypeAttr(UsdGeom.Tokens.face)
            subset.CreateIndicesAttr(indices)
            material = materials.get(material_key)
            if material is not None:
                UsdShade.MaterialBindingAPI.Apply(subset.GetPrim()).Bind(material)


@dataclass(frozen=True, slots=True)
class CompoundBoxColliderWriter:
    def write(self, stage, walls: tuple[WallBox, ...]) -> None:
        if not walls:
            return

        UsdGeom.Xform.Define(stage, "/Maze/Colliders")
        segments = convex_segment_boxes((wall.center, wall.size) for wall in walls)

        for index, (center, size) in enumerate(segments):
            mesh = UsdGeom.Mesh.Define(stage, f"/Maze/Colliders/collider_{index:04d}")
            points, face_counts, face_indices, _ = box_mesh(center, size)
            mesh.CreatePointsAttr(points)
            mesh.CreateFaceVertexCountsAttr(face_counts)
            mesh.CreateFaceVertexIndicesAttr(face_indices)
            mesh.CreateDoubleSidedAttr(False)

            UsdGeom.Imageable(mesh).CreatePurposeAttr(UsdGeom.Tokens.guide)
            UsdPhysics.CollisionAPI.Apply(mesh.GetPrim())


def _material_key_sort_key(value: tuple[MaterialKey, list[int]]) -> tuple[str, int]:
    (element_name, face_side), _ = value
    face_order = {None: 0, "left": 1, "right": 2}
    return element_name, face_order[face_side]


def _material_request_name(element_name: str, face_side: str | None) -> str:
    if face_side is None:
        return sanitize_prim_name(element_name)
    return sanitize_prim_name(f"{element_name}_{face_side}")
