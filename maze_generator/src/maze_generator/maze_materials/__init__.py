"""Materials package."""

from .color import Color, ColorResolver, MaterialMap, resolve_color
from .discovery import discover_all_default_materials, discover_default_materials, get_default_assets_path
from .source import MaterialSource, UsdMaterialRef
from .usd_nodes import create_preview_material, create_texture_material, reference_usd_material

__all__ = [
    "Color",
    "ColorResolver",
    "MaterialMap",
    "MaterialSource",
    "UsdMaterialRef",
    "create_preview_material",
    "create_texture_material",
    "discover_all_default_materials",
    "discover_default_materials",
    "get_default_assets_path",
    "reference_usd_material",
    "resolve_color",
]
