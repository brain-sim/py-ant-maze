"""USD shader/material construction helpers."""

from __future__ import annotations

from pathlib import Path

from pxr import Gf, Sdf, UsdShade

from .color import Color, validate_color


def create_preview_material(stage, mat_path: str, element_name: str, color: Color):
    _ = element_name
    validate_color(color, field_name="color")

    material = UsdShade.Material.Define(stage, mat_path)
    shader = UsdShade.Shader.Define(stage, f"{mat_path}/PreviewSurface")
    shader.CreateIdAttr("UsdPreviewSurface")
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color))
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.7)
    material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
    return material


def create_texture_material(stage, mat_path: str, element_name: str, texture_path: str):
    _ = element_name
    path = Path(texture_path)
    if not path.is_file():
        raise FileNotFoundError(f"Texture file not found: {texture_path}")

    material = UsdShade.Material.Define(stage, mat_path)
    shader = UsdShade.Shader.Define(stage, f"{mat_path}/PreviewSurface")
    shader.CreateIdAttr("UsdPreviewSurface")
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.7)

    primvar_reader = UsdShade.Shader.Define(stage, f"{mat_path}/PrimvarReader")
    primvar_reader.CreateIdAttr("UsdPrimvarReader_float2")
    primvar_reader.CreateInput("varname", Sdf.ValueTypeNames.Token).Set("st")

    texture_shader = UsdShade.Shader.Define(stage, f"{mat_path}/Texture")
    texture_shader.CreateIdAttr("UsdUVTexture")
    texture_shader.CreateInput("file", Sdf.ValueTypeNames.Asset).Set(str(path.resolve()))
    texture_shader.CreateInput("sourceColorSpace", Sdf.ValueTypeNames.Token).Set("sRGB")
    texture_shader.CreateInput("wrapS", Sdf.ValueTypeNames.Token).Set("repeat")
    texture_shader.CreateInput("wrapT", Sdf.ValueTypeNames.Token).Set("repeat")

    texture_shader.CreateInput("st", Sdf.ValueTypeNames.Float2).ConnectToSource(
        primvar_reader.ConnectableAPI(),
        "result",
    )
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(
        texture_shader.ConnectableAPI(),
        "rgb",
    )

    material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
    return material


def reference_usd_material(stage, mat_path: str, usd_file: str, material_path: str):
    file_path = Path(usd_file)
    if not file_path.is_file():
        raise FileNotFoundError(f"USD material file not found: {usd_file}")
    if not material_path.startswith("/"):
        raise ValueError(f"USD material path must be absolute: {material_path!r}")

    material_prim = stage.DefinePrim(mat_path)
    material_prim.GetReferences().AddReference(str(file_path.resolve()), material_path)
    return UsdShade.Material(material_prim)
