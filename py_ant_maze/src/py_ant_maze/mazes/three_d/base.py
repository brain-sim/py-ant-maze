from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, List, Tuple, TypeVar

from ...core.parsing.level_connectors import (
    LevelConnector,
    LevelConnectorLocation,
    level_connectors_to_spec,
    parse_level_connectors,
)
from ...core.handlers import MazeTypeHandler
from ...core.parsing.multi_level import LevelDefinition, parse_level_layouts
from ...core.types import Grid, LayoutInput, LayoutSpec
from .common import element_value, validate_connector_rules

LayoutT = TypeVar("LayoutT")
FrozenLayoutT = TypeVar("FrozenLayoutT")


@dataclass
class LevelLayout(Generic[LayoutT]):
    definition: LevelDefinition
    layout: LayoutT


@dataclass
class MultiLevelLayout(Generic[LayoutT]):
    levels: List[LevelLayout[LayoutT]]
    connectors: List[LevelConnector]


@dataclass(frozen=True)
class FrozenLevelLayout(Generic[FrozenLayoutT]):
    definition: LevelDefinition
    layout: FrozenLayoutT


@dataclass(frozen=True)
class FrozenMultiLevelLayout(Generic[FrozenLayoutT]):
    levels: Tuple[FrozenLevelLayout[FrozenLayoutT], ...]
    connectors: Tuple[LevelConnector, ...]


class MultiLevelHandler(MazeTypeHandler):
    connector_allow_arm: bool = False
    connector_require_arm: bool = False

    def parse_layout(self, spec: LayoutSpec, config: Any) -> MultiLevelLayout[Any]:
        if not isinstance(spec, dict):
            raise TypeError("layout must be a mapping")
        levels_spec = spec.get("levels")
        if levels_spec is None:
            raise ValueError("layout.levels is required")

        parsed_levels = parse_level_layouts(levels_spec, context="layout.levels")
        levels = [
            LevelLayout(
                definition=level.definition,
                layout=self.parse_level_layout(level.layout_spec, config),
            )
            for level in parsed_levels
        ]

        connectors = parse_level_connectors(
            spec.get("connectors"),
            levels=[level.definition for level in levels],
            context="layout.connectors",
            allow_arm=self.connector_allow_arm,
            require_arm=self.connector_require_arm,
        )
        self._validate_connectors(connectors, levels, config)
        return MultiLevelLayout(levels=levels, connectors=connectors)

    def layout_to_spec(
        self,
        layout: MultiLevelLayout[Any],
        config: Any,
        with_grid_numbers: bool,
    ) -> LayoutSpec:
        levels_spec = [
            {
                "id": level.definition.name,
                "layout": self.level_layout_to_spec(level.layout, config, with_grid_numbers),
            }
            for level in layout.levels
        ]
        mapping: LayoutSpec = {"levels": levels_spec}
        if layout.connectors:
            mapping["connectors"] = level_connectors_to_spec(layout.connectors)
        return mapping

    def freeze(self, config: Any, layout: MultiLevelLayout[Any]) -> Tuple[Any, Any]:
        frozen_levels = tuple(
            FrozenLevelLayout(
                definition=level.definition,
                layout=self.freeze_level_layout(level.layout),
            )
            for level in layout.levels
        )
        return (
            self.freeze_config(config),
            FrozenMultiLevelLayout(levels=frozen_levels, connectors=tuple(layout.connectors)),
        )

    def thaw(self, config: Any, layout: FrozenMultiLevelLayout[Any]) -> Tuple[Any, Any]:
        return (
            self.thaw_config(config),
            MultiLevelLayout(
                levels=[
                    LevelLayout(
                        definition=level.definition,
                        layout=self.thaw_level_layout(level.layout),
                    )
                    for level in layout.levels
                ],
                connectors=list(layout.connectors),
            ),
        )

    def _validate_connectors(
        self,
        connectors: List[LevelConnector],
        levels: List[LevelLayout[Any]],
        config: Any,
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
        levels: List[LevelLayout[Any]],
        location: LevelConnectorLocation,
        *,
        context: str,
    ) -> None:
        grid = self.cell_grid_for_location(levels[location.level.index].layout, location, context=context)
        height = len(grid)
        width = len(grid[0]) if grid else 0
        if location.row >= height:
            raise ValueError(f"{context}.row is out of range")
        if location.col >= width:
            raise ValueError(f"{context}.col is out of range")

    def _validate_cell_value(
        self,
        levels: List[LevelLayout[Any]],
        location: LevelConnectorLocation,
        expected: int,
        *,
        context: str,
    ) -> None:
        grid = self.cell_grid_for_location(levels[location.level.index].layout, location, context=context)
        if grid[location.row][location.col] != expected:
            raise ValueError(f"{context} must reference a matching connector cell")

    def parse_level_layout(self, spec: LayoutInput, config: Any) -> Any:
        raise NotImplementedError

    def level_layout_to_spec(self, layout: Any, config: Any, with_grid_numbers: bool) -> LayoutSpec:
        raise NotImplementedError

    def freeze_level_layout(self, layout: Any) -> Any:
        raise NotImplementedError

    def thaw_level_layout(self, layout: Any) -> Any:
        raise NotImplementedError

    def freeze_config(self, config: Any) -> Any:
        raise NotImplementedError

    def thaw_config(self, config: Any) -> Any:
        raise NotImplementedError

    def cell_grid_for_location(
        self,
        level_layout: Any,
        location: LevelConnectorLocation,
        *,
        context: str,
    ) -> Grid:
        raise NotImplementedError
