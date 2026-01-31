import math
from typing import Any, Dict, List, Optional

from ..core.element_set import ElementSet
from ..core.elements import CellElement, WallElement
from ..core.grid import format_grid, parse_grid
from ..io.yaml_types import QuotedStr, literal_block


class RadialArmConfig:
    def __init__(
        self,
        cell_elements: ElementSet,
        wall_elements: ElementSet,
    ) -> None:
        self.cell_elements = cell_elements
        self.wall_elements = wall_elements

    @classmethod
    def from_mapping(cls, mapping: Dict[str, Any]) -> "RadialArmConfig":
        if not isinstance(mapping, dict):
            raise TypeError("config must be a mapping")
        cell_items = mapping.get("cell_elements")
        wall_items = mapping.get("wall_elements")
        if cell_items is None:
            cell_items = mapping.get("elements")
        if cell_items is None:
            raise ValueError("config.cell_elements is required")
        if wall_items is None:
            raise ValueError("config.wall_elements is required")

        cell_elements = _parse_cell_elements(cell_items)
        wall_elements = _parse_wall_elements(wall_items)
        return cls(cell_elements, wall_elements)

    def to_mapping(self) -> Dict[str, Any]:
        return {
            "cell_elements": self.cell_elements.to_list(token_wrapper=QuotedStr),
            "wall_elements": self.wall_elements.to_list(token_wrapper=QuotedStr),
        }


class RadialArmLayout:
    def __init__(
        self,
        hub: "RadialArmHub",
        arms: List["RadialArmArm"],
    ) -> None:
        self.hub = hub
        self.arms = arms

    @classmethod
    def from_mapping(
        cls,
        mapping: Dict[str, Any],
        config: RadialArmConfig,
    ) -> "RadialArmLayout":
        if not isinstance(mapping, dict):
            raise TypeError("layout must be a mapping")
        hub_spec = mapping.get("center_hub")
        arms_spec = mapping.get("arms")
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
        return cls(hub, arms)

    def to_mapping(self, config: RadialArmConfig, with_grid_numbers: bool) -> Dict[str, Any]:
        hub_mapping: Dict[str, Any] = {
            "shape": self.hub.shape,
            "angle_degrees": self.hub.angle_degrees,
        }
        if self.hub.shape == "circular":
            hub_mapping["radius"] = self.hub.radius
        elif self.hub.shape == "polygon":
            hub_mapping["side_length"] = self.hub.side_length
            hub_mapping["sides"] = self.hub.sides
        arms_mapping = [_arm_to_mapping(arm, with_grid_numbers) for arm in self.arms]
        return {"center_hub": hub_mapping, "arms": arms_mapping}


class RadialArmArm:
    def __init__(
        self,
        cell_elements: ElementSet,
        wall_elements: ElementSet,
        cells: List[List[int]],
        vertical_walls: List[List[int]],
        horizontal_walls: List[List[int]],
    ) -> None:
        self.cell_elements = cell_elements
        self.wall_elements = wall_elements
        self.cells = cells
        self.vertical_walls = vertical_walls
        self.horizontal_walls = horizontal_walls


class RadialArmHub:
    def __init__(
        self,
        shape: str,
        angle_degrees: float,
        radius: Optional[float] = None,
        side_length: Optional[float] = None,
        sides: Optional[int] = None,
    ) -> None:
        self.shape = shape
        self.angle_degrees = angle_degrees
        self.radius = radius
        self.side_length = side_length
        self.sides = sides


def _parse_hub_spec(
    hub_spec: Dict[str, Any],
    arms: List[RadialArmArm],
) -> RadialArmHub:
    shape = hub_spec.get("shape")
    if shape not in {"circular", "polygon"}:
        raise ValueError("layout.center_hub.shape must be 'circular' or 'polygon'")
    if "arm_width" in hub_spec:
        raise ValueError("layout.center_hub.arm_width is derived from arm layouts")
    angle_degrees = _parse_angle_degrees(hub_spec.get("angle_degrees", 360.0))
    arm_count = len(arms)
    if arm_count == 0:
        raise ValueError("layout.arms must have at least one arm")
    arm_widths = [len(arm.cells) for arm in arms]

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

    sides = hub_spec.get("sides", arm_count)
    if not isinstance(sides, int) or isinstance(sides, bool) or sides < 3:
        raise ValueError("layout.center_hub.sides must be an integer >= 3")
    if sides != arm_count:
        raise ValueError("layout.center_hub.sides must match the number of arms")

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
        sides=sides,
    )


