"""Extract wall geometry from py_ant_maze Maze objects.

Dimensions (cell_size, wall_height, wall_thickness) are read from the
maze's config object. These can be set in the YAML config section.
"""

from __future__ import annotations

from typing import List

from py_ant_maze import Maze

from .types import MazeGeometry, WallBox


def extract_geometry(maze: Maze) -> MazeGeometry:
    """Extract wall geometry from a Maze.

    Physical dimensions are read from the maze config
    (cell_size, wall_height, wall_thickness).

    Args:
        maze: A frozen py_ant_maze.Maze.

    Returns:
        MazeGeometry with wall boxes in world space.

    Raises:
        ValueError: If the maze type is not supported.
    """
    if maze.maze_type == "occupancy_grid":
        return _extract_occupancy_grid(maze)
    elif maze.maze_type == "edge_grid":
        return _extract_edge_grid(maze)
    else:
        raise ValueError(f"Unsupported maze type: {maze.maze_type}")


def _extract_occupancy_grid(maze: Maze) -> MazeGeometry:
    """Extract walls from an occupancy_grid maze.

    Non-open cells (value != 0) become full cell-sized wall boxes.
    Reads cell_size and wall_height from maze.config.
    """
    grid = maze.layout.grid
    elements = maze.config.cell_elements
    cell_size = maze.config.cell_size
    wall_height = maze.config.wall_height

    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    walls: List[WallBox] = []

    for r in range(rows):
        for c in range(cols):
            value = grid[r][c]
            element = elements.element_for_value(value)

            # Skip open cells (value 0 by convention)
            if value == 0:
                continue

            # Center of this cell in world space
            # Origin at top-left corner; x increases right, y increases down
            cx = (c + 0.5) * cell_size
            cy = (r + 0.5) * cell_size
            cz = wall_height / 2.0

            walls.append(WallBox(
                center=(cx, cy, cz),
                size=(cell_size, cell_size, wall_height),
                element_name=element.name,
            ))

    bounds = (cols * cell_size, rows * cell_size, wall_height)
    return MazeGeometry(walls=walls, bounds=bounds)


def _extract_edge_grid(maze: Maze) -> MazeGeometry:
    """Extract walls from an edge_grid maze.

    vertical_walls and horizontal_walls grids produce thin wall boxes.
    Walls with value 0 (open) are skipped.
    Reads cell_size, wall_height, wall_thickness from maze.config.
    """
    v_walls = maze.layout.vertical_walls
    h_walls = maze.layout.horizontal_walls
    wall_elements = maze.config.wall_elements
    cell_size = maze.config.cell_size
    wall_height = maze.config.wall_height
    wall_thickness = maze.config.wall_thickness

    # Grid dimensions from cell grid
    cells = maze.layout.cells
    rows = len(cells)
    cols = len(cells[0]) if rows > 0 else 0

    walls: List[WallBox] = []

    # Vertical walls: rows × (cols + 1)
    # A vertical wall at (r, c) sits on the left edge of cell (r, c).
    for r in range(len(v_walls)):
        for c in range(len(v_walls[r])):
            value = v_walls[r][c]
            if value == 0:
                continue

            element = wall_elements.element_for_value(value)

            cx = c * cell_size
            cy = (r + 0.5) * cell_size
            cz = wall_height / 2.0

            walls.append(WallBox(
                center=(cx, cy, cz),
                size=(wall_thickness, cell_size, wall_height),
                element_name=element.name,
            ))

    # Horizontal walls: (rows + 1) × cols
    # A horizontal wall at (r, c) sits on the top edge of cell (r, c).
    for r in range(len(h_walls)):
        for c in range(len(h_walls[r])):
            value = h_walls[r][c]
            if value == 0:
                continue

            element = wall_elements.element_for_value(value)

            cx = (c + 0.5) * cell_size
            cy = r * cell_size
            cz = wall_height / 2.0

            walls.append(WallBox(
                center=(cx, cy, cz),
                size=(cell_size, wall_thickness, wall_height),
                element_name=element.name,
            ))

    bounds = (cols * cell_size, rows * cell_size, wall_height)
    return MazeGeometry(walls=walls, bounds=bounds)
