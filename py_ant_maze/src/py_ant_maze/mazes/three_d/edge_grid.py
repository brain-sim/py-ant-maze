from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias, Union

from ...core.structures.element_set import ElementSet, FrozenElementSet
from ...core.parsing.maze_parsing import parse_cell_elements, parse_wall_elements
from ...core.types import ConfigSpec, Grid, LayoutInput, LayoutSpec
from ..two_d.edge_grid import (
    EdgeGridConfig,
    EdgeGridLayout,
    FrozenEdgeGridLayout,
    edge_grid_layout_to_spec,
    parse_edge_grid_layout,
    freeze_edge_grid_layout,
    thaw_edge_grid_layout,
)
from .base import (
    FrozenLevelLayout,
    FrozenMultiLevelLayout,
    LevelLayout,
    MultiLevelHandler,
    MultiLevelLayout,
)
from .common import ensure_required_elements


@dataclass
class EdgeGrid3DConfig:
    cell_elements: ElementSet
    wall_elements: ElementSet


@dataclass(frozen=True)
class FrozenEdgeGrid3DConfig:
    cell_elements: FrozenElementSet
    wall_elements: FrozenElementSet


EdgeGrid3DLayout: TypeAlias = MultiLevelLayout[EdgeGridLayout]
FrozenEdgeGrid3DLayout: TypeAlias = FrozenMultiLevelLayout[FrozenEdgeGridLayout]
EdgeGrid3DLevelLayout: TypeAlias = LevelLayout[EdgeGridLayout]
FrozenEdgeGrid3DLevelLayout: TypeAlias = FrozenLevelLayout[FrozenEdgeGridLayout]

EdgeGrid3DConfigLike: TypeAlias = Union[EdgeGrid3DConfig, FrozenEdgeGrid3DConfig]
EdgeGrid3DLayoutLike: TypeAlias = Union[EdgeGrid3DLayout, FrozenEdgeGrid3DLayout]


def freeze_edge_grid_3d_config(config: EdgeGrid3DConfig) -> FrozenEdgeGrid3DConfig:
    return FrozenEdgeGrid3DConfig(
        cell_elements=config.cell_elements.freeze(),
        wall_elements=config.wall_elements.freeze(),
    )


def thaw_edge_grid_3d_config(config: EdgeGrid3DConfigLike) -> EdgeGrid3DConfig:
    if isinstance(config, EdgeGrid3DConfig):
        return config
    return EdgeGrid3DConfig(
        cell_elements=config.cell_elements.thaw(),
        wall_elements=config.wall_elements.thaw(),
    )


class EdgeGrid3DHandler(MultiLevelHandler):
    maze_type = "edge_grid_3d"

    def parse_config(self, spec: ConfigSpec) -> EdgeGrid3DConfig:
        cell_elements = parse_cell_elements(
            spec,
            allow_elements_alias=True,
            reserved_defaults={"open": 0, "wall": 1, "elevator": 2, "escalator": 3},
        )
        wall_elements = parse_wall_elements(spec, reserved_defaults={"open": 0, "wall": 1})
        ensure_required_elements(cell_elements, context="config.cell_elements")
        return EdgeGrid3DConfig(cell_elements=cell_elements, wall_elements=wall_elements)

    def config_to_spec(self, config: EdgeGrid3DConfigLike) -> ConfigSpec:
        return {
            "cell_elements": config.cell_elements.to_list(),
            "wall_elements": config.wall_elements.to_list(),
        }

    def parse_level_layout(self, spec: LayoutInput, config: EdgeGrid3DConfig) -> EdgeGridLayout:
        level_config = EdgeGridConfig(config.cell_elements, config.wall_elements)
        return parse_edge_grid_layout(spec, level_config)

    def level_layout_to_spec(
        self,
        layout: Union[EdgeGridLayout, FrozenEdgeGridLayout],
        config: EdgeGrid3DConfigLike,
        with_grid_numbers: bool,
    ) -> LayoutSpec:
        level_config = EdgeGridConfig(config.cell_elements, config.wall_elements)
        return edge_grid_layout_to_spec(layout, level_config, with_grid_numbers)

    def freeze_level_layout(self, layout: EdgeGridLayout) -> FrozenEdgeGridLayout:
        return freeze_edge_grid_layout(layout)

    def thaw_level_layout(self, layout: Union[FrozenEdgeGridLayout, EdgeGridLayout]) -> EdgeGridLayout:
        return thaw_edge_grid_layout(layout)

    def freeze_config(self, config: EdgeGrid3DConfig) -> FrozenEdgeGrid3DConfig:
        return freeze_edge_grid_3d_config(config)

    def thaw_config(self, config: EdgeGrid3DConfigLike) -> EdgeGrid3DConfig:
        return thaw_edge_grid_3d_config(config)

    def cell_grid_for_location(
        self,
        level_layout: EdgeGridLayout,
        location,
        *,
        context: str,
    ) -> Grid:
        return level_layout.cells


HANDLER = EdgeGrid3DHandler()
