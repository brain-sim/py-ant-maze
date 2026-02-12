"""Procedural color resolution utilities."""

from __future__ import annotations

from dataclasses import dataclass, field

Color = tuple[float, float, float]
MaterialMap = dict[str, Color]

_DEFAULT_COLORS: MaterialMap = {
    "wall": (0.5, 0.5, 0.5),
    "door": (0.6, 0.3, 0.1),
    "open": (0.85, 0.85, 0.8),
}

_PALETTE: tuple[Color, ...] = (
    (0.8, 0.2, 0.2),
    (0.2, 0.6, 0.8),
    (0.2, 0.8, 0.3),
    (0.9, 0.7, 0.1),
    (0.7, 0.3, 0.7),
    (0.3, 0.7, 0.7),
)


@dataclass(slots=True)
class ColorResolver:
    material_map: MaterialMap | None = None
    _assigned: dict[str, Color] = field(default_factory=dict)

    def resolve(self, element_name: str) -> Color:
        if not element_name:
            raise ValueError("element_name must be non-empty")
        if self.material_map is not None and element_name in self.material_map:
            color = self.material_map[element_name]
            _validate_color(color, field_name=f"material_map[{element_name!r}]")
            return color
        if element_name in _DEFAULT_COLORS:
            return _DEFAULT_COLORS[element_name]
        color = self._assigned.get(element_name)
        if color is not None:
            return color
        color = _PALETTE[len(self._assigned) % len(_PALETTE)]
        self._assigned[element_name] = color
        return color


def resolve_color(
    element_name: str,
    material_map: MaterialMap | None,
    cache: dict[str, Color] | None = None,
) -> Color:
    resolver = ColorResolver(material_map=material_map)
    if cache:
        resolver._assigned.update(cache)
    color = resolver.resolve(element_name)
    if cache is not None and element_name not in cache and element_name not in _DEFAULT_COLORS:
        cache[element_name] = color
    return color


def validate_color(color: Color, *, field_name: str) -> None:
    _validate_color(color, field_name=field_name)


def _validate_color(color: Color, *, field_name: str) -> None:
    if len(color) != 3:
        raise ValueError(f"{field_name} must have exactly 3 values")
    for component in color:
        if not isinstance(component, (int, float)):
            raise TypeError(f"{field_name} values must be numeric")
        if component < 0 or component > 1:
            raise ValueError(f"{field_name} values must be in [0, 1]")
