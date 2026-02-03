from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias, Union

from ...core.structures.element_set import ElementSet, FrozenElementSet
from ...core.parsing.maze_parsing import parse_cell_elements, parse_wall_elements
from ...core.types import ConfigSpec, Grid, LayoutInput, LayoutSpec
from ..two_d.radial_arm import (
    RadialArmConfig,
    RadialArmLayout,
    FrozenRadialArmLayout,
    parse_radial_arm_layout,
    radial_arm_layout_to_spec,
    freeze_radial_arm_layout,
    thaw_radial_arm_layout,
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
class RadialArm3DConfig:
    cell_elements: ElementSet
    wall_elements: ElementSet


@dataclass(frozen=True)
class FrozenRadialArm3DConfig:
    cell_elements: FrozenElementSet
    wall_elements: FrozenElementSet


RadialArm3DLayout: TypeAlias = MultiLevelLayout[RadialArmLayout]
FrozenRadialArm3DLayout: TypeAlias = FrozenMultiLevelLayout[FrozenRadialArmLayout]
RadialArm3DLevelLayout: TypeAlias = LevelLayout[RadialArmLayout]
FrozenRadialArm3DLevelLayout: TypeAlias = FrozenLevelLayout[FrozenRadialArmLayout]

RadialArm3DConfigLike: TypeAlias = Union[RadialArm3DConfig, FrozenRadialArm3DConfig]
RadialArm3DLayoutLike: TypeAlias = Union[RadialArm3DLayout, FrozenRadialArm3DLayout]


def freeze_radial_arm_3d_config(config: RadialArm3DConfig) -> FrozenRadialArm3DConfig:
    return FrozenRadialArm3DConfig(
        cell_elements=config.cell_elements.freeze(),
        wall_elements=config.wall_elements.freeze(),
    )


def thaw_radial_arm_3d_config(config: RadialArm3DConfigLike) -> RadialArm3DConfig:
    if isinstance(config, RadialArm3DConfig):
        return config
    return RadialArm3DConfig(
        cell_elements=config.cell_elements.thaw(),
        wall_elements=config.wall_elements.thaw(),
    )


class RadialArm3DHandler(MultiLevelHandler):
    maze_type = "radial_arm_3d"
    connector_allow_arm = True
    connector_require_arm = True

    def parse_config(self, spec: ConfigSpec) -> RadialArm3DConfig:
        cell_elements = parse_cell_elements(
            spec,
            allow_elements_alias=True,
            reserved_defaults={"open": 0, "wall": 1, "elevator": 2, "escalator": 3},
        )
        wall_elements = parse_wall_elements(spec, reserved_defaults={"open": 0, "wall": 1})
        ensure_required_elements(cell_elements, context="config.cell_elements")
        return RadialArm3DConfig(cell_elements=cell_elements, wall_elements=wall_elements)

    def config_to_spec(self, config: RadialArm3DConfigLike) -> ConfigSpec:
        return {
            "cell_elements": config.cell_elements.to_list(),
            "wall_elements": config.wall_elements.to_list(),
        }

    def parse_level_layout(self, spec: LayoutInput, config: RadialArm3DConfig) -> RadialArmLayout:
        level_config = RadialArmConfig(config.cell_elements, config.wall_elements)
        return parse_radial_arm_layout(spec, level_config)

    def level_layout_to_spec(
        self,
        layout: Union[RadialArmLayout, FrozenRadialArmLayout],
        config: RadialArm3DConfigLike,
        with_grid_numbers: bool,
    ) -> LayoutSpec:
        level_config = RadialArmConfig(config.cell_elements, config.wall_elements)
        return radial_arm_layout_to_spec(layout, level_config, with_grid_numbers)

    def freeze_level_layout(self, layout: RadialArmLayout) -> FrozenRadialArmLayout:
        return freeze_radial_arm_layout(layout)

    def thaw_level_layout(self, layout: Union[FrozenRadialArmLayout, RadialArmLayout]) -> RadialArmLayout:
        return thaw_radial_arm_layout(layout)

    def freeze_config(self, config: RadialArm3DConfig) -> FrozenRadialArm3DConfig:
        return freeze_radial_arm_3d_config(config)

    def thaw_config(self, config: RadialArm3DConfigLike) -> RadialArm3DConfig:
        return thaw_radial_arm_3d_config(config)

    def cell_grid_for_location(
        self,
        level_layout: RadialArmLayout,
        location,
        *,
        context: str,
    ) -> Grid:
        if location.arm is None:
            raise ValueError(f"{context}.arm is required")
        if location.arm >= len(level_layout.arms):
            raise ValueError(f"{context}.arm is out of range")
        return level_layout.arms[location.arm].cells


HANDLER = RadialArm3DHandler()
