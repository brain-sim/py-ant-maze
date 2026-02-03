"""
radial_arm_3d maze type - 3D radial arm mazes with shared hub configuration.

Unlike other 3D maze types where each level has identical structure, radial_arm_3d
stores the hub and arm structure at the root layout level, with each level only
containing the cell/wall data for its arms. This ensures consistency across levels.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Tuple, TypeAlias, Union

from ...core.structures.element_set import ElementSet, FrozenElementSet
from ...core.handlers import MazeTypeHandler
from ...core.parsing.level_connectors import (
    LevelConnector,
    LevelConnectorLocation,
    level_connectors_to_spec,
    parse_level_connectors,
)
from ...core.parsing.maze_parsing import parse_cell_elements, parse_wall_elements
from ...core.parsing.multi_level import LevelDefinition, parse_level_layouts
from ...core.types import ConfigSpec, Grid, LayoutInput, LayoutSpec
from ..two_d.radial_arm import (
    RadialArmHub,
    FrozenRadialArmHub,
    _parse_hub_spec,
)
from ..two_d.edge_grid import (
    EdgeGridConfig,
    EdgeGridLayout,
    FrozenEdgeGridLayout,
    edge_grid_layout_to_spec,
    freeze_edge_grid_layout,
    parse_edge_grid_layout,
    thaw_edge_grid_layout,
)
from .common import ensure_required_elements, element_value, validate_connector_rules


# Type aliases for arm layouts
ArmLayouts: TypeAlias = List[EdgeGridLayout]
FrozenArmLayouts: TypeAlias = Tuple[FrozenEdgeGridLayout, ...]


@dataclass
class RadialArm3DConfig:
    cell_elements: ElementSet
    wall_elements: ElementSet


@dataclass(frozen=True)
class FrozenRadialArm3DConfig:
    cell_elements: FrozenElementSet
    wall_elements: FrozenElementSet


@dataclass
class RadialArm3DLevelLayout:
    """Per-level layout containing only arm data (no hub - hub is shared)."""
    definition: LevelDefinition
    arms: ArmLayouts


@dataclass(frozen=True)
class FrozenRadialArm3DLevelLayout:
    """Frozen per-level layout containing only arm data."""
    definition: LevelDefinition
    arms: FrozenArmLayouts


@dataclass
class RadialArm3DLayout:
    """
    3D radial arm layout with hub at root level.
    
    The hub and arm structure (count, dimensions) are shared across all levels.
    Each level contains its own cell/wall data for the arms.
    """
    hub: RadialArmHub
    levels: List[RadialArm3DLevelLayout]
    connectors: List[LevelConnector]


@dataclass(frozen=True)
class FrozenRadialArm3DLayout:
    """Frozen 3D radial arm layout."""
    hub: FrozenRadialArmHub
    levels: Tuple[FrozenRadialArm3DLevelLayout, ...]
    connectors: Tuple[LevelConnector, ...]


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


def freeze_radial_arm_3d_layout(layout: RadialArm3DLayout) -> FrozenRadialArm3DLayout:
    return FrozenRadialArm3DLayout(
        hub=FrozenRadialArmHub(
            shape=layout.hub.shape,
            angle_degrees=layout.hub.angle_degrees,
            radius=layout.hub.radius,
            side_length=layout.hub.side_length,
        ),
        levels=tuple(
            FrozenRadialArm3DLevelLayout(
                definition=level.definition,
                arms=tuple(freeze_edge_grid_layout(arm) for arm in level.arms),
            )
            for level in layout.levels
        ),
        connectors=tuple(layout.connectors),
    )


def thaw_radial_arm_3d_layout(layout: RadialArm3DLayoutLike) -> RadialArm3DLayout:
    if isinstance(layout, RadialArm3DLayout):
        return layout
    return RadialArm3DLayout(
        hub=RadialArmHub(
            shape=layout.hub.shape,
            angle_degrees=layout.hub.angle_degrees,
            radius=layout.hub.radius,
            side_length=layout.hub.side_length,
        ),
        levels=[
            RadialArm3DLevelLayout(
                definition=level.definition,
                arms=[thaw_edge_grid_layout(arm) for arm in level.arms],
            )
            for level in layout.levels
        ],
        connectors=list(layout.connectors),
    )


class RadialArm3DHandler(MazeTypeHandler):
    """
    Handler for radial_arm_3d mazes.
    
    Unlike other 3D types, this doesn't extend MultiLevelHandler because
    the layout structure is different - hub is at root, not per-level.
    """
    maze_type = "radial_arm_3d"

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

    def parse_layout(self, spec: LayoutSpec, config: RadialArm3DConfig) -> RadialArm3DLayout:
        if not isinstance(spec, dict):
            raise TypeError("layout must be a mapping")
        
        # Parse hub from root level
        hub_spec = spec.get("center_hub")
        if hub_spec is None:
            raise ValueError("layout.center_hub is required")
        if not isinstance(hub_spec, dict):
            raise TypeError("layout.center_hub must be a mapping")
        
        # Parse levels
        levels_spec = spec.get("levels")
        if levels_spec is None:
            raise ValueError("layout.levels is required")
        
        parsed_levels = parse_level_layouts(levels_spec, context="layout.levels")
        edge_config = EdgeGridConfig(config.cell_elements, config.wall_elements)
        
        # Parse each level's arm layouts
        levels: List[RadialArm3DLevelLayout] = []
        expected_arm_count = None
        
        for level in parsed_levels:
            level_layout_spec = level.layout_spec
            if not isinstance(level_layout_spec, dict):
                raise TypeError(f"layout.levels[{level.definition.index}].layout must be a mapping")
            
            arms_spec = level_layout_spec.get("arms")
            if arms_spec is None:
                raise ValueError(f"layout.levels[{level.definition.index}].layout.arms is required")
            if not isinstance(arms_spec, list) or not arms_spec:
                raise TypeError(f"layout.levels[{level.definition.index}].layout.arms must be a non-empty list")
            
            # Validate arm count consistency across levels
            if expected_arm_count is None:
                expected_arm_count = len(arms_spec)
            elif len(arms_spec) != expected_arm_count:
                raise ValueError(
                    f"layout.levels[{level.definition.index}].layout.arms has {len(arms_spec)} arms, "
                    f"expected {expected_arm_count} to match first level"
                )
            
            # Parse arm layouts
            arms = self._parse_level_arms(arms_spec, edge_config, level.definition.index)
            levels.append(RadialArm3DLevelLayout(definition=level.definition, arms=arms))
        
        # Parse hub with arm widths from first level
        first_level_arms = levels[0].arms
        hub = _parse_hub_spec(hub_spec, first_level_arms)
        
        # Parse connectors
        connectors = parse_level_connectors(
            spec.get("connectors"),
            levels=[level.definition for level in levels],
            context="layout.connectors",
            allow_arm=True,
            require_arm=True,
        )
        self._validate_connectors(connectors, levels, config)
        
        return RadialArm3DLayout(hub=hub, levels=levels, connectors=connectors)

    def _parse_level_arms(
        self,
        arms_spec: list,
        edge_config: EdgeGridConfig,
        level_index: int,
    ) -> ArmLayouts:
        """Parse arm layouts for a single level."""
        arms: ArmLayouts = []
        for arm_index, arm_spec in enumerate(arms_spec):
            context = f"layout.levels[{level_index}].layout.arms[{arm_index}]"
            if not isinstance(arm_spec, dict):
                raise TypeError(f"{context} must be a mapping")
            if "config" in arm_spec:
                raise ValueError(f"{context}.config is not allowed; use top-level config")
            layout_spec = arm_spec.get("layout")
            if layout_spec is None:
                raise ValueError(f"{context}.layout is required")
            if not isinstance(layout_spec, dict):
                raise TypeError(f"{context}.layout must be a mapping")
            arms.append(
                parse_edge_grid_layout(layout_spec, edge_config, context=f"{context}.layout")
            )
        return arms

    def layout_to_spec(
        self,
        layout: RadialArm3DLayoutLike,
        config: RadialArm3DConfigLike,
        with_grid_numbers: bool,
    ) -> LayoutSpec:
        # Hub spec
        hub_mapping = {
            "shape": layout.hub.shape,
            "angle_degrees": layout.hub.angle_degrees,
        }
        if layout.hub.shape == "circular":
            hub_mapping["radius"] = layout.hub.radius
        elif layout.hub.shape == "polygon":
            hub_mapping["side_length"] = layout.hub.side_length
        
        # Levels spec
        edge_config = EdgeGridConfig(config.cell_elements, config.wall_elements)
        levels_spec = []
        for level in layout.levels:
            arms_spec = [
                {"layout": edge_grid_layout_to_spec(arm, edge_config, with_grid_numbers)}
                for arm in level.arms
            ]
            levels_spec.append({
                "id": level.definition.name,
                "layout": {"arms": arms_spec},
            })
        
        result: LayoutSpec = {
            "center_hub": hub_mapping,
            "levels": levels_spec,
        }
        if layout.connectors:
            result["connectors"] = level_connectors_to_spec(layout.connectors)
        return result

    def freeze(
        self,
        config: RadialArm3DConfig,
        layout: RadialArm3DLayout,
    ) -> Tuple[FrozenRadialArm3DConfig, FrozenRadialArm3DLayout]:
        return (
            freeze_radial_arm_3d_config(config),
            freeze_radial_arm_3d_layout(layout),
        )

    def thaw(
        self,
        config: RadialArm3DConfigLike,
        layout: RadialArm3DLayoutLike,
    ) -> Tuple[RadialArm3DConfig, RadialArm3DLayout]:
        return (
            thaw_radial_arm_3d_config(config),
            thaw_radial_arm_3d_layout(layout),
        )

    def _validate_connectors(
        self,
        connectors: List[LevelConnector],
        levels: List[RadialArm3DLevelLayout],
        config: RadialArm3DConfig,
    ) -> None:
        if not connectors:
            return
        
        elevator_value = element_value(config.cell_elements, "elevator", context="config.cell_elements")
        escalator_value = element_value(config.cell_elements, "escalator", context="config.cell_elements")
        
        for index, connector in enumerate(connectors):
            context = f"layout.connectors[{index}]"
            validate_connector_rules(connector, context=context)
            self._validate_location(levels, connector.start, context=f"{context}.from")
            self._validate_location(levels, connector.end, context=f"{context}.to")
            expected = elevator_value if connector.kind == "elevator" else escalator_value
            self._validate_cell_value(levels, connector.start, expected, context=f"{context}.from")
            self._validate_cell_value(levels, connector.end, expected, context=f"{context}.to")

    def _validate_location(
        self,
        levels: List[RadialArm3DLevelLayout],
        location: LevelConnectorLocation,
        *,
        context: str,
    ) -> None:
        if location.arm is None:
            raise ValueError(f"{context}.arm is required")
        level = levels[location.level.index]
        if location.arm >= len(level.arms):
            raise ValueError(f"{context}.arm is out of range")
        grid = level.arms[location.arm].cells
        height = len(grid)
        width = len(grid[0]) if grid else 0
        if location.row >= height:
            raise ValueError(f"{context}.row is out of range")
        if location.col >= width:
            raise ValueError(f"{context}.col is out of range")

    def _validate_cell_value(
        self,
        levels: List[RadialArm3DLevelLayout],
        location: LevelConnectorLocation,
        expected: int,
        *,
        context: str,
    ) -> None:
        level = levels[location.level.index]
        grid = level.arms[location.arm].cells
        if grid[location.row][location.col] != expected:
            raise ValueError(f"{context} must reference a matching connector cell")


HANDLER = RadialArm3DHandler()