def _parse_cell_elements(items: List[Dict[str, Any]]) -> ElementSet:
    return ElementSet.from_list(
        items,
        CellElement,
        reserved_defaults={"open": 0},
    )


def _parse_wall_elements(items: List[Dict[str, Any]]) -> ElementSet:
    return ElementSet.from_list(
        items,
        WallElement,
        reserved_defaults={"open": 0, "wall": 1},
    )


def _parse_arms(arms_spec: List[Dict[str, Any]], config: RadialArmConfig) -> List[RadialArmArm]:
    arms: List[RadialArmArm] = []
    for index, arm_spec in enumerate(arms_spec):
        if not isinstance(arm_spec, dict):
            raise TypeError(f"layout.arms[{index}] must be a mapping")
        if "config" in arm_spec:
            raise ValueError(f"layout.arms[{index}].config is not allowed; use top-level config")
        layout_spec = arm_spec.get("layout", arm_spec)
        if layout_spec is None:
            raise ValueError(f"layout.arms[{index}].layout is required")
        if not isinstance(layout_spec, dict):
            raise TypeError(f"layout.arms[{index}].layout must be a mapping")

        cell_elements = config.cell_elements
        wall_elements = config.wall_elements

        cells_spec = layout_spec.get("cells")
        walls_spec = layout_spec.get("walls")
        if cells_spec is None:
            raise ValueError(f"layout.arms[{index}].layout.cells is required")
        if walls_spec is None:
            raise ValueError(f"layout.arms[{index}].layout.walls is required")
        if not isinstance(walls_spec, dict):
            raise TypeError(f"layout.arms[{index}].layout.walls must be a mapping")
        vertical_spec = walls_spec.get("vertical")
        horizontal_spec = walls_spec.get("horizontal")
        if vertical_spec is None or horizontal_spec is None:
            raise ValueError(
                f"layout.arms[{index}].layout.walls must include vertical and horizontal"
            )

        cells = parse_grid(cells_spec, cell_elements)
        vertical = parse_grid(vertical_spec, wall_elements)
        horizontal = parse_grid(horizontal_spec, wall_elements)
        _validate_arm_dimensions(cells, vertical, horizontal, index)
        arms.append(
            RadialArmArm(
                cell_elements=cell_elements,
                wall_elements=wall_elements,
                cells=cells,
                vertical_walls=vertical,
                horizontal_walls=horizontal,
            )
        )
    return arms


def _validate_arm_dimensions(
    cells: List[List[int]],
    vertical: List[List[int]],
    horizontal: List[List[int]],
    index: int,
) -> None:
    height = len(cells)
    width = len(cells[0]) if cells else 0
    if height == 0 or width == 0:
        raise ValueError(f"layout.arms[{index}].layout.cells must be non-empty")
    if len(vertical) != height:
        raise ValueError(
            f"layout.arms[{index}].layout.walls.vertical must have same number of rows as cells"
        )
    if any(len(row) != width + 1 for row in vertical):
        raise ValueError(
            f"layout.arms[{index}].layout.walls.vertical must have width + 1 columns"
        )
    if len(horizontal) != height + 1:
        raise ValueError(
            f"layout.arms[{index}].layout.walls.horizontal must have height + 1 rows"
        )
    if any(len(row) != width for row in horizontal):
        raise ValueError(
            f"layout.arms[{index}].layout.walls.horizontal must have same number of columns as cells"
        )


def _arm_to_mapping(arm: RadialArmArm, with_grid_numbers: bool) -> Dict[str, Any]:
    cell_lines = format_grid(arm.cells, arm.cell_elements, with_grid_numbers)
    vertical_lines = format_grid(arm.vertical_walls, arm.wall_elements, with_grid_numbers)
    horizontal_lines = format_grid(arm.horizontal_walls, arm.wall_elements, with_grid_numbers)
    return {
        "layout": {
            "cells": literal_block(cell_lines),
            "walls": {
                "vertical": literal_block(vertical_lines),
                "horizontal": literal_block(horizontal_lines),
            },
        },
    }


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


def _min_circular_radius(arm_widths: List[int], angle_degrees: float) -> float:
    angle_radians = math.radians(angle_degrees)
    total_width = sum(arm_widths)
    return total_width / angle_radians
