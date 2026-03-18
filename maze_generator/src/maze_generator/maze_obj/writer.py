"""OBJ bundle writer with visual and collider outputs."""

from __future__ import annotations

import os
import shutil
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import trimesh

from ..maze_boolean.union import (
    boolean_union_boxes,
    convex_segment_boxes,
    create_box_trimesh,
    mesh_face_sides,
    mesh_face_varying_uvs,
)
from ..maze_geometry.models import MazeGeometry
from ..maze_materials.color import ColorResolver, MaterialMap
from ..maze_materials.source import FaceSide, MaterialSource, texture_name_requests_stretch

MaterialKey = tuple[str, FaceSide | None]


@dataclass(frozen=True, slots=True)
class ObjChunk:
    object_name: str
    material_name: str
    element_name: str
    face_side: FaceSide | None
    vertices: np.ndarray
    faces: np.ndarray
    uvs: np.ndarray


def write_obj_bundle(
    geometry: MazeGeometry,
    output_dir: str,
    *,
    material_map: MaterialMap | None = None,
    material_source: MaterialSource | None = None,
) -> None:
    if not isinstance(geometry, MazeGeometry):
        raise TypeError("geometry must be MazeGeometry")
    if not output_dir:
        raise ValueError("output_dir must be non-empty")

    bundle_dir = Path(output_dir).resolve()
    bundle_dir.mkdir(parents=True, exist_ok=True)
    texture_dir = bundle_dir / "textures"
    texture_dir.mkdir(parents=True, exist_ok=True)

    visual_obj = bundle_dir / "visual.obj"
    visual_mtl = bundle_dir / "visual.mtl"
    collider_obj = bundle_dir / "collider.obj"
    collider_mtl = bundle_dir / "collider.mtl"

    face_override_elements = _face_override_elements(geometry, material_source)
    material_requests = _material_requests(geometry, material_source)
    uv_modes = _material_request_uv_modes(material_requests, material_source)
    visual_chunks = _build_visual_chunks(
        geometry,
        face_override_elements=face_override_elements,
        uv_modes=uv_modes,
    )
    collider_chunks = _build_collider_chunks(geometry)

    _write_mtl(
        visual_mtl,
        visual_chunks,
        material_map=material_map,
        material_source=material_source,
        obj_dir=bundle_dir,
        texture_dir=texture_dir,
    )
    _write_obj_file(visual_obj, visual_mtl.name, visual_chunks)

    _write_single_color_mtl(collider_mtl, material_name="collider", color=(0.5, 0.5, 0.5))
    _write_obj_file(collider_obj, collider_mtl.name, collider_chunks)

    if not visual_obj.is_file():
        raise RuntimeError(f"OBJ file was not written: {visual_obj}")
    if not visual_mtl.is_file():
        raise RuntimeError(f"MTL file was not written: {visual_mtl}")
    if not collider_obj.is_file():
        raise RuntimeError(f"OBJ file was not written: {collider_obj}")
    if not collider_mtl.is_file():
        raise RuntimeError(f"MTL file was not written: {collider_mtl}")


def _build_visual_chunks(
    geometry: MazeGeometry,
    *,
    face_override_elements: set[str] | None = None,
    uv_modes: dict[MaterialKey, str] | None = None,
) -> list[ObjChunk]:
    grouped: dict[str, list[tuple[tuple[float, float, float], tuple[float, float, float]]]] = defaultdict(list)
    for wall in geometry.walls:
        grouped[wall.element_name].append((wall.center, wall.size))

    chunks: list[ObjChunk] = []
    face_overrides = face_override_elements or set()
    request_uv_modes = uv_modes or {}
    for element_name, box_specs in sorted(grouped.items()):
        tmesh = boolean_union_boxes(box_specs)
        if element_name in face_overrides:
            face_sides = mesh_face_sides(tmesh, collapse_caps=True)
            face_uv_modes = [
                request_uv_modes.get((element_name, face_side), "repeat")
                for face_side in face_sides
            ]
            vertices, faces, uvs = _mesh_with_uv(tmesh, face_uv_modes=face_uv_modes)
            chunks.extend(
                _partition_visual_chunks(
                    element_name,
                    vertices=vertices,
                    uvs=uvs,
                    face_sides=face_sides,
                )
            )
            continue

        vertices, faces, uvs = _mesh_with_uv(
            tmesh,
            uv_mode=request_uv_modes.get((element_name, None), "repeat"),
        )
        chunks.append(
            ObjChunk(
                object_name=f"visual_{_material_request_name(element_name, None)}",
                material_name=_material_request_name(element_name, None),
                element_name=element_name,
                face_side=None,
                vertices=vertices,
                faces=faces,
                uvs=uvs,
            )
        )

    return chunks


