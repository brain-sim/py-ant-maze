from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Tuple, TypeAlias, Union

from ...core.structures.element_set import ElementSet, FrozenElementSet
from ...core.structures.grid import freeze_grid, format_grid, parse_grid, thaw_grid
from ...core.handlers import MazeTypeHandler
from ...core.parsing.maze_parsing import parse_cell_elements
from ...core.types import CellGrid, ConfigSpec, FrozenCellGrid, LayoutSpec


# Default physical dimensions (meters)
DEFAULT_CELL_SIZE = 1.0
DEFAULT_WALL_HEIGHT = 0.5


@dataclass
class OccupancyGridConfig:
    cell_elements: ElementSet
    cell_size: float = DEFAULT_CELL_SIZE
    wall_height: float = DEFAULT_WALL_HEIGHT


@dataclass
class OccupancyGridLayout:
    grid: CellGrid


@dataclass(frozen=True)
class FrozenOccupancyGridConfig:
    cell_elements: FrozenElementSet
    cell_size: float = DEFAULT_CELL_SIZE
    wall_height: float = DEFAULT_WALL_HEIGHT


@dataclass(frozen=True)
class FrozenOccupancyGridLayout:
    grid: FrozenCellGrid


OccupancyGridConfigLike: TypeAlias = Union[OccupancyGridConfig, FrozenOccupancyGridConfig]
OccupancyGridLayoutLike: TypeAlias = Union[OccupancyGridLayout, FrozenOccupancyGridLayout]


def parse_occupancy_grid_layout(spec: Any, config: OccupancyGridConfig) -> OccupancyGridLayout:
    layout_spec = spec
    if isinstance(spec, dict):
        if "grid" in spec:
            layout_spec = spec["grid"]
        elif "cells" in spec:
            layout_spec = spec["cells"]
    grid = parse_grid(layout_spec, config.cell_elements)
    return OccupancyGridLayout(grid=grid)


def occupancy_grid_layout_to_spec(
    layout: OccupancyGridLayoutLike,
    config: OccupancyGridConfigLike,
    with_grid_numbers: bool,
) -> LayoutSpec:
    lines = format_grid(layout.grid, config.cell_elements, with_grid_numbers)
    text = "\n".join(lines)
    return {"grid": text + "\n" if text else text}


def freeze_occupancy_grid_config(config: OccupancyGridConfig) -> FrozenOccupancyGridConfig:
    return FrozenOccupancyGridConfig(
        cell_elements=config.cell_elements.freeze(),
        cell_size=config.cell_size,
        wall_height=config.wall_height,
    )


def freeze_occupancy_grid_layout(layout: OccupancyGridLayout) -> FrozenOccupancyGridLayout:
    return FrozenOccupancyGridLayout(grid=freeze_grid(layout.grid))


def thaw_occupancy_grid_config(config: OccupancyGridConfigLike) -> OccupancyGridConfig:
    if isinstance(config, OccupancyGridConfig):
        return config
    return OccupancyGridConfig(
        cell_elements=config.cell_elements.thaw(),
        cell_size=config.cell_size,
        wall_height=config.wall_height,
    )


def thaw_occupancy_grid_layout(layout: OccupancyGridLayoutLike) -> OccupancyGridLayout:
    if isinstance(layout, OccupancyGridLayout):
        return layout
    return OccupancyGridLayout(grid=thaw_grid(layout.grid))


class OccupancyGridHandler(MazeTypeHandler):
    maze_type = "occupancy_grid"
    aliases = ("occupancy_grid_2d",)

    def parse_config(self, spec: ConfigSpec) -> OccupancyGridConfig:
        element_set = parse_cell_elements(
            spec,
            allow_elements_alias=True,
            reserved_defaults={"open": 0, "wall": 1},
        )
        cell_size = spec.get("cell_size", DEFAULT_CELL_SIZE)
        wall_height = spec.get("wall_height", DEFAULT_WALL_HEIGHT)
        return OccupancyGridConfig(
            cell_elements=element_set,
            cell_size=cell_size,
            wall_height=wall_height,
        )

    def parse_layout(
        self,
        spec: LayoutSpec,
        config: OccupancyGridConfig,
    ) -> OccupancyGridLayout:
        return parse_occupancy_grid_layout(spec, config)

    def config_to_spec(self, config: OccupancyGridConfigLike) -> ConfigSpec:
        result: ConfigSpec = {"cell_elements": config.cell_elements.to_list()}
        if config.cell_size != DEFAULT_CELL_SIZE:
            result["cell_size"] = config.cell_size
        if config.wall_height != DEFAULT_WALL_HEIGHT:
            result["wall_height"] = config.wall_height
        return result

    def layout_to_spec(
        self,
        layout: OccupancyGridLayoutLike,
        config: OccupancyGridConfigLike,
        with_grid_numbers: bool,
    ) -> LayoutSpec:
        return occupancy_grid_layout_to_spec(layout, config, with_grid_numbers)

    def freeze(self, config: OccupancyGridConfig, layout: OccupancyGridLayout) -> Tuple[Any, Any]:
        return (
            freeze_occupancy_grid_config(config),
            freeze_occupancy_grid_layout(layout),
        )

    def thaw(self, config: OccupancyGridConfigLike, layout: OccupancyGridLayoutLike) -> Tuple[Any, Any]:
        return (
            thaw_occupancy_grid_config(config),
            thaw_occupancy_grid_layout(layout),
        )


HANDLER = OccupancyGridHandler()
