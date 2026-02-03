from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple, TypeAlias, Union

from ...core.structures.element_set import ElementSet, FrozenElementSet
from ...core.handlers import MazeTypeHandler
from ...core.parsing.maze_parsing import parse_cell_elements, parse_wall_elements
from ...core.types import ConfigSpec, LayoutSpec, Spec
from .edge_grid import (
    EdgeGridConfig,
    EdgeGridLayout,
    FrozenEdgeGridLayout,
    edge_grid_layout_to_spec,
    freeze_edge_grid_layout,
    parse_edge_grid_layout,
    thaw_edge_grid_layout,
)


ArmSpec: TypeAlias = Spec
ArmSpecList: TypeAlias = List[ArmSpec]
ArmLayouts: TypeAlias = List[EdgeGridLayout]
FrozenArmLayouts: TypeAlias = Tuple[FrozenEdgeGridLayout, ...]
ArmWidths: TypeAlias = List[int]
HubSpec: TypeAlias = Spec


@dataclass
class RadialArmConfig:
    cell_elements: ElementSet
    wall_elements: ElementSet


@dataclass
class RadialArmHub:
    shape: str
    angle_degrees: float
    radius: Optional[float] = None
    side_length: Optional[float] = None


@dataclass
class RadialArmLayout:
    hub: RadialArmHub
    arms: ArmLayouts


@dataclass(frozen=True)
class FrozenRadialArmConfig:
    cell_elements: FrozenElementSet
    wall_elements: FrozenElementSet


@dataclass(frozen=True)
class FrozenRadialArmHub:
    shape: str
    angle_degrees: float
    radius: Optional[float] = None
    side_length: Optional[float] = None


@dataclass(frozen=True)
class FrozenRadialArmLayout:
    hub: FrozenRadialArmHub
    arms: FrozenArmLayouts


RadialArmConfigLike: TypeAlias = Union[RadialArmConfig, FrozenRadialArmConfig]
RadialArmLayoutLike: TypeAlias = Union[RadialArmLayout, FrozenRadialArmLayout]


def parse_radial_arm_layout(spec: LayoutSpec, config: RadialArmConfig) -> RadialArmLayout:
    if not isinstance(spec, dict):
        raise TypeError("layout must be a mapping")
    hub_spec = spec.get("center_hub")
    arms_spec = spec.get("arms")
    if hub_spec is None:
        raise ValueError("layout.center_hub is required")
    if arms_spec is None:
        raise ValueError("layout.arms is required")
    if not isinstance(hub_spec, dict):
        raise TypeError("layout.center_hub must be a mapping")
    if not isinstance(arms_spec, list) or not arms_spec:
        raise TypeError("layout.arms must be a non-empty list")

    arms = _parse_arms(arms_spec, config)
    hub = _parse_hub_spec(hub_spec, arms)
    return RadialArmLayout(hub=hub, arms=arms)


def radial_arm_layout_to_spec(
    layout: RadialArmLayoutLike,
    config: RadialArmConfigLike,
    with_grid_numbers: bool,
) -> LayoutSpec:
    hub_mapping: Spec = {
        "shape": layout.hub.shape,
        "angle_degrees": layout.hub.angle_degrees,
    }
    if layout.hub.shape == "circular":
        hub_mapping["radius"] = layout.hub.radius
    elif layout.hub.shape == "polygon":
        hub_mapping["side_length"] = layout.hub.side_length

    edge_config = EdgeGridConfig(config.cell_elements, config.wall_elements)
    arms_mapping = [
        {"layout": edge_grid_layout_to_spec(arm, edge_config, with_grid_numbers)}
        for arm in layout.arms
    ]
    return {"center_hub": hub_mapping, "arms": arms_mapping}


def freeze_radial_arm_config(config: RadialArmConfig) -> FrozenRadialArmConfig:
    return FrozenRadialArmConfig(
        cell_elements=config.cell_elements.freeze(),
        wall_elements=config.wall_elements.freeze(),
    )


def freeze_radial_arm_layout(layout: RadialArmLayout) -> FrozenRadialArmLayout:
    return FrozenRadialArmLayout(
        hub=FrozenRadialArmHub(
            shape=layout.hub.shape,
            angle_degrees=layout.hub.angle_degrees,
            radius=layout.hub.radius,
            side_length=layout.hub.side_length,
        ),
        arms=tuple(freeze_edge_grid_layout(arm) for arm in layout.arms),
    )


def thaw_radial_arm_config(config: RadialArmConfigLike) -> RadialArmConfig:
    if isinstance(config, RadialArmConfig):
        return config
    return RadialArmConfig(
        cell_elements=config.cell_elements.thaw(),
        wall_elements=config.wall_elements.thaw(),
    )


def thaw_radial_arm_layout(layout: RadialArmLayoutLike) -> RadialArmLayout:
    if isinstance(layout, RadialArmLayout):
        return layout
    return RadialArmLayout(
        hub=RadialArmHub(
            shape=layout.hub.shape,
            angle_degrees=layout.hub.angle_degrees,
            radius=layout.hub.radius,
            side_length=layout.hub.side_length,
        ),
        arms=[thaw_edge_grid_layout(arm) for arm in layout.arms],
    )