def _build_collider_chunks(geometry: MazeGeometry) -> list[ObjChunk]:
    if not geometry.walls:
        return []

    segments = convex_segment_boxes((wall.center, wall.size) for wall in geometry.walls)
    chunks: list[ObjChunk] = []
    for segment_index, (center, size) in enumerate(segments):
        tmesh = create_box_trimesh(center, size)
        vertices, faces, uvs = _mesh_with_uv(tmesh)
        chunks.append(
            ObjChunk(
                object_name=f"collider_{segment_index:04d}",
                material_name="collider",
                element_name="collider",
                face_side=None,
                vertices=vertices,
                faces=faces,
                uvs=uvs,
            )
        )
    return chunks


def _mesh_with_uv(
    mesh: trimesh.Trimesh,
    *,
    uv_mode: str = "repeat",
    face_uv_modes: list[str] | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if faces.ndim != 2 or faces.shape[1] != 3:
        raise ValueError("Wall mesh must be triangulated")

    expanded_vertices = vertices[faces.reshape(-1)]
    expanded_faces = np.arange(expanded_vertices.shape[0], dtype=np.int64).reshape(-1, 3)
    uvs = mesh_face_varying_uvs(mesh, uv_mode=uv_mode, face_uv_modes=face_uv_modes)

    return expanded_vertices, expanded_faces, uvs


def _partition_visual_chunks(
    element_name: str,
    *,
    vertices: np.ndarray,
    uvs: np.ndarray,
    face_sides: list[FaceSide | None],
) -> list[ObjChunk]:
    grouped_vertices: dict[FaceSide | None, list[np.ndarray]] = defaultdict(list)
    grouped_uvs: dict[FaceSide | None, list[np.ndarray]] = defaultdict(list)

    for face_index, face_side in enumerate(face_sides):
        start = face_index * 3
        end = start + 3
        grouped_vertices[face_side].append(vertices[start:end])
        grouped_uvs[face_side].append(uvs[start:end])

    chunks: list[ObjChunk] = []
    for face_side in (None, "left", "right"):
        face_vertices = grouped_vertices.get(face_side)
        if not face_vertices:
            continue

        chunk_vertices = np.concatenate(face_vertices, axis=0)
        chunk_uvs = np.concatenate(grouped_uvs[face_side], axis=0)
        chunk_faces = np.arange(len(chunk_vertices), dtype=np.int64).reshape(-1, 3)
        material_name = _material_request_name(element_name, face_side)
        chunks.append(
            ObjChunk(
                object_name=f"visual_{material_name}",
                material_name=material_name,
                element_name=element_name,
                face_side=face_side,
                vertices=chunk_vertices,
                faces=chunk_faces,
                uvs=chunk_uvs,
            )
        )
    return chunks


def _write_obj_file(output: Path, mtl_filename: str, chunks: list[ObjChunk]) -> None:
    lines: list[str] = ["# Generated by maze_generator", f"mtllib {mtl_filename}"]

    vertex_offset = 1
    uv_offset = 1

    for chunk in chunks:
        lines.append(f"o {chunk.object_name}")
        lines.append(f"usemtl {chunk.material_name}")

        for x, y, z in chunk.vertices:
            lines.append(f"v {x:.8f} {y:.8f} {z:.8f}")

        for u, v in chunk.uvs:
            lines.append(f"vt {u:.8f} {v:.8f}")

        for face in chunk.faces:
            a, b, c = face + vertex_offset
            ta, tb, tc = face + uv_offset
            lines.append(f"f {a}/{ta} {b}/{tb} {c}/{tc}")

        vertex_offset += len(chunk.vertices)
        uv_offset += len(chunk.uvs)

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_mtl(
    output: Path,
    chunks: list[ObjChunk],
    *,
    material_map: MaterialMap | None,
    material_source: MaterialSource | None,
    obj_dir: Path,
    texture_dir: Path,
) -> None:
    resolver = ColorResolver(material_map=material_map)
    emitted: set[str] = set()
    lines: list[str] = ["# Generated by maze_generator"]
    copied_textures: dict[Path, Path] = {}

    for chunk in chunks:
        if chunk.material_name in emitted:
            continue
        emitted.add(chunk.material_name)

        texture_path: str | None = None
        if material_source is not None:
            texture_path = material_source.resolve_texture_for_obj(
                chunk.element_name,
                face=chunk.face_side,
            )

        lines.append(f"newmtl {chunk.material_name}")
        lines.append("Ka 0.000000 0.000000 0.000000")
        lines.append("Ks 0.000000 0.000000 0.000000")
        lines.append("d 1.000000")
        lines.append("illum 2")

        if texture_path is not None:
            resolved_texture = _resolve_existing_texture(texture_path)
            write_texture_path = _copy_texture_to_dir(
                resolved_texture,
                texture_dir,
                copied_textures,
            )
            lines.append("Kd 1.000000 1.000000 1.000000")
            lines.append(f"map_Kd {_to_relative_texture_path(str(write_texture_path), obj_dir)}")
        else:
            color = resolver.resolve(chunk.element_name)
            lines.append(f"Kd {color[0]:.6f} {color[1]:.6f} {color[2]:.6f}")

        lines.append("")

    output.write_text("\n".join(lines), encoding="utf-8")


def _write_single_color_mtl(output: Path, *, material_name: str, color: tuple[float, float, float]) -> None:
    lines = [
        "# Generated by maze_generator",
        f"newmtl {material_name}",
        "Ka 0.000000 0.000000 0.000000",
        "Ks 0.000000 0.000000 0.000000",
        "d 1.000000",
        "illum 2",
        f"Kd {color[0]:.6f} {color[1]:.6f} {color[2]:.6f}",
        "",
    ]
    output.write_text("\n".join(lines), encoding="utf-8")


def _resolve_existing_texture(texture_path: str) -> Path:
    resolved = Path(texture_path).expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"Texture file not found: {texture_path}")
    return resolved


