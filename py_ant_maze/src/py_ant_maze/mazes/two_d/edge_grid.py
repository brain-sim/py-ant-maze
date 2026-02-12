from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, TypeAlias, Union

from ...core.structures.element_set import ElementSet, FrozenElementSet
from ...core.structures.grid import freeze_grid, format_grid, parse_grid, thaw_grid
from ...core.handlers import MazeTypeHandler
from ...core.parsing.maze_parsing import (
    parse_cell_elements,
    parse_wall_elements,
    validate_edge_grid_dimensions,
)
from ...core.types import ConfigSpec, CellGrid, WallGrid, FrozenCellGrid, FrozenWallGrid, LayoutSpec


# Default physical dimensions (meters)
DEFAULT_CELL_SIZE = 1.0
DEFAULT_WALL_HEIGHT = 1.0
DEFAULT_WALL_THICKNESS = 0.05


@dataclass
class EdgeGridConfig:
    cell_elements: ElementSet
    wall_elements: ElementSet
    cell_size: float = DEFAULT_CELL_SIZE
    wall_height: float = DEFAULT_WALL_HEIGHT
    wall_thickness: float = DEFAULT_WALL_THICKNESS


@dataclass
class EdgeGridLayout:
    cells: CellGrid
    vertical_walls: WallGrid
    horizontal_walls: WallGrid


@dataclass(frozen=True)
class FrozenEdgeGridConfig:
    cell_elements: FrozenElementSet
    wall_elements: FrozenElementSet
    cell_size: float = DEFAULT_CELL_SIZE
    wall_height: float = DEFAULT_WALL_HEIGHT
    wall_thickness: float = DEFAULT_WALL_THICKNESS


@dataclass(frozen=True)
class FrozenEdgeGridLayout:
    cells: FrozenCellGrid
    vertical_walls: FrozenWallGrid
    horizontal_walls: FrozenWallGrid


EdgeGridConfigLike: TypeAlias = Union[EdgeGridConfig, FrozenEdgeGridConfig]
EdgeGridLayoutLike: TypeAlias = Union[EdgeGridLayout, FrozenEdgeGridLayout]


def parse_edge_grid_layout(
    spec: LayoutSpec,
    config: EdgeGridConfig,
    *,
    context: str = "layout",
) -> EdgeGridLayout:
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
    return EdgeGridLayout(cells=cells, vertical_walls=vertical, horizontal_walls=horizontal)


def edge_grid_layout_to_spec(
    layout: EdgeGridLayoutLike,
    config: EdgeGridConfigLike,
    with_grid_numbers: bool,
) -> LayoutSpec:
    cells_lines = format_grid(layout.cells, config.cell_elements, with_grid_numbers)
    vertical_lines = format_grid(layout.vertical_walls, config.wall_elements, with_grid_numbers)
    horizontal_lines = format_grid(layout.horizontal_walls, config.wall_elements, with_grid_numbers)
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


def freeze_edge_grid_config(config: EdgeGridConfig) -> FrozenEdgeGridConfig:
    return FrozenEdgeGridConfig(
        cell_elements=config.cell_elements.freeze(),
        wall_elements=config.wall_elements.freeze(),
        cell_size=config.cell_size,
        wall_height=config.wall_height,
        wall_thickness=config.wall_thickness,
    )


def freeze_edge_grid_layout(layout: EdgeGridLayout) -> FrozenEdgeGridLayout:
    return FrozenEdgeGridLayout(
        cells=freeze_grid(layout.cells),
        vertical_walls=freeze_grid(layout.vertical_walls),
        horizontal_walls=freeze_grid(layout.horizontal_walls),
    )


def thaw_edge_grid_config(config: EdgeGridConfigLike) -> EdgeGridConfig:
    if isinstance(config, EdgeGridConfig):
        return config
    return EdgeGridConfig(
        cell_elements=config.cell_elements.thaw(),
        wall_elements=config.wall_elements.thaw(),
        cell_size=config.cell_size,
        wall_height=config.wall_height,
        wall_thickness=config.wall_thickness,
    )


def thaw_edge_grid_layout(layout: EdgeGridLayoutLike) -> EdgeGridLayout:
    if isinstance(layout, EdgeGridLayout):
        return layout
    return EdgeGridLayout(
        cells=thaw_grid(layout.cells),
        vertical_walls=thaw_grid(layout.vertical_walls),
        horizontal_walls=thaw_grid(layout.horizontal_walls),
    )


class EdgeGridHandler(MazeTypeHandler):
    maze_type = "edge_grid"
    aliases = ("edge_grid_2d",)

    def parse_config(self, spec: ConfigSpec) -> EdgeGridConfig:
        cell_elements = parse_cell_elements(spec, allow_elements_alias=True, reserved_defaults={"open": 0})
        wall_elements = parse_wall_elements(spec, reserved_defaults={"open": 0, "wall": 1})
        cell_size = spec.get("cell_size", DEFAULT_CELL_SIZE)
        wall_height = spec.get("wall_height", DEFAULT_WALL_HEIGHT)
        wall_thickness = spec.get("wall_thickness", DEFAULT_WALL_THICKNESS)
        return EdgeGridConfig(
            cell_elements=cell_elements,
            wall_elements=wall_elements,
            cell_size=cell_size,
            wall_height=wall_height,
            wall_thickness=wall_thickness,
        )

    def parse_layout(self, spec: LayoutSpec, config: EdgeGridConfig) -> EdgeGridLayout:
        return parse_edge_grid_layout(spec, config)

    def config_to_spec(self, config: EdgeGridConfigLike) -> ConfigSpec:
        result: ConfigSpec = {
            "cell_elements": config.cell_elements.to_list(),
            "wall_elements": config.wall_elements.to_list(),
        }
        if config.cell_size != DEFAULT_CELL_SIZE:
            result["cell_size"] = config.cell_size
        if config.wall_height != DEFAULT_WALL_HEIGHT:
            result["wall_height"] = config.wall_height
        if config.wall_thickness != DEFAULT_WALL_THICKNESS:
            result["wall_thickness"] = config.wall_thickness
        return result

    def layout_to_spec(
        self,
        layout: EdgeGridLayoutLike,
        config: EdgeGridConfigLike,
        with_grid_numbers: bool,
    ) -> LayoutSpec:
        return edge_grid_layout_to_spec(layout, config, with_grid_numbers)

    def freeze(self, config: EdgeGridConfig, layout: EdgeGridLayout) -> Tuple[object, object]:
        return (
            freeze_edge_grid_config(config),
            freeze_edge_grid_layout(layout),
        )

    def thaw(self, config: EdgeGridConfigLike, layout: EdgeGridLayoutLike) -> Tuple[object, object]:
        return (
            thaw_edge_grid_config(config),
            thaw_edge_grid_layout(layout),
        )


HANDLER = EdgeGridHandler()
