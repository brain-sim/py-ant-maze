"""USD material utilities for maze walls."""

from __future__ import annotations

from typing import Dict, Tuple

Color = Tuple[float, float, float]
MaterialMap = Dict[str, Color]

# Default colors keyed by element_name
_DEFAULTS: MaterialMap = {
    "wall": (0.5, 0.5, 0.5),
    "door": (0.6, 0.3, 0.1),
    "open": (0.85, 0.85, 0.8),
}

# Palette for unknown element names
_PALETTE: list[Color] = [
    (0.8, 0.2, 0.2),
    (0.2, 0.6, 0.8),
    (0.2, 0.8, 0.3),
    (0.9, 0.7, 0.1),
    (0.7, 0.3, 0.7),
    (0.3, 0.7, 0.7),
]


def resolve_color(element_name: str, material_map: MaterialMap | None, _cache: dict[str, Color] = {}) -> Color:
    """Get the color for an element name."""
    if material_map and element_name in material_map:
        return material_map[element_name]
    if element_name in _DEFAULTS:
        return _DEFAULTS[element_name]
    if element_name not in _cache:
        idx = len(_cache) % len(_PALETTE)
        _cache[element_name] = _PALETTE[idx]
    return _cache[element_name]


def create_preview_material(stage, mat_path: str, element_name: str, color: Color):
    """Create a UsdPreviewSurface material at the given prim path."""
    from pxr import Sdf, UsdShade, Gf

    material = UsdShade.Material.Define(stage, mat_path)

    shader_path = f"{mat_path}/PreviewSurface"
    shader = UsdShade.Shader.Define(stage, shader_path)
    shader.CreateIdAttr("UsdPreviewSurface")
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color))
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.7)

    material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")

    return material
