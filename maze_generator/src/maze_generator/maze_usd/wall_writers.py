"""Wall writer implementations for USD output."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from pxr import Sdf, UsdGeom, UsdPhysics, UsdShade

from ..maze_boolean.union import boolean_union_boxes, convex_segment_boxes, trimesh_to_usd_data
from ..maze_geometry.models import WallBox
from .mesh_primitives import box_mesh, sanitize_prim_name


@dataclass(frozen=True, slots=True)
class MergedWallWriter:
    def write(self, stage, walls: tuple[WallBox, ...], materials: dict[str, object]) -> None:
        if not walls:
            return
        self._write_boolean_merged(stage, walls, materials)

    def _write_boolean_merged(self, stage, walls: tuple[WallBox, ...], materials: dict[str, object]) -> None:
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
        material_faces: dict[str, list[int]] = defaultdict(list)

        for element_name, box_specs in sorted(grouped.items()):
            union_mesh = boolean_union_boxes(box_specs)
            vertices, face_counts, face_indices, uvs = trimesh_to_usd_data(union_mesh)

            all_points.extend(vertices)
            all_face_counts.extend(face_counts)
            all_face_indices.extend(index + vertex_offset for index in face_indices)
            all_uvs.extend(uvs)

            for local_face_index in range(len(face_counts)):
                material_faces[element_name].append(face_offset + local_face_index)

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

        for element_name, indices in sorted(material_faces.items()):
            subset = UsdGeom.Subset.Define(
                stage,
                f"/Maze/Walls/merged_walls/material_{sanitize_prim_name(element_name)}",
            )
            subset.CreateElementTypeAttr(UsdGeom.Tokens.face)
            subset.CreateIndicesAttr(indices)
            material = materials.get(element_name)
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
