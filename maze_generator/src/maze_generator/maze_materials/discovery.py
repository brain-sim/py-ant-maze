"""Asset discovery helpers for packaged default materials."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .source import MaterialSource

ALL_TEXTURE_PATTERNS: tuple[str, ...] = ("*.jpg", "*.jpeg", "*.png", "*.exr", "*.tif", "*.tiff")


def get_default_assets_path() -> Path:
    assets_path = Path(__file__).resolve().parent.parent / "default_assets"
    if not assets_path.is_dir():
        raise FileNotFoundError(f"default_assets directory not found: {assets_path}")
    return assets_path


def discover_default_materials(
    texture_pattern: str = "*.jpg",
    additional_patterns: Iterable[str] | None = None,
    *,
    allow_empty: bool = False,
) -> MaterialSource:
    patterns = [texture_pattern]
    if additional_patterns is not None:
        patterns.extend(additional_patterns)
    return _discover_materials(patterns, allow_empty=allow_empty)


def discover_all_default_materials(*, allow_empty: bool = False) -> MaterialSource:
    return _discover_materials(ALL_TEXTURE_PATTERNS, allow_empty=allow_empty)


def _discover_materials(patterns: Iterable[str], *, allow_empty: bool) -> MaterialSource:
    pattern_list = list(patterns)
    if not pattern_list:
        raise ValueError("at least one texture pattern is required")

    textures_path = get_default_assets_path() / "textures"
    if not textures_path.is_dir():
        raise FileNotFoundError(f"textures directory not found: {textures_path}")

    textures: dict[str, str] = {}
    for pattern in pattern_list:
        if not pattern:
            raise ValueError("texture pattern must be non-empty")
        for texture_file in sorted(textures_path.glob(pattern)):
            if not texture_file.is_file():
                continue
            textures[texture_file.stem] = str(texture_file.resolve())

    if not textures and not allow_empty:
        patterns_repr = ", ".join(pattern_list)
        raise FileNotFoundError(f"No textures found in {textures_path} for patterns: {patterns_repr}")

    return MaterialSource(textures=textures)
