from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Set, Tuple, TypeAlias, Union

from ...core.structures.element_set import ElementSet, FrozenElementSet
from ...core.structures.elements import MazeElement
from ...core.structures.grid import freeze_grid, format_grid, parse_grid, thaw_grid
from ...core.handlers import MazeTypeHandler
from ...core.parsing.maze_parsing import parse_cell_elements, parse_wall_elements
from ...core.types import CellGrid, ConfigSpec, FrozenCellGrid, LayoutSpec


# Default physical dimensions (meters)
DEFAULT_CELL_SIZE = 1.0
DEFAULT_WALL_HEIGHT = 1.0


@dataclass
class OccupancyGridConfig:
    cell_elements: ElementSet
    wall_elements: ElementSet
    cell_size: float = DEFAULT_CELL_SIZE
    wall_height: float = DEFAULT_WALL_HEIGHT


@dataclass
class OccupancyGridLayout:
    grid: CellGrid


@dataclass(frozen=True)
class FrozenOccupancyGridConfig:
    cell_elements: FrozenElementSet
    wall_elements: FrozenElementSet
    cell_size: float = DEFAULT_CELL_SIZE
    wall_height: float = DEFAULT_WALL_HEIGHT


@dataclass(frozen=True)
class FrozenOccupancyGridLayout:
    grid: FrozenCellGrid


OccupancyGridConfigLike: TypeAlias = Union[OccupancyGridConfig, FrozenOccupancyGridConfig]
OccupancyGridLayoutLike: TypeAlias = Union[OccupancyGridLayout, FrozenOccupancyGridLayout]
ElementSetLike: TypeAlias = Union[ElementSet, FrozenElementSet]


def parse_occupancy_grid_layout(spec: Any, config: OccupancyGridConfig) -> OccupancyGridLayout:
    layout_spec = spec
    if isinstance(spec, dict):
        if "grid" in spec:
            layout_spec = spec["grid"]
        elif "cells" in spec:
            layout_spec = spec["cells"]
    grid_elements = occupancy_grid_elements(
        config.cell_elements,
        config.wall_elements,
        context="config",
    )
    grid = parse_grid(layout_spec, grid_elements)
    return OccupancyGridLayout(grid=grid)


def occupancy_grid_layout_to_spec(
    layout: OccupancyGridLayoutLike,
    config: OccupancyGridConfigLike,
    with_grid_numbers: bool,
) -> LayoutSpec:
    grid_elements = occupancy_grid_elements(
        config.cell_elements,
        config.wall_elements,
        context="config",
    )
    lines = format_grid(layout.grid, grid_elements, with_grid_numbers)
    text = "\n".join(lines)
    return {"grid": text + "\n" if text else text}


def freeze_occupancy_grid_config(config: OccupancyGridConfig) -> FrozenOccupancyGridConfig:
    return FrozenOccupancyGridConfig(
        cell_elements=config.cell_elements.freeze(),
        wall_elements=config.wall_elements.freeze(),
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
        wall_elements=config.wall_elements.thaw(),
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
        wall_elements = parse_wall_elements(
            spec,
            reserved_defaults={"wall": 1},
        )
        blocked_values = element_values(wall_elements)
        cell_defaults = resolve_default_values(
            {"open": 0},
            blocked_values=blocked_values,
        )
        cell_elements = parse_cell_elements(
            spec,
            allow_elements_alias=True,
            reserved_defaults=cell_defaults,
            blocked_values=blocked_values,
        )
        occupancy_grid_elements(cell_elements, wall_elements, context="config")
        cell_size = spec.get("cell_size", DEFAULT_CELL_SIZE)
        wall_height = spec.get("wall_height", DEFAULT_WALL_HEIGHT)
        return OccupancyGridConfig(
            cell_elements=cell_elements,
            wall_elements=wall_elements,
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
        result: ConfigSpec = {
            "cell_elements": config.cell_elements.to_list(),
            "wall_elements": config.wall_elements.to_list(),
        }
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


def element_values(element_set: ElementSetLike) -> Set[int]:
    return {element.value for element in element_set.elements()}


def resolve_default_values(
    preferred_defaults: Dict[str, int],
    *,
    blocked_values: Set[int],
) -> Dict[str, int]:
    resolved: Dict[str, int] = {}
    used = set(blocked_values)
    for name, preferred in preferred_defaults.items():
        value = preferred
        while value in used:
            value += 1
        resolved[name] = value
        used.add(value)
    return resolved


def occupancy_grid_elements(
    cell_elements: ElementSetLike,
    wall_elements: ElementSetLike,
    *,
    context: str,
) -> ElementSet:
    elements = []
    token_owners: Dict[str, str] = {}
    value_owners: Dict[int, str] = {}

    for section, element_set in (
        ("cell_elements", cell_elements),
        ("wall_elements", wall_elements),
    ):
        for element in element_set.elements():
            token_owner = token_owners.get(element.token)
            if token_owner is not None:
                raise ValueError(
                    f"{context}.{section} token '{element.token}' duplicates {context}.{token_owner}"
                )

            value_owner = value_owners.get(element.value)
            if value_owner is not None:
                raise ValueError(
                    f"{context}.{section} value {element.value} duplicates {context}.{value_owner}"
                )

            token_owners[element.token] = section
            value_owners[element.value] = section
            elements.append(
                MazeElement(
                    name=f"{section}.{element.name}",
                    token=element.token,
                    value=element.value,
                )
            )

    return ElementSet(elements)


HANDLER = OccupancyGridHandler()
