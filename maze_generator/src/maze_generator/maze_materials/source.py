"""Material source configuration and validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True, slots=True)
class UsdMaterialRef:
    file: str
    path: str

    def __post_init__(self) -> None:
        if not self.file:
            raise ValueError("USD material file path must be non-empty")
        if not self.path:
            raise ValueError("USD material prim path must be non-empty")
        if not self.path.startswith("/"):
            raise ValueError(f"USD material prim path must be absolute: {self.path!r}")
        if not Path(self.file).is_file():
            raise FileNotFoundError(f"USD material file not found: {self.file}")

    @classmethod
    def from_mapping(cls, value: Mapping[str, str], *, element_name: str) -> "UsdMaterialRef":
        file_path = value.get("file")
        prim_path = value.get("path")
        if file_path is None or prim_path is None:
            raise ValueError(f"USD material for {element_name!r} must include 'file' and 'path'")
        return cls(file=file_path, path=prim_path)


@dataclass(frozen=True, slots=True)
class MaterialSource:
    textures: dict[str, str] = field(default_factory=dict)
    usd_materials: dict[str, UsdMaterialRef | Mapping[str, str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "textures", _normalize_textures(self.textures))
        object.__setattr__(self, "usd_materials", _normalize_usd_materials(self.usd_materials))

    def get_texture(self, element_name: str) -> str | None:
        return self.textures.get(element_name)

    def get_usd_material(self, element_name: str) -> UsdMaterialRef | None:
        value = self.usd_materials.get(element_name)
        if value is None:
            return None
        if isinstance(value, UsdMaterialRef):
            return value
        return UsdMaterialRef.from_mapping(value, element_name=element_name)

    def has_custom_material(self, element_name: str) -> bool:
        return element_name in self.textures or element_name in self.usd_materials


def _normalize_textures(textures: Mapping[str, str]) -> dict[str, str]:
    if not isinstance(textures, Mapping):
        raise TypeError("textures must be a mapping of element_name -> file path")
    normalized: dict[str, str] = {}
    for element_name, texture_path in textures.items():
        _validate_element_name(element_name)
        if not texture_path:
            raise ValueError(f"Texture path for {element_name!r} must be non-empty")
        path = Path(texture_path)
        if not path.is_file():
            raise FileNotFoundError(f"Texture file not found for {element_name!r}: {texture_path}")
        normalized[element_name] = str(path.resolve())
    return normalized


def _normalize_usd_materials(
    usd_materials: Mapping[str, UsdMaterialRef | Mapping[str, str]],
) -> dict[str, UsdMaterialRef]:
    if not isinstance(usd_materials, Mapping):
        raise TypeError("usd_materials must be a mapping of element_name -> material reference")
    normalized: dict[str, UsdMaterialRef] = {}
    for element_name, value in usd_materials.items():
        _validate_element_name(element_name)
        if isinstance(value, UsdMaterialRef):
            normalized[element_name] = value
            continue
        if not isinstance(value, Mapping):
            raise TypeError(f"USD material for {element_name!r} must be UsdMaterialRef or mapping")
        normalized[element_name] = UsdMaterialRef.from_mapping(value, element_name=element_name)
    return normalized


def _validate_element_name(element_name: str) -> None:
    if not isinstance(element_name, str):
        raise TypeError("element name must be a string")
    if not element_name:
        raise ValueError("element name must be non-empty")
