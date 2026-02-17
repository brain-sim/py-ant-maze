"""OBJ bundle writer with visual and collider outputs."""

from __future__ import annotations

import os
import shutil
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import trimesh

from ..maze_boolean.union import boolean_union_boxes, convex_segment_boxes, create_box_trimesh
from ..maze_geometry.models import MazeGeometry
from ..maze_materials.color import ColorResolver, MaterialMap
from ..maze_materials.source import MaterialSource


@dataclass(frozen=True, slots=True)
class ObjChunk:
    object_name: str
    material_name: str
    element_name: str
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

    visual_chunks = _build_visual_chunks(geometry)
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


def _build_visual_chunks(geometry: MazeGeometry) -> list[ObjChunk]:
    grouped: dict[str, list[tuple[tuple[float, float, float], tuple[float, float, float]]]] = defaultdict(list)
    for wall in geometry.walls:
        grouped[wall.element_name].append((wall.center, wall.size))

    chunks: list[ObjChunk] = []
    for element_name, box_specs in sorted(grouped.items()):
        tmesh = boolean_union_boxes(box_specs)
        vertices, faces, uvs = _mesh_with_world_uv(tmesh)
        clean_name = _sanitize_name(element_name)
        chunks.append(
            ObjChunk(
                object_name=f"visual_{clean_name}",
                material_name=clean_name,
                element_name=element_name,
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
        vertices, faces, uvs = _mesh_with_world_uv(tmesh)
        chunks.append(
            ObjChunk(
                object_name=f"collider_{segment_index:04d}",
                material_name="collider",
                element_name="collider",
                vertices=vertices,
                faces=faces,
                uvs=uvs,
            )
        )
    return chunks


def _mesh_with_world_uv(mesh: trimesh.Trimesh) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if faces.ndim != 2 or faces.shape[1] != 3:
        raise ValueError("Wall mesh must be triangulated")

    expanded_vertices = vertices[faces.reshape(-1)]
    expanded_faces = np.arange(expanded_vertices.shape[0], dtype=np.int64).reshape(-1, 3)
    uvs = np.empty((expanded_vertices.shape[0], 2), dtype=np.float64)

    for face_idx, face in enumerate(faces):
        v0, v1, v2 = vertices[face]
        edge1 = v1 - v0
        edge2 = v2 - v0
        normal = np.cross(edge1, edge2)
        dominant_axis = int(np.argmax(np.abs(normal)))
        base = 3 * face_idx

        for local_idx, vertex in enumerate((v0, v1, v2)):
            if dominant_axis == 0:
                u, v = vertex[1], vertex[2]
            elif dominant_axis == 1:
                u, v = vertex[0], vertex[2]
            else:
                u, v = vertex[0], vertex[1]
            uvs[base + local_idx] = (float(u), float(v))

    return expanded_vertices, expanded_faces, uvs


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
            texture_path = material_source.get_texture(chunk.element_name)

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
