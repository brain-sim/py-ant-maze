"""Material source configuration and validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Mapping

FaceSide = Literal["left", "right"]
_STRETCH_TEXTURE_MARKER = "_stretch"
_LEFT_FACE_MARKER = "_left"
_RIGHT_FACE_MARKER = "_right"
_FACE_MARKERS: tuple[FaceSide, ...] = ("left", "right")


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

    def get_texture(self, element_name: str, *, face: FaceSide | None = None) -> str | None:
        for candidate_name in _material_resolution_names(element_name, face=face):
            texture_path = self.textures.get(candidate_name)
            if texture_path is not None:
                return texture_path
        return None

    def get_usd_material(self, element_name: str, *, face: FaceSide | None = None) -> UsdMaterialRef | None:
        for candidate_name in _material_resolution_names(element_name, face=face):
            value = self.usd_materials.get(candidate_name)
            if value is None:
                continue
            if isinstance(value, UsdMaterialRef):
                return value
            return UsdMaterialRef.from_mapping(value, element_name=candidate_name)
        return None

    def resolve_for_usd(
        self,
        element_name: str,
        *,
        face: FaceSide | None = None,
    ) -> tuple[UsdMaterialRef | None, str | None]:
        """Resolve material candidates for USD export.

        Priority order:
        Base faces:
        1) USD material for `<element>_stretch`
        2) USD material for `<element>`
        3) texture for `<element>_stretch`
        4) texture for `<element>`

        Left/right faces:
        1) USD material for `<element>_<face>_stretch`
        2) USD material for `<element>_<face>`
        3) USD material for `<element>_stretch`
        4) USD material for `<element>`
        5) texture for `<element>_<face>_stretch`
        6) texture for `<element>_<face>`
        7) texture for `<element>_stretch`
        8) texture for `<element>`
        """
        usd_material = self.get_usd_material(element_name, face=face)
        if usd_material is not None:
            return usd_material, None
        return None, self.get_texture(element_name, face=face)

    def resolve_texture_for_obj(self, element_name: str, *, face: FaceSide | None = None) -> str | None:
        """Resolve texture candidate for OBJ export.

        Priority order:
        Base faces:
        1) texture for `<element>_stretch`
        2) texture for `<element>`

        Left/right faces:
        1) texture for `<element>_<face>_stretch`
        2) texture for `<element>_<face>`
        3) texture for `<element>_stretch`
        4) texture for `<element>`
        """
        return self.get_texture(element_name, face=face)

    def has_custom_material(self, element_name: str, *, face: FaceSide | None = None) -> bool:
        return any(
            candidate_name in self.textures or candidate_name in self.usd_materials
            for candidate_name in _material_resolution_names(element_name, face=face)
        )

    def has_face_override(self, element_name: str) -> bool:
        return any(
            candidate_name in self.textures or candidate_name in self.usd_materials
            for face in _FACE_MARKERS
            for candidate_name in _face_specific_resolution_names(element_name, face=face)
        )


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


def texture_name_requests_stretch(texture_path: str) -> bool:
    return _STRETCH_TEXTURE_MARKER in Path(texture_path).stem.lower()


def _material_resolution_names(
    element_name: str,
    *,
    face: FaceSide | None = None,
) -> tuple[str, ...]:
    _validate_element_name(element_name)
    stretch_name = f"{element_name}{_STRETCH_TEXTURE_MARKER}"
    if face is None:
        return stretch_name, element_name

    face_marker = _face_marker(face)
    face_name = f"{element_name}{face_marker}"
    stretch_face_name = f"{stretch_name}{face_marker}"
    return (
        f"{face_name}{_STRETCH_TEXTURE_MARKER}",
        stretch_face_name,
        face_name,
        stretch_name,
        element_name,
    )


def _face_specific_resolution_names(
    element_name: str,
    *,
    face: FaceSide,
) -> tuple[str, str, str]:
    _validate_element_name(element_name)
    face_marker = _face_marker(face)
    face_name = f"{element_name}{face_marker}"
    stretch_name = f"{element_name}{_STRETCH_TEXTURE_MARKER}"
    return f"{face_name}{_STRETCH_TEXTURE_MARKER}", f"{stretch_name}{face_marker}", face_name


def _face_marker(face: FaceSide) -> str:
    if face == "left":
        return _LEFT_FACE_MARKER
    if face == "right":
        return _RIGHT_FACE_MARKER
    raise ValueError(f"face must be 'left' or 'right', got {face!r}")