def _copy_texture_to_dir(source: Path, texture_dir: Path, copied_textures: dict[Path, Path]) -> Path:
    cached = copied_textures.get(source)
    if cached is not None:
        return cached

    target = texture_dir / source.name
    if target.exists() and not _same_file(target, source):
        stem = source.stem
        suffix = source.suffix
        idx = 1
        while True:
            candidate = texture_dir / f"{stem}_{idx}{suffix}"
            if not candidate.exists() or _same_file(candidate, source):
                target = candidate
                break
            idx += 1

    if not target.exists():
        shutil.copy2(source, target)

    copied_textures[source] = target
    return target


def _same_file(path_a: Path, path_b: Path) -> bool:
    try:
        return path_a.samefile(path_b)
    except FileNotFoundError:
        return False


def _to_relative_texture_path(texture_path: str, obj_dir: Path) -> str:
    path = Path(texture_path).resolve()
    try:
        rel = path.relative_to(obj_dir)
    except ValueError:
        rel = Path(os.path.relpath(path, obj_dir))
    return rel.as_posix()


def _sanitize_name(name: str) -> str:
    clean = "".join(char if char.isalnum() or char == "_" else "_" for char in name.strip())
    if not clean:
        raise ValueError("Material name cannot be empty after sanitization")
    if clean[0].isdigit():
        return f"n_{clean}"
    return clean


def _material_request_name(element_name: str, face: FaceSide | None) -> str:
    if face is None:
        return _sanitize_name(element_name)
    return _sanitize_name(f"{element_name}_{face}")


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
) -> tuple[MaterialKey, ...]:
    requests: list[MaterialKey] = []
    for element_name in geometry.element_names:
        if material_source is not None and material_source.has_face_override(element_name):
            requests.append((element_name, "left"))
            requests.append((element_name, "right"))
            continue
        requests.append((element_name, None))
    return tuple(requests)


def _material_request_uv_modes(
    material_requests: tuple[MaterialKey, ...],
    material_source: MaterialSource | None,
) -> dict[MaterialKey, str]:
    uv_modes: dict[MaterialKey, str] = {}
    for element_name, face in material_requests:
        if material_source is None:
            uv_modes[(element_name, face)] = "repeat"
            continue
        texture_path = material_source.resolve_texture_for_obj(element_name, face=face)
        uv_modes[(element_name, face)] = (
            "stretch"
            if texture_path is not None and texture_name_requests_stretch(texture_path)
            else "repeat"
        )
    return uv_modes
