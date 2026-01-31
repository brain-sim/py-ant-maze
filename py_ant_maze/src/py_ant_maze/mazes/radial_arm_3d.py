from __future__ import annotations

from dataclasses import dataclass
from typing import List

from ..core.base import ConfigBase, LayoutBase
from ..core.connectors import Connector, connectors_to_spec, parse_connectors
from ..core.element_set import ElementSet
from ..core.maze_parsing import parse_cell_elements, parse_wall_elements
from ..core.multi_level import LevelDefinition, parse_level_layouts
from ..core.types import ConfigSpec, LayoutSpec
from ._three_d import ensure_required_elements, element_value, validate_connector_rules
from .radial_arm import RadialArmLayout


@dataclass(frozen=True)
class LevelLayout:
    definition: LevelDefinition
    layout: RadialArmLayout


class RadialArm3DConfig(ConfigBase):
    def __init__(self, cell_elements: ElementSet, wall_elements: ElementSet) -> None:
        self.cell_elements = cell_elements
        self.wall_elements = wall_elements

    @classmethod
    def from_spec(cls, spec: ConfigSpec) -> "RadialArm3DConfig":
        cell_elements = parse_cell_elements(
            spec,
            allow_elements_alias=True,
            reserved_defaults={"open": 0, "wall": 1, "elevator": 2, "escalator": 3},
        )
        wall_elements = parse_wall_elements(spec, reserved_defaults={"open": 0, "wall": 1})
        ensure_required_elements(cell_elements, context="config.cell_elements")
        return cls(cell_elements, wall_elements)

    def to_spec(self) -> ConfigSpec:
        return {
            "cell_elements": self.cell_elements.to_list(),
            "wall_elements": self.wall_elements.to_list(),
        }


class RadialArm3DLayout(LayoutBase):
    def __init__(self, levels: List[LevelLayout], connectors: List[Connector]) -> None:
        self.levels = levels
        self.connectors = connectors

    @classmethod
    def from_spec(
        cls,
        spec: LayoutSpec,
        config: RadialArm3DConfig,
    ) -> "RadialArm3DLayout":
        if not isinstance(spec, dict):
            raise TypeError("layout must be a mapping")
        levels_spec = spec.get("levels")
        if levels_spec is None:
            raise ValueError("layout.levels is required")

        parsed_levels = parse_level_layouts(levels_spec, context="layout.levels")
        levels = [
            LevelLayout(
                definition=level.definition,
                layout=RadialArmLayout.from_spec(level.layout_spec, config),
            )
            for level in parsed_levels
        ]

        connectors = parse_connectors(
            spec.get("connectors"),
            levels=[level.definition for level in levels],
            context="layout.connectors",
            allow_arm=True,
            require_arm=True,
        )
        _validate_connectors(connectors, levels, config)
        return cls(levels, connectors)

    def to_spec(self, config: RadialArm3DConfig, with_grid_numbers: bool) -> LayoutSpec:
        levels_spec = [
            {
                "id": level.definition.name,
                "layout": level.layout.to_spec(config, with_grid_numbers),
            }
            for level in self.levels
        ]
        mapping: LayoutSpec = {"levels": levels_spec}
        if self.connectors:
            mapping["connectors"] = connectors_to_spec(self.connectors)
        return mapping


def _validate_connectors(
    connectors: List[Connector],
    levels: List[LevelLayout],
    config: RadialArm3DConfig,
) -> None:
    if not connectors:
        return

    elevator_value = element_value(config.cell_elements, "elevator", context="config.cell_elements")
    escalator_value = element_value(config.cell_elements, "escalator", context="config.cell_elements")

    for index, connector in enumerate(connectors):
        context = f"layout.connectors[{index}]"
        validate_connector_rules(connector, context=context)
        _validate_location(connector.start, levels, context=f"{context}.from")
        _validate_location(connector.end, levels, context=f"{context}.to")
        expected = elevator_value if connector.kind == "elevator" else escalator_value
        _validate_cell_value(connector.start, levels, expected, context=f"{context}.from")
        _validate_cell_value(connector.end, levels, expected, context=f"{context}.to")


def _validate_location(location, levels: List[LevelLayout], *, context: str) -> None:
    arms = levels[location.level.index].layout.arms
    if location.arm is None:
        raise ValueError(f"{context}.arm is required")
    if location.arm >= len(arms):
        raise ValueError(f"{context}.arm is out of range")

    cells = arms[location.arm].cells
    height = len(cells)
    width = len(cells[0]) if cells else 0
    if location.row >= height:
        raise ValueError(f"{context}.row is out of range")
    if location.col >= width:
        raise ValueError(f"{context}.col is out of range")


def _validate_cell_value(
    location,
    levels: List[LevelLayout],
    expected: int,
    *,
    context: str,
) -> None:
    cells = levels[location.level.index].layout.arms[location.arm].cells
    if cells[location.row][location.col] != expected:
        raise ValueError(f"{context} must reference a matching connector cell")
