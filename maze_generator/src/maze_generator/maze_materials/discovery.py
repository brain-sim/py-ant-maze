"""Asset discovery helpers for packaged default materials."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from pxr import Usd, UsdShade

from .source import MaterialSource, UsdMaterialRef

ALL_TEXTURE_PATTERNS: tuple[str, ...] = ("*.jpg", "*.jpeg", "*.png", "*.exr", "*.tif", "*.tiff")
ALL_USD_PATTERNS: tuple[str, ...] = ("*.usd", "*.usda", "*.usdc", "*.usdz")


def get_default_assets_path() -> Path:
    assets_path = Path(__file__).resolve().parent.parent / "default_assets"
    if not assets_path.is_dir():
        raise FileNotFoundError(f"default_assets directory not found: {assets_path}")
    return assets_path


def discover_default_materials(
    texture_pattern: str = "*.jpg",
    additional_patterns: Iterable[str] | None = None,
    usd_patterns: Iterable[str] | None = None,
    *,
    allow_empty: bool = False,
) -> MaterialSource:
    texture_patterns = [texture_pattern]
    if additional_patterns is not None:
        texture_patterns.extend(additional_patterns)
    usd_pattern_list = list(usd_patterns) if usd_patterns is not None else list(ALL_USD_PATTERNS)
    return _discover_materials(
        texture_patterns=texture_patterns,
        usd_patterns=usd_pattern_list,
        allow_empty=allow_empty,
    )


def discover_all_default_materials(*, allow_empty: bool = False) -> MaterialSource:
    return _discover_materials(
        texture_patterns=ALL_TEXTURE_PATTERNS,
        usd_patterns=ALL_USD_PATTERNS,
        allow_empty=allow_empty,
    )


def _discover_materials(
    *,
    texture_patterns: Iterable[str],
    usd_patterns: Iterable[str],
    allow_empty: bool,
) -> MaterialSource:
    texture_pattern_list = _normalize_patterns(texture_patterns, label="texture")
    usd_pattern_list = _normalize_patterns(usd_patterns, label="USD material")

    assets_path = get_default_assets_path()
    textures_path = assets_path / "textures"
    if not textures_path.is_dir():
        raise FileNotFoundError(f"textures directory not found: {textures_path}")
    materials_path = assets_path / "materials"
    if not materials_path.is_dir():
        raise FileNotFoundError(f"materials directory not found: {materials_path}")

    textures = _discover_textures(textures_path, texture_pattern_list)
    usd_materials = _discover_usd_materials(materials_path, usd_pattern_list)

    if not textures and not usd_materials and not allow_empty:
        texture_patterns_repr = ", ".join(texture_pattern_list)
        usd_patterns_repr = ", ".join(usd_pattern_list)
        raise FileNotFoundError(
            "No materials discovered from default_assets. "
            f"textures_path={textures_path} patterns=[{texture_patterns_repr}] "
            f"materials_path={materials_path} patterns=[{usd_patterns_repr}]"
        )

    return MaterialSource(textures=textures, usd_materials=usd_materials)


def _normalize_patterns(patterns: Iterable[str], *, label: str) -> list[str]:
    pattern_list = list(patterns)
    if not pattern_list:
        raise ValueError(f"at least one {label} pattern is required")
    for pattern in pattern_list:
        if not pattern:
            raise ValueError(f"{label} pattern must be non-empty")
    return pattern_list


def _discover_textures(textures_path: Path, patterns: list[str]) -> dict[str, str]:
    textures: dict[str, str] = {}
    for texture_file in _discover_files(textures_path, patterns, recursive=False):
        element_name = texture_file.stem
        _insert_unique(
            textures,
            element_name,
            str(texture_file.resolve()),
            asset_kind="texture",
        )
    return textures


def _discover_usd_materials(materials_path: Path, patterns: list[str]) -> dict[str, UsdMaterialRef]:
    usd_materials: dict[str, UsdMaterialRef] = {}
    for material_file in _discover_files(materials_path, patterns, recursive=True):
        stage = Usd.Stage.Open(str(material_file.resolve()))
        if stage is None:
            raise RuntimeError(f"Failed to open USD file during material discovery: {material_file}")

        material_paths = [
            prim.GetPath().pathString
            for prim in stage.Traverse()
            if prim.IsA(UsdShade.Material)
        ]
        if not material_paths:
            raise ValueError(f"No UsdShade.Material prims found in {material_file}")

        if len(material_paths) == 1:
            _insert_unique(
                usd_materials,
                _single_material_element_name(materials_path, material_file),
                UsdMaterialRef(file=str(material_file.resolve()), path=material_paths[0]),
                asset_kind="USD material",
            )
            continue

        for material_path in material_paths:
            element_name = material_path.rsplit("/", maxsplit=1)[-1]
            _insert_unique(
                usd_materials,
                element_name,
                UsdMaterialRef(file=str(material_file.resolve()), path=material_path),
                asset_kind="USD material",
            )
    return usd_materials


def _discover_files(directory: Path, patterns: list[str], *, recursive: bool) -> tuple[Path, ...]:
    found: dict[str, Path] = {}
    for pattern in patterns:
        iterator = directory.rglob(pattern) if recursive else directory.glob(pattern)
        for file_path in sorted(iterator):
            if file_path.is_file():
                found[str(file_path.resolve())] = file_path
    return tuple(found[key] for key in sorted(found))


def _single_material_element_name(materials_path: Path, material_file: Path) -> str:
    relative_path = material_file.relative_to(materials_path)
    if len(relative_path.parts) > 1:
        return relative_path.parts[0]
    return material_file.stem


def _insert_unique(values: dict[str, object], key: str, value: object, *, asset_kind: str) -> None:
    if key in values:
        raise ValueError(f"Duplicate discovered {asset_kind} for element {key!r}")
    values[key] = value
