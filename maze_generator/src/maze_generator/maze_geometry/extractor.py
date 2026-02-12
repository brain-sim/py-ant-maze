"""Geometry extraction from py_ant_maze mazes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

from py_ant_maze import Maze

from .models import MazeGeometry, WallBox

Grid = Sequence[Sequence[int]]
WallValueMap = dict[int, str]


class GeometryExtractor(Protocol):
    def extract(self, maze: Maze) -> MazeGeometry:
        ...


def extract_geometry(maze: Maze) -> MazeGeometry:
    extractor = _EXTRACTORS.get(maze.maze_type)
    if extractor is None:
        supported = ", ".join(sorted(_EXTRACTORS))
        raise ValueError(f"Unsupported maze type: {maze.maze_type!r}. Supported: {supported}")
    return extractor.extract(maze)


@dataclass(frozen=True, slots=True)
class OccupancyGridExtractor:
    def extract(self, maze: Maze) -> MazeGeometry:
        grid = maze.layout.grid
        rows, cols = _validate_rectangular_grid("layout.grid", grid)
        cell_size = _validate_positive_scalar("cell_size", maze.config.cell_size)
        wall_height = _validate_positive_scalar("wall_height", maze.config.wall_height)
        wall_map = _wall_value_map(maze)
        cell_values = {element.value for element in maze.config.cell_elements.elements()}
        known_values = set(wall_map).union(cell_values)

        walls: list[WallBox] = []
        for row in range(rows):
            for col in range(cols):
                value = grid[row][col]
                if value not in known_values:
                    raise ValueError(f"Unknown grid value {value} at layout.grid[{row}][{col}]")
                element_name = wall_map.get(value)
                if element_name is None:
                    continue
                walls.append(
                    WallBox(
                        center=((col + 0.5) * cell_size, (row + 0.5) * cell_size, wall_height / 2.0),
                        size=(cell_size, cell_size, wall_height),
                        element_name=element_name,
                    )
                )

        return MazeGeometry.from_walls(walls, bounds=(cols * cell_size, rows * cell_size, wall_height))


@dataclass(frozen=True, slots=True)
class EdgeGridExtractor:
    def extract(self, maze: Maze) -> MazeGeometry:
        cells = maze.layout.cells
        rows, cols = _validate_rectangular_grid("layout.cells", cells)
        v_walls = maze.layout.vertical_walls
        h_walls = maze.layout.horizontal_walls
        _validate_grid_shape("layout.vertical_walls", v_walls, expected_rows=rows, expected_cols=cols + 1)
        _validate_grid_shape("layout.horizontal_walls", h_walls, expected_rows=rows + 1, expected_cols=cols)

        cell_size = _validate_positive_scalar("cell_size", maze.config.cell_size)
        wall_height = _validate_positive_scalar("wall_height", maze.config.wall_height)
        wall_thickness = _validate_positive_scalar("wall_thickness", maze.config.wall_thickness)
        wall_map = _wall_value_map(maze)
        open_values = {
            element.value for element in maze.config.wall_elements.elements() if element.name.lower() == "open"
        }

        walls: list[WallBox] = []
        for row in range(rows):
            for col in range(cols + 1):
                value = v_walls[row][col]
                if value in open_values:
                    continue
                element_name = _resolve_wall_name(wall_map, value, "layout.vertical_walls", row, col)
                walls.append(
                    WallBox(
                        center=(col * cell_size, (row + 0.5) * cell_size, wall_height / 2.0),
                        size=(wall_thickness, cell_size, wall_height),
                        element_name=element_name,
                    )
                )

        for row in range(rows + 1):
            for col in range(cols):
                value = h_walls[row][col]
                if value in open_values:
                    continue
                element_name = _resolve_wall_name(wall_map, value, "layout.horizontal_walls", row, col)
                walls.append(
                    WallBox(
                        center=((col + 0.5) * cell_size, row * cell_size, wall_height / 2.0),
                        size=(cell_size, wall_thickness, wall_height),
                        element_name=element_name,
                    )
                )

        return MazeGeometry.from_walls(walls, bounds=(cols * cell_size, rows * cell_size, wall_height))


_EXTRACTORS: dict[str, GeometryExtractor] = {
    "occupancy_grid": OccupancyGridExtractor(),
    "edge_grid": EdgeGridExtractor(),
}


def _wall_value_map(maze: Maze) -> WallValueMap:
    wall_elements = maze.config.wall_elements.elements()
    if not wall_elements:
        raise ValueError("maze config must contain at least one wall element")
    return {element.value: element.name for element in wall_elements}


def _resolve_wall_name(
    wall_map: WallValueMap,
    value: int,
    grid_name: str,
    row: int,
    col: int,
) -> str:
    element_name = wall_map.get(value)
    if element_name is None:
        raise ValueError(f"Unknown wall value {value} at {grid_name}[{row}][{col}]")
    return element_name


def _validate_positive_scalar(name: str, value: float) -> float:
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric")
    if value <= 0:
        raise ValueError(f"{name} must be > 0")
    return float(value)


def _validate_grid_shape(grid_name: str, grid: Grid, *, expected_rows: int, expected_cols: int) -> None:
    rows, cols = _validate_rectangular_grid(grid_name, grid)
    if rows != expected_rows or cols != expected_cols:
        raise ValueError(f"{grid_name} must be {expected_rows}x{expected_cols}, got {rows}x{cols}")


def _validate_rectangular_grid(grid_name: str, grid: Grid) -> tuple[int, int]:
    if not isinstance(grid, (list, tuple)):
        raise TypeError(f"{grid_name} must be a sequence of rows")
    if not grid:
        raise ValueError(f"{grid_name} cannot be empty")

    cols = None
    for row_index, row in enumerate(grid):
        if not isinstance(row, (list, tuple)):
            raise TypeError(f"{grid_name}[{row_index}] must be a sequence")
        if cols is None:
            cols = len(row)
            if cols == 0:
                raise ValueError(f"{grid_name} rows cannot be empty")
        elif len(row) != cols:
            raise ValueError(f"{grid_name} must be rectangular")

        for col_index, value in enumerate(row):
            if not isinstance(value, int):
                raise TypeError(f"{grid_name}[{row_index}][{col_index}] must be an integer")

    return len(grid), cols
