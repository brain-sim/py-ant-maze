"""Geometry domain models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

Vec3 = tuple[float, float, float]


def _validate_vec3(value: Vec3, *, field_name: str) -> None:
    if len(value) != 3:
        raise ValueError(f"{field_name} must have exactly 3 values")
    for component in value:
        if not isinstance(component, (int, float)):
            raise TypeError(f"{field_name} values must be numeric")


def _validate_positive_vec3(value: Vec3, *, field_name: str) -> None:
    _validate_vec3(value, field_name=field_name)
    for component in value:
        if component <= 0:
            raise ValueError(f"{field_name} values must be > 0")


@dataclass(frozen=True, slots=True)
class WallBox:
    center: Vec3
    size: Vec3
    element_name: str

    def __post_init__(self) -> None:
        if not self.element_name:
            raise ValueError("element_name must be non-empty")
        _validate_vec3(self.center, field_name="center")
        _validate_positive_vec3(self.size, field_name="size")


@dataclass(frozen=True, slots=True)
class MazeGeometry:
    walls: tuple[WallBox, ...]
    bounds: Vec3

    def __post_init__(self) -> None:
        _validate_positive_vec3(self.bounds, field_name="bounds")

    @classmethod
    def from_walls(cls, walls: Iterable[WallBox], bounds: Vec3) -> "MazeGeometry":
        return cls(tuple(walls), bounds)

    @property
    def element_names(self) -> tuple[str, ...]:
        return tuple(sorted({wall.element_name for wall in self.walls}))
