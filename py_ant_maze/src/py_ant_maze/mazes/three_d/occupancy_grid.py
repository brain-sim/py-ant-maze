from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias, Union

from ...core.structures.element_set import ElementSet, FrozenElementSet
from ...core.parsing.maze_parsing import parse_cell_elements, parse_wall_elements
from ...core.types import ConfigSpec, Grid, LayoutInput, LayoutSpec
from ..two_d.occupancy_grid import (
    OccupancyGridConfig,
    OccupancyGridLayout,
    FrozenOccupancyGridLayout,
    element_values,
    occupancy_grid_elements,
    resolve_default_values,
    occupancy_grid_layout_to_spec,
    parse_occupancy_grid_layout,
    freeze_occupancy_grid_layout,
    thaw_occupancy_grid_layout,
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
class OccupancyGrid3DConfig:
    cell_elements: ElementSet
    wall_elements: ElementSet


@dataclass(frozen=True)
class FrozenOccupancyGrid3DConfig:
    cell_elements: FrozenElementSet
    wall_elements: FrozenElementSet


OccupancyGrid3DLayout: TypeAlias = MultiLevelLayout[OccupancyGridLayout]
FrozenOccupancyGrid3DLayout: TypeAlias = FrozenMultiLevelLayout[FrozenOccupancyGridLayout]
OccupancyGrid3DLevelLayout: TypeAlias = LevelLayout[OccupancyGridLayout]
FrozenOccupancyGrid3DLevelLayout: TypeAlias = FrozenLevelLayout[FrozenOccupancyGridLayout]

OccupancyGrid3DConfigLike: TypeAlias = Union[OccupancyGrid3DConfig, FrozenOccupancyGrid3DConfig]
OccupancyGrid3DLayoutLike: TypeAlias = Union[OccupancyGrid3DLayout, FrozenOccupancyGrid3DLayout]


def freeze_occupancy_grid_3d_config(config: OccupancyGrid3DConfig) -> FrozenOccupancyGrid3DConfig:
    return FrozenOccupancyGrid3DConfig(
        cell_elements=config.cell_elements.freeze(),
        wall_elements=config.wall_elements.freeze(),
    )


def thaw_occupancy_grid_3d_config(config: OccupancyGrid3DConfigLike) -> OccupancyGrid3DConfig:
    if isinstance(config, OccupancyGrid3DConfig):
        return config
    return OccupancyGrid3DConfig(
        cell_elements=config.cell_elements.thaw(),
        wall_elements=config.wall_elements.thaw(),
    )


class OccupancyGrid3DHandler(MultiLevelHandler):
    maze_type = "occupancy_grid_3d"

    def parse_config(self, spec: ConfigSpec) -> OccupancyGrid3DConfig:
        wall_elements = parse_wall_elements(
            spec,
            reserved_defaults={"wall": 1},
        )
        blocked_values = element_values(wall_elements)
        cell_defaults = resolve_default_values(
            {"open": 0, "elevator": 2, "escalator": 3},
            blocked_values=blocked_values,
        )
        cell_elements = parse_cell_elements(
            spec,
            allow_elements_alias=True,
            reserved_defaults=cell_defaults,
            blocked_values=blocked_values,
        )
        ensure_required_elements(cell_elements, context="config.cell_elements")
        occupancy_grid_elements(cell_elements, wall_elements, context="config")
        return OccupancyGrid3DConfig(
            cell_elements=cell_elements,
            wall_elements=wall_elements,
        )

    def config_to_spec(self, config: OccupancyGrid3DConfigLike) -> ConfigSpec:
        return {
            "cell_elements": config.cell_elements.to_list(),
            "wall_elements": config.wall_elements.to_list(),
        }

    def parse_level_layout(self, spec: LayoutInput, config: OccupancyGrid3DConfig) -> OccupancyGridLayout:
        level_config = OccupancyGridConfig(
            cell_elements=config.cell_elements,
            wall_elements=config.wall_elements,
        )
        return parse_occupancy_grid_layout(spec, level_config)

    def level_layout_to_spec(
        self,
        layout: Union[OccupancyGridLayout, FrozenOccupancyGridLayout],
        config: OccupancyGrid3DConfigLike,
        with_grid_numbers: bool,
    ) -> LayoutSpec:
        level_config = OccupancyGridConfig(
            cell_elements=config.cell_elements,
            wall_elements=config.wall_elements,
        )
        return occupancy_grid_layout_to_spec(layout, level_config, with_grid_numbers)

    def freeze_level_layout(self, layout: OccupancyGridLayout) -> FrozenOccupancyGridLayout:
        return freeze_occupancy_grid_layout(layout)

    def thaw_level_layout(
        self, layout: Union[FrozenOccupancyGridLayout, OccupancyGridLayout]
    ) -> OccupancyGridLayout:
        return thaw_occupancy_grid_layout(layout)

    def freeze_config(self, config: OccupancyGrid3DConfig) -> FrozenOccupancyGrid3DConfig:
        return freeze_occupancy_grid_3d_config(config)

    def thaw_config(self, config: OccupancyGrid3DConfigLike) -> OccupancyGrid3DConfig:
        return thaw_occupancy_grid_3d_config(config)

    def cell_grid_for_location(
        self,
        level_layout: OccupancyGridLayout,
        location,
        *,
        context: str,
    ) -> Grid:
        return level_layout.grid


HANDLER = OccupancyGrid3DHandler()