class RadialArmHandler(MazeTypeHandler):
    maze_type = "radial_arm"
    aliases = ("radial_arm_2d",)

    def parse_config(self, spec: ConfigSpec) -> RadialArmConfig:
        cell_elements = parse_cell_elements(spec, allow_elements_alias=True, reserved_defaults={"open": 0})
        wall_elements = parse_wall_elements(spec, reserved_defaults={"open": 0, "wall": 1})
        return RadialArmConfig(cell_elements=cell_elements, wall_elements=wall_elements)

    def parse_layout(self, spec: LayoutSpec, config: RadialArmConfig) -> RadialArmLayout:
        return parse_radial_arm_layout(spec, config)

    def config_to_spec(self, config: RadialArmConfigLike) -> ConfigSpec:
        return {
            "cell_elements": config.cell_elements.to_list(),
            "wall_elements": config.wall_elements.to_list(),
        }

    def layout_to_spec(
        self,
        layout: RadialArmLayoutLike,
        config: RadialArmConfigLike,
        with_grid_numbers: bool,
    ) -> LayoutSpec:
        return radial_arm_layout_to_spec(layout, config, with_grid_numbers)

    def freeze(self, config: RadialArmConfig, layout: RadialArmLayout) -> Tuple[Any, Any]:
        return (
            freeze_radial_arm_config(config),
            freeze_radial_arm_layout(layout),
        )

    def thaw(self, config: RadialArmConfigLike, layout: RadialArmLayoutLike) -> Tuple[Any, Any]:
        return (
            thaw_radial_arm_config(config),
            thaw_radial_arm_layout(layout),
        )


def _parse_hub_spec(hub_spec: HubSpec, arms: ArmLayouts) -> RadialArmHub:
    shape = hub_spec.get("shape")
    if shape not in {"circular", "polygon"}:
        raise ValueError("layout.center_hub.shape must be 'circular' or 'polygon'")
    if "arm_width" in hub_spec:
        raise ValueError("layout.center_hub.arm_width is derived from arm layouts")
    angle_degrees = _parse_angle_degrees(hub_spec.get("angle_degrees", 360.0))
    arm_count = len(arms)
    if arm_count == 0:
        raise ValueError("layout.arms must have at least one arm")
    arm_widths: ArmWidths = [len(arm.cells) for arm in arms]

    if shape == "circular":
        radius = hub_spec.get("radius")
        min_radius = _min_circular_radius(arm_widths, angle_degrees)
        if radius is None:
            radius = min_radius
        else:
            radius = _parse_positive_number(radius, "layout.center_hub.radius")
            if radius < min_radius:
                raise ValueError(f"layout.center_hub.radius must be >= {min_radius:.6g}")
        return RadialArmHub(
            shape="circular",
            angle_degrees=angle_degrees,
            radius=radius,
        )

    if "sides" in hub_spec:
        raise ValueError("layout.center_hub.sides is derived from number of arms")

    side_length = hub_spec.get("side_length")
    min_side = max(arm_widths)
    if side_length is None:
        side_length = min_side
    else:
        side_length = _parse_positive_number(side_length, "layout.center_hub.side_length")
        if side_length < min_side:
            raise ValueError(f"layout.center_hub.side_length must be >= {min_side:.6g}")
    return RadialArmHub(
        shape="polygon",
        angle_degrees=angle_degrees,
        side_length=side_length,
    )


def _parse_arms(arms_spec: ArmSpecList, config: RadialArmConfig) -> ArmLayouts:
    edge_config = EdgeGridConfig(config.cell_elements, config.wall_elements)
    arms: ArmLayouts = []
    for index, arm_spec in enumerate(arms_spec):
        if not isinstance(arm_spec, dict):
            raise TypeError(f"layout.arms[{index}] must be a mapping")
        if "config" in arm_spec:
            raise ValueError(f"layout.arms[{index}].config is not allowed; use top-level config")
        layout_spec = arm_spec.get("layout")
        if layout_spec is None:
            raise ValueError(f"layout.arms[{index}].layout is required")
        if not isinstance(layout_spec, dict):
            raise TypeError(f"layout.arms[{index}].layout must be a mapping")
        arms.append(
            parse_edge_grid_layout(
                layout_spec,
                edge_config,
                context=f"layout.arms[{index}].layout",
            )
        )
    return arms


def _parse_positive_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field} must be a number")
    if value <= 0:
        raise ValueError(f"{field} must be > 0")
    return float(value)


def _parse_angle_degrees(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("layout.center_hub.angle_degrees must be a number")
    if value <= 0 or value > 360:
        raise ValueError("layout.center_hub.angle_degrees must be in (0, 360]")
    return float(value)


def _min_circular_radius(arm_widths: ArmWidths, angle_degrees: float) -> float:
    """Calculate minimum hub radius for circular hub.
    
    Uses max arm width × arm count (not sum of widths) to ensure the hub
    can properly connect to the widest arm, assuming all arms have that width.
    """
    angle_radians = math.radians(angle_degrees)
    max_width = max(arm_widths)
    arm_count = len(arm_widths)
    total_width = max_width * arm_count
    return total_width / angle_radians


HANDLER = RadialArmHandler()
