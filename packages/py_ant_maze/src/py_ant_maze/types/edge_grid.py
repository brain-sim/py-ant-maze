from typing import Any, Dict, List

from ..element_set import ElementSet
from ..elements import CellElement, WallElement
from ..grid import parse_grid, format_grid


class EdgeGridConfig:
    def __init__(self, cell_elements: ElementSet, wall_elements: ElementSet) -> None:
        self.cell_elements = cell_elements
        self.wall_elements = wall_elements

    @classmethod
    def from_mapping(cls, mapping: Dict[str, Any]) -> "EdgeGridConfig":
        if not isinstance(mapping, dict):
            raise TypeError("config must be a mapping")
        cell_items = mapping.get("cell_elements")
        wall_items = mapping.get("wall_elements")
        if cell_items is None:
            raise ValueError("config.cell_elements is required")
        if wall_items is None:
            raise ValueError("config.wall_elements is required")

        cell_elements = ElementSet.from_list(
            cell_items,
            CellElement,
            reserved_defaults={"open": 0},
        )
        wall_elements = ElementSet.from_list(
            wall_items,
            WallElement,
            reserved_defaults={"open": 0, "wall": 1},
        )
        return cls(cell_elements, wall_elements)

    def to_mapping(self) -> Dict[str, Any]:
        return {
            "cell_elements": self.cell_elements.to_list(),
            "wall_elements": self.wall_elements.to_list(),
        }


class EdgeGridLayout:
    def __init__(
        self,
        cells: List[List[int]],
        vertical_walls: List[List[int]],
        horizontal_walls: List[List[int]],
    ) -> None:
        self.cells = cells
        self.vertical_walls = vertical_walls
        self.horizontal_walls = horizontal_walls

    @classmethod
    def from_mapping(
        cls,
        mapping: Dict[str, Any],
        config: EdgeGridConfig,
    ) -> "EdgeGridLayout":
        if not isinstance(mapping, dict):
            raise TypeError("layout must be a mapping")
        cells_spec = mapping.get("cells")
        walls_spec = mapping.get("walls", {})
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

        _validate_wall_dimensions(cells, vertical, horizontal)
        return cls(cells, vertical, horizontal)

    def to_mapping(self, config: EdgeGridConfig, with_grid_numbers: bool) -> Dict[str, Any]:
        cells_lines = format_grid(self.cells, config.cell_elements, with_grid_numbers)
        vertical_lines = format_grid(self.vertical_walls, config.wall_elements, with_grid_numbers)
        horizontal_lines = format_grid(self.horizontal_walls, config.wall_elements, with_grid_numbers)
        return {
            "cells": "\n".join(cells_lines),
            "walls": {
                "vertical": "\n".join(vertical_lines),
                "horizontal": "\n".join(horizontal_lines),
            },
        }


def _validate_wall_dimensions(
    cells: List[List[int]],
    vertical: List[List[int]],
    horizontal: List[List[int]],
) -> None:
    height = len(cells)
    width = len(cells[0]) if cells else 0
    if height == 0 or width == 0:
        raise ValueError("cells must be non-empty")
    if len(vertical) != height:
        raise ValueError("vertical walls must have same number of rows as cells")
    if any(len(row) != width + 1 for row in vertical):
        raise ValueError("vertical walls must have width + 1 columns")
    if len(horizontal) != height + 1:
        raise ValueError("horizontal walls must have height + 1 rows")
    if any(len(row) != width for row in horizontal):
        raise ValueError("horizontal walls must have same number of columns as cells")
