from typing import Dict, Optional, Set, TypeAlias

from ..structures.element_set import ElementSet
from ..structures.elements import CellElement, WallElement
from ..types import ConfigSpec, CellGrid, WallGrid


ElementDefaults: TypeAlias = Dict[str, int]
BlockedValues: TypeAlias = Set[int]


def parse_cell_elements(
    mapping: ConfigSpec,
    *,
    allow_elements_alias: bool = True,
    reserved_defaults: Optional[ElementDefaults] = None,
    blocked_values: Optional[BlockedValues] = None,
) -> ElementSet:
    if not isinstance(mapping, dict):
        raise TypeError("config must be a mapping")
    items = mapping.get("cell_elements")
    if items is None and allow_elements_alias:
        items = mapping.get("elements")
    if items is None:
        raise ValueError("config.cell_elements is required")
    reserved_defaults = reserved_defaults or {"open": 0, "wall": 1}
    return ElementSet.from_list(
        items,
        CellElement,
        reserved_defaults=reserved_defaults,
        blocked_values=blocked_values,
    )


def parse_wall_elements(
    mapping: ConfigSpec,
    *,
    reserved_defaults: Optional[ElementDefaults] = None,
    blocked_values: Optional[BlockedValues] = None,
) -> ElementSet:
    if not isinstance(mapping, dict):
        raise TypeError("config must be a mapping")
    items = mapping.get("wall_elements")
    if items is None:
        raise ValueError("config.wall_elements is required")
    reserved_defaults = reserved_defaults or {"open": 0, "wall": 1}
    return ElementSet.from_list(
        items,
        WallElement,
        reserved_defaults=reserved_defaults,
        blocked_values=blocked_values,
    )


def validate_edge_grid_dimensions(
    cells: CellGrid,
    vertical: WallGrid,
    horizontal: WallGrid,
    *,
    context: str,
) -> None:
    height = len(cells)
    width = len(cells[0]) if cells else 0
    if height == 0 or width == 0:
        raise ValueError(f"{context}.cells must be non-empty")
    if len(vertical) != height:
        raise ValueError(f"{context}.walls.vertical must have same number of rows as cells")
    if any(len(row) != width + 1 for row in vertical):
        raise ValueError(f"{context}.walls.vertical must have width + 1 columns")
    if len(horizontal) != height + 1:
        raise ValueError(f"{context}.walls.horizontal must have height + 1 rows")
    if any(len(row) != width for row in horizontal):
        raise ValueError(f"{context}.walls.horizontal must have same number of columns as cells")
