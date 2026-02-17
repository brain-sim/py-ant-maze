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


def convex_segment_boxes(boxes: Iterable[BoxSpec], *, decimals: int = 9) -> list[BoxSpec]:
    """Cover the union of axis-aligned boxes with non-overlapping convex box segments."""
    box_list = list(boxes)
    if not box_list:
        raise ValueError("convex_segment_boxes requires at least one box")

    bounds = [_box_bounds(center, size, decimals=decimals) for center, size in box_list]
    x_breaks = sorted({x for mins, maxs in bounds for x in (mins[0], maxs[0])})
    y_breaks = sorted({y for mins, maxs in bounds for y in (mins[1], maxs[1])})
    z_breaks = sorted({z for mins, maxs in bounds for z in (mins[2], maxs[2])})

    x_index = {value: index for index, value in enumerate(x_breaks)}
    y_index = {value: index for index, value in enumerate(y_breaks)}
    z_index = {value: index for index, value in enumerate(z_breaks)}

    occupied = np.zeros((len(x_breaks) - 1, len(y_breaks) - 1, len(z_breaks) - 1), dtype=bool)
    for mins, maxs in bounds:
        x0, x1 = x_index[mins[0]], x_index[maxs[0]]
        y0, y1 = y_index[mins[1]], y_index[maxs[1]]
        z0, z1 = z_index[mins[2]], z_index[maxs[2]]
        occupied[x0:x1, y0:y1, z0:z1] = True

    segments: list[BoxSpec] = []
    while True:
        filled = np.argwhere(occupied)
        if len(filled) == 0:
            break

        x0, y0, z0 = (int(value) for value in filled[0])
        x1 = _expand_x(occupied, x0, y0, z0)
        y1 = _expand_y(occupied, x0, x1, y0, z0)
        z1 = _expand_z(occupied, x0, x1, y0, y1, z0)

        occupied[x0:x1, y0:y1, z0:z1] = False

        mins = (x_breaks[x0], y_breaks[y0], z_breaks[z0])
        maxs = (x_breaks[x1], y_breaks[y1], z_breaks[z1])
        segments.append(_bounds_to_box(mins, maxs))

    return segments


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


def _expand_x(occupied: np.ndarray, x0: int, y0: int, z0: int) -> int:
    x1 = x0 + 1
    while x1 < occupied.shape[0] and occupied[x1, y0, z0]:
        x1 += 1
    return x1


def _expand_y(occupied: np.ndarray, x0: int, x1: int, y0: int, z0: int) -> int:
    y1 = y0 + 1
    while y1 < occupied.shape[1] and np.all(occupied[x0:x1, y1, z0]):
        y1 += 1
    return y1


def _expand_z(occupied: np.ndarray, x0: int, x1: int, y0: int, y1: int, z0: int) -> int:
    z1 = z0 + 1
    while z1 < occupied.shape[2] and np.all(occupied[x0:x1, y0:y1, z1]):
        z1 += 1
    return z1


def _box_bounds(center: Vec3, size: Vec3, *, decimals: int) -> tuple[Vec3, Vec3]:
    half_size = (size[0] / 2.0, size[1] / 2.0, size[2] / 2.0)
    mins = (
        _quantize(center[0] - half_size[0], decimals=decimals),
        _quantize(center[1] - half_size[1], decimals=decimals),
        _quantize(center[2] - half_size[2], decimals=decimals),
    )
    maxs = (
        _quantize(center[0] + half_size[0], decimals=decimals),
        _quantize(center[1] + half_size[1], decimals=decimals),
        _quantize(center[2] + half_size[2], decimals=decimals),
    )
    return mins, maxs


def _bounds_to_box(mins: Vec3, maxs: Vec3) -> BoxSpec:
    center = (
        (mins[0] + maxs[0]) / 2.0,
        (mins[1] + maxs[1]) / 2.0,
        (mins[2] + maxs[2]) / 2.0,
    )
    size = (
        maxs[0] - mins[0],
        maxs[1] - mins[1],
        maxs[2] - mins[2],
    )
    return center, size


def _quantize(value: float, *, decimals: int) -> float:
    rounded = float(round(float(value), decimals))
    if rounded == -0.0:
        return 0.0
    return rounded


def _require_manifold3d() -> None:
    if importlib.util.find_spec("manifold3d") is None:
        raise ImportError("manifold3d is required for merged wall generation. Install `manifold3d`.")
