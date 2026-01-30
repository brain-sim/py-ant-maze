from typing import Any, Dict, List

from ..element_set import ElementSet
from ..elements import CellElement
from ..grid import parse_grid, format_grid
from ..yaml_types import literal_block


class OccupancyGridConfig:
    def __init__(self, cell_elements: ElementSet) -> None:
        self.cell_elements = cell_elements

    @classmethod
    def from_mapping(cls, mapping: Dict[str, Any]) -> "OccupancyGridConfig":
        if not isinstance(mapping, dict):
            raise TypeError("config must be a mapping")
        elements = mapping.get("cell_elements")
        if elements is None:
            elements = mapping.get("elements")
        if elements is None:
            raise ValueError("config.cell_elements is required")
        element_set = ElementSet.from_list(
            elements,
            CellElement,
            reserved_defaults={"open": 0, "wall": 1},
        )
        return cls(element_set)

    def to_mapping(self) -> Dict[str, Any]:
        return {"cell_elements": self.cell_elements.to_list()}


class OccupancyGridLayout:
    def __init__(self, grid: List[List[int]]) -> None:
        self.grid = grid

    @classmethod
    def from_mapping(
        cls,
        mapping: Any,
        config: OccupancyGridConfig,
    ) -> "OccupancyGridLayout":
        layout_spec = mapping
        if isinstance(mapping, dict):
            if "grid" in mapping:
                layout_spec = mapping["grid"]
            elif "cells" in mapping:
                layout_spec = mapping["cells"]
        grid = parse_grid(layout_spec, config.cell_elements)
        return cls(grid)

    def to_mapping(self, config: OccupancyGridConfig, with_grid_numbers: bool) -> Dict[str, Any]:
        lines = format_grid(self.grid, config.cell_elements, with_grid_numbers)
        return {"grid": literal_block(lines)}
