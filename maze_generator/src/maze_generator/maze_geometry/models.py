"""Geometry domain models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

Vec3 = tuple[float, float, float]
CoordinateFrame = Literal["config", "simulation_genesis", "simulation_isaac"]
_FRAME_CONFIG = "config"
_FRAME_SIMULATION_GENESIS = "simulation_genesis"
_FRAME_SIMULATION_ISAAC = "simulation_isaac"
_VALID_COORDINATE_FRAMES = (
    _FRAME_CONFIG,
    _FRAME_SIMULATION_GENESIS,
    _FRAME_SIMULATION_ISAAC,
)
_CANONICAL_COORDINATE_FRAMES = (
    _FRAME_CONFIG,
    _FRAME_SIMULATION_GENESIS,
    _FRAME_SIMULATION_ISAAC,
)


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


def normalize_coordinate_frame(value: str) -> str:
    frame = str(value).strip().lower()
    if frame not in _VALID_COORDINATE_FRAMES:
        raise ValueError(
            f"frame must be one of {_VALID_COORDINATE_FRAMES}, got {value!r}"
        )
    return frame


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
    frame: CoordinateFrame = "config"

    def __post_init__(self) -> None:
        _validate_positive_vec3(self.bounds, field_name="bounds")
        normalized = normalize_coordinate_frame(self.frame)
        if normalized not in _CANONICAL_COORDINATE_FRAMES:
            raise ValueError(
                f"frame must be one of {_VALID_COORDINATE_FRAMES}, got {self.frame!r}"
            )
        object.__setattr__(self, "frame", normalized)

    @classmethod
    def from_walls(
        cls,
        walls: Iterable[WallBox],
        bounds: Vec3,
        *,
        frame: CoordinateFrame = "config",
    ) -> "MazeGeometry":
        return cls(tuple(walls), bounds, frame=frame)

    @property
    def element_names(self) -> tuple[str, ...]:
        return tuple(sorted({wall.element_name for wall in self.walls}))

    def to_frame(self, target_frame: CoordinateFrame) -> "MazeGeometry":
        normalized_target = normalize_coordinate_frame(target_frame)
        if normalized_target == self.frame:
            return self

        transformed_walls = tuple(
            WallBox(
                center=_transform_center(
                    wall.center,
                    bounds=self.bounds,
                    source_frame=self.frame,
                    target_frame=normalized_target,
                ),
                size=wall.size,
                element_name=wall.element_name,
            )
            for wall in self.walls
        )
        return MazeGeometry(transformed_walls, self.bounds, frame=normalized_target)


def _transform_center(
    center: Vec3,
    *,
    bounds: Vec3,
    source_frame: str,
    target_frame: str,
) -> Vec3:
    x_cfg, y_cfg, z_cfg = _to_config_frame_xyz(center, bounds=bounds, frame=source_frame)
    return _from_config_frame_xyz(x_cfg, y_cfg, z_cfg, bounds=bounds, frame=target_frame)


def _to_config_frame_xyz(center: Vec3, *, bounds: Vec3, frame: str) -> Vec3:
    normalized_frame = normalize_coordinate_frame(frame)
    width, height, _ = bounds
    x, y, z = center

    if normalized_frame == _FRAME_CONFIG:
        return x, y, z
    if normalized_frame == _FRAME_SIMULATION_GENESIS:
        return x, height - y, z
    if normalized_frame == _FRAME_SIMULATION_ISAAC:
        return width - x, height - y, z
    raise ValueError(f"Unsupported source frame: {normalized_frame!r}")


def _from_config_frame_xyz(
    x_cfg: float,
    y_cfg: float,
    z_cfg: float,
    *,
    bounds: Vec3,
    frame: str,
) -> Vec3:
    normalized_frame = normalize_coordinate_frame(frame)
    width, height, _ = bounds

    if normalized_frame == _FRAME_CONFIG:
        return (x_cfg, y_cfg, z_cfg)
    if normalized_frame == _FRAME_SIMULATION_GENESIS:
        return (x_cfg, height - y_cfg, z_cfg)
    if normalized_frame == _FRAME_SIMULATION_ISAAC:
        return (width - x_cfg, height - y_cfg, z_cfg)
    raise ValueError(f"Unsupported target frame: {normalized_frame!r}")
