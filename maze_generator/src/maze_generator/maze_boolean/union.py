"""Boolean mesh operations used by merged wall export."""

from __future__ import annotations

import importlib.util
from typing import Iterable, Literal, Sequence, cast

import numpy as np
import trimesh
from pxr import Gf

from ..maze_geometry.models import Vec3

BoxSpec = tuple[Vec3, Vec3]
UvMode = Literal["repeat", "stretch"]
FaceSide = Literal["left", "right"]


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


def mesh_face_sides(mesh, *, collapse_caps: bool = False) -> list[FaceSide | None]:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if faces.ndim != 2 or faces.shape[1] != 3:
        raise ValueError("Wall mesh must be triangulated")

    face_sides: list[FaceSide | None] = []
    for face in faces:
        _, dominant_axis, dominant_sign = _face_normal_metadata(vertices, face)
        if dominant_axis == 2 and not collapse_caps:
            face_sides.append(None)
            continue
        face_sides.append("right" if dominant_sign >= 0 else "left")
    return face_sides


def mesh_face_varying_uvs(
    mesh,
    *,
    uv_mode: UvMode = "repeat",
    face_uv_modes: Sequence[UvMode] | None = None,
) -> np.ndarray:
    normalized_uv_mode = _normalize_uv_mode(uv_mode)
    normalized_face_uv_modes: list[UvMode] | None = None
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if faces.ndim != 2 or faces.shape[1] != 3:
        raise ValueError("Wall mesh must be triangulated")

    if face_uv_modes is not None:
        if len(face_uv_modes) != len(faces):
            raise ValueError(
                f"face_uv_modes must match face count: expected {len(faces)}, got {len(face_uv_modes)}"
            )
        normalized_face_uv_modes = [_normalize_uv_mode(value) for value in face_uv_modes]

    uvs = np.empty((faces.shape[0] * 3, 2), dtype=np.float64)
    component_labels: np.ndarray | None = None
    component_bounds: tuple[np.ndarray, np.ndarray] | None = None

    if len(faces) and (
        normalized_uv_mode == "stretch"
        or (normalized_face_uv_modes is not None and any(value == "stretch" for value in normalized_face_uv_modes))
    ):
        component_labels = _face_components(len(faces), np.asarray(mesh.face_adjacency, dtype=np.int64))
        component_bounds = _component_bounds(vertices, faces, component_labels)

    for face_idx, face in enumerate(faces):
        v0, v1, v2 = vertices[face]
        _, dominant_axis, _ = _face_normal_metadata(vertices, face)
        base = 3 * face_idx

        face_component_bounds = None
        if component_labels is not None and component_bounds is not None:
            component_index = int(component_labels[face_idx])
            mins, maxs = component_bounds
            face_component_bounds = mins[component_index], maxs[component_index]

        face_uv_mode = normalized_uv_mode
        if normalized_face_uv_modes is not None:
            face_uv_mode = normalized_face_uv_modes[face_idx]

        for local_idx, vertex in enumerate((v0, v1, v2)):
            u, v = _project_uv(
                vertex,
                dominant_axis,
                component_bounds=face_component_bounds,
                stretch=face_uv_mode == "stretch",
            )
            uvs[base + local_idx] = (u, v)

    return uvs


def trimesh_to_usd_data(
    mesh,
    *,
    uv_mode: UvMode = "repeat",
    face_uv_modes: Sequence[UvMode] | None = None,
) -> tuple[list, list[int], list[int], list]:
    """Convert trimesh to USD mesh data with face-varying UVs."""
    vertices = [Gf.Vec3f(*vertex) for vertex in mesh.vertices]
    face_counts = [3] * len(mesh.faces)
    face_indices = mesh.faces.flatten().tolist()
    uv_array = mesh_face_varying_uvs(mesh, uv_mode=uv_mode, face_uv_modes=face_uv_modes)
    uvs = [Gf.Vec2f(float(u), float(v)) for u, v in uv_array]

    return vertices, face_counts, face_indices, uvs


def _normalize_uv_mode(value: str) -> UvMode:
    normalized = str(value).strip().lower()
    if normalized not in {"repeat", "stretch"}:
        raise ValueError(f"uv_mode must be 'repeat' or 'stretch', got {value!r}")
    return cast(UvMode, normalized)


def _face_components(face_count: int, face_adjacency: np.ndarray) -> np.ndarray:
    labels = np.full(face_count, -1, dtype=np.int64)
    neighbors: list[list[int]] = [[] for _ in range(face_count)]

    for face_a, face_b in face_adjacency:
        a = int(face_a)
        b = int(face_b)
        neighbors[a].append(b)
        neighbors[b].append(a)

    component_index = 0
    for start_face in range(face_count):
        if labels[start_face] != -1:
            continue

        stack = [start_face]
        labels[start_face] = component_index
        while stack:
            face_index = stack.pop()
            for neighbor in neighbors[face_index]:
                if labels[neighbor] != -1:
                    continue
                labels[neighbor] = component_index
                stack.append(neighbor)

        component_index += 1

    return labels


def _face_normal_metadata(vertices: np.ndarray, face: np.ndarray) -> tuple[np.ndarray, int, float]:
    v0, v1, v2 = vertices[face]
    edge1 = v1 - v0
    edge2 = v2 - v0
    normal = np.cross(edge1, edge2)
    dominant_axis = int(np.argmax(np.abs(normal)))
    return normal, dominant_axis, float(normal[dominant_axis])


def _component_bounds(
    vertices: np.ndarray,
    faces: np.ndarray,
    component_labels: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    component_count = int(component_labels.max()) + 1
    mins = np.full((component_count, 3), np.inf, dtype=np.float64)
    maxs = np.full((component_count, 3), -np.inf, dtype=np.float64)

    for face_index, face in enumerate(faces):
        component_index = int(component_labels[face_index])
        face_vertices = vertices[face]
        mins[component_index] = np.minimum(mins[component_index], np.min(face_vertices, axis=0))
        maxs[component_index] = np.maximum(maxs[component_index], np.max(face_vertices, axis=0))

    return mins, maxs


def _project_uv(
    vertex: np.ndarray,
    dominant_axis: int,
    *,
    component_bounds: tuple[np.ndarray, np.ndarray] | None,
    stretch: bool,
) -> tuple[float, float]:
    if dominant_axis == 0:
        u_axis, v_axis = 1, 2
    elif dominant_axis == 1:
        u_axis, v_axis = 0, 2
    else:
        u_axis, v_axis = 0, 1

    u = float(vertex[u_axis])
    v = float(vertex[v_axis])
    if not stretch or component_bounds is None:
        return u, v

    mins, maxs = component_bounds
    return (
        _normalize_uv_coordinate(u, mins[u_axis], maxs[u_axis]),
        _normalize_uv_coordinate(v, mins[v_axis], maxs[v_axis]),
    )


def _normalize_uv_coordinate(value: float, lower: float, upper: float) -> float:
    span = upper - lower
    if span <= 1e-9:
        return 0.0
    normalized = (value - lower) / span
    if normalized < 0.0:
        return 0.0
    if normalized > 1.0:
        return 1.0
    return float(normalized)


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
