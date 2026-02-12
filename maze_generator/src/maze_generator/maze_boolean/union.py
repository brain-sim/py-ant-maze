"""Boolean mesh operations used by merged wall export."""

from __future__ import annotations

import importlib.util
from typing import Iterable

import numpy as np
import trimesh
from pxr import Gf

from ..maze_geometry.models import Vec3

BoxSpec = tuple[Vec3, Vec3]


def create_box_trimesh(center: Vec3, size: Vec3):
    box = trimesh.creation.box(extents=size)
    box.apply_translation(center)
    return box


def boolean_union_boxes(boxes: Iterable[BoxSpec]):
    _require_manifold3d()
    box_list = list(boxes)
    if not box_list:
        raise ValueError("boolean_union_boxes requires at least one box")

    meshes = [create_box_trimesh(center, size) for center, size in box_list]
    if len(meshes) == 1:
        return meshes[0]

    merged = trimesh.boolean.union(meshes, engine="manifold")
    if merged is None:
        raise RuntimeError("trimesh boolean union returned no mesh (engine='manifold')")
    return merged


def trimesh_to_usd_data(mesh) -> tuple[list, list[int], list[int], list]:
    """Convert trimesh to USD mesh data with world-space UVs."""
    vertices = [Gf.Vec3f(*vertex) for vertex in mesh.vertices]
    face_counts = [3] * len(mesh.faces)
    face_indices = mesh.faces.flatten().tolist()

    uvs = []
    for face in mesh.faces:
        v0, v1, v2 = mesh.vertices[face]
        edge1 = v1 - v0
        edge2 = v2 - v0
        normal = np.cross(edge1, edge2)
        dominant_axis = int(np.argmax(np.abs(normal)))

        for vertex in (v0, v1, v2):
            if dominant_axis == 0:
                u, v = vertex[1], vertex[2]
            elif dominant_axis == 1:
                u, v = vertex[0], vertex[2]
            else:
                u, v = vertex[0], vertex[1]
            uvs.append(Gf.Vec2f(float(u), float(v)))

    return vertices, face_counts, face_indices, uvs


def _require_manifold3d() -> None:
    if importlib.util.find_spec("manifold3d") is None:
        raise ImportError("manifold3d is required for merge=True. Install `manifold3d`.")
