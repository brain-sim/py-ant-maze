"""USD mesh primitive utilities."""

from __future__ import annotations

from pxr import Gf


def box_mesh(
    center: tuple[float, float, float],
    size: tuple[float, float, float],
) -> tuple[list, list, list, list]:
    cx, cy, cz = center
    hw, hd, hh = size[0] / 2.0, size[1] / 2.0, size[2] / 2.0

    points = [
        Gf.Vec3f(cx - hw, cy - hd, cz - hh),
        Gf.Vec3f(cx + hw, cy - hd, cz - hh),
        Gf.Vec3f(cx + hw, cy + hd, cz - hh),
        Gf.Vec3f(cx - hw, cy + hd, cz - hh),
        Gf.Vec3f(cx - hw, cy - hd, cz + hh),
        Gf.Vec3f(cx + hw, cy - hd, cz + hh),
        Gf.Vec3f(cx + hw, cy + hd, cz + hh),
        Gf.Vec3f(cx - hw, cy + hd, cz + hh),
    ]

    face_vertex_counts = [4, 4, 4, 4, 4, 4]
    face_vertex_indices = [
        0, 3, 2, 1,
        4, 5, 6, 7,
        0, 1, 5, 4,
        2, 3, 7, 6,
        0, 4, 7, 3,
        1, 2, 6, 5,
    ]

    uvs = [
        Gf.Vec2f(0, 0), Gf.Vec2f(1, 0), Gf.Vec2f(1, 1), Gf.Vec2f(0, 1),
        Gf.Vec2f(0, 0), Gf.Vec2f(1, 0), Gf.Vec2f(1, 1), Gf.Vec2f(0, 1),
        Gf.Vec2f(0, 0), Gf.Vec2f(1, 0), Gf.Vec2f(1, 1), Gf.Vec2f(0, 1),
        Gf.Vec2f(0, 0), Gf.Vec2f(1, 0), Gf.Vec2f(1, 1), Gf.Vec2f(0, 1),
        Gf.Vec2f(0, 0), Gf.Vec2f(1, 0), Gf.Vec2f(1, 1), Gf.Vec2f(0, 1),
        Gf.Vec2f(0, 0), Gf.Vec2f(1, 0), Gf.Vec2f(1, 1), Gf.Vec2f(0, 1),
    ]

    return points, face_vertex_counts, face_vertex_indices, uvs


def sanitize_prim_name(name: str) -> str:
    clean = "".join(char if char.isalnum() or char == "_" else "_" for char in name.strip())
    if not clean:
        raise ValueError("Prim name cannot be empty after sanitization")
    if clean[0].isdigit():
        return f"n_{clean}"
    return clean
