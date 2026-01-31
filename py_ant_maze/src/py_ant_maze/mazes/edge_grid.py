from ..core.base import ConfigBase, LayoutBase
from ..core.element_set import ElementSet
from ..core.grid import parse_grid, format_grid
from ..core.maze_parsing import (
    parse_cell_elements,
    parse_wall_elements,
    validate_edge_grid_dimensions,
)
from ..core.types import ConfigSpec, Grid, LayoutSpec


class EdgeGridConfig(ConfigBase):
    def __init__(self, cell_elements: ElementSet, wall_elements: ElementSet) -> None:
        self.cell_elements = cell_elements
        self.wall_elements = wall_elements

    @classmethod
    def from_spec(cls, spec: ConfigSpec) -> "EdgeGridConfig":
        cell_elements = parse_cell_elements(spec, allow_elements_alias=True, reserved_defaults={"open": 0})
        wall_elements = parse_wall_elements(spec, reserved_defaults={"open": 0, "wall": 1})
        return cls(cell_elements, wall_elements)

    def to_spec(self) -> ConfigSpec:
        return {
            "cell_elements": self.cell_elements.to_list(),
            "wall_elements": self.wall_elements.to_list(),
        }


class EdgeGridLayout(LayoutBase):
    def __init__(
        self,
        cells: Grid,
        vertical_walls: Grid,
        horizontal_walls: Grid,
    ) -> None:
        self.cells = cells
        self.vertical_walls = vertical_walls
        self.horizontal_walls = horizontal_walls

    @classmethod
    def from_spec(
        cls,
        spec: LayoutSpec,
        config: EdgeGridConfig,
        *,
        context: str = "layout",
    ) -> "EdgeGridLayout":
        if not isinstance(spec, dict):
            raise TypeError("layout must be a mapping")
        cells_spec = spec.get("cells")
        walls_spec = spec.get("walls", {})
        if cells_spec is None:
            raise ValueError("layout.cells is required")
        if not isinstance(walls_spec, dict):
            raise TypeError("layout.walls must be a mapping")

        vertical_spec = walls_spec.get("vertical")
        horizontal_spec = walls_spec.get("horizontal")
        if vertical_spec is None or horizontal_spec is None:
            raise ValueError("layout.walls must include vertical and horizontal")

        cells = parse_grid(cells_spec, config.cell_elements)
        vertical = parse_grid(vertical_spec, config.wall_elements)
        horizontal = parse_grid(horizontal_spec, config.wall_elements)

        validate_edge_grid_dimensions(cells, vertical, horizontal, context=context)
        return cls(cells, vertical, horizontal)

    def to_spec(self, config: EdgeGridConfig, with_grid_numbers: bool) -> LayoutSpec:
        cells_lines = format_grid(self.cells, config.cell_elements, with_grid_numbers)
        vertical_lines = format_grid(self.vertical_walls, config.wall_elements, with_grid_numbers)
        horizontal_lines = format_grid(self.horizontal_walls, config.wall_elements, with_grid_numbers)
        cells_text = "\n".join(cells_lines)
        vertical_text = "\n".join(vertical_lines)
        horizontal_text = "\n".join(horizontal_lines)
        return {
            "cells": cells_text + "\n" if cells_text else cells_text,
            "walls": {
                "vertical": vertical_text + "\n" if vertical_text else vertical_text,
                "horizontal": horizontal_text + "\n" if horizontal_text else horizontal_text,
            },
        }
