from typing import Any

from ..core.base import ConfigBase, LayoutBase
from ..core.element_set import ElementSet
from ..core.grid import parse_grid, format_grid
from ..core.maze_parsing import parse_cell_elements
from ..core.types import ConfigSpec, Grid, LayoutSpec


class OccupancyGridConfig(ConfigBase):
    def __init__(self, cell_elements: ElementSet) -> None:
        self.cell_elements = cell_elements

    @classmethod
    def from_spec(cls, spec: ConfigSpec) -> "OccupancyGridConfig":
        element_set = parse_cell_elements(
            spec,
            allow_elements_alias=True,
            reserved_defaults={"open": 0, "wall": 1},
        )
        return cls(element_set)

    def to_spec(self) -> ConfigSpec:
        return {"cell_elements": self.cell_elements.to_list()}


class OccupancyGridLayout(LayoutBase):
    def __init__(self, grid: Grid) -> None:
        self.grid = grid

    @classmethod
    def from_spec(
        cls,
        spec: Any,
        config: OccupancyGridConfig,
    ) -> "OccupancyGridLayout":
        layout_spec = spec
        if isinstance(spec, dict):
            if "grid" in spec:
                layout_spec = spec["grid"]
            elif "cells" in spec:
                layout_spec = spec["cells"]
        grid = parse_grid(layout_spec, config.cell_elements)
        return cls(grid)

    def to_spec(self, config: OccupancyGridConfig, with_grid_numbers: bool) -> LayoutSpec:
        lines = format_grid(self.grid, config.cell_elements, with_grid_numbers)
        text = "\n".join(lines)
        return {"grid": text + "\n" if text else text}
