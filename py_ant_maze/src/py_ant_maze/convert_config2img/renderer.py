"""Maze-to-image renderer for 2D occupancy and edge grids."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

from PIL import Image, ImageDraw

from ..maze import Maze, MazeDraft
from .colors import WebColorResolver
from .models import RGB, RenderPalette, RenderSizing

RectSpec = Tuple[int, int, int, int, RGB]


class MazeConfigImageRenderer:
    def __init__(
        self,
        *,
        sizing: RenderSizing | None = None,
        palette: RenderPalette | None = None,
    ) -> None:
        self.sizing = sizing or RenderSizing()
        self.palette = palette or RenderPalette()
        self.color_resolver = WebColorResolver(self.palette)

    def render(self, maze: Maze | MazeDraft) -> Image.Image:
        frozen = maze.freeze() if isinstance(maze, MazeDraft) else maze
        if frozen.maze_type == "occupancy_grid":
            return self._render_occupancy_grid(frozen)
        if frozen.maze_type == "edge_grid":
            return self._render_edge_grid(frozen)
        raise ValueError(
            "convert_config2img supports only 2D occupancy_grid and edge_grid "
            f"(got {frozen.maze_type!r})"
        )

    def _render_occupancy_grid(self, maze: Maze) -> Image.Image:
        grid = _validated_rect_grid(maze.layout.grid, context="layout.grid")
        rows = len(grid)
        cols = len(grid[0])
        cell_size = _cell_size(rows, cols, self.sizing)

        gap = self.sizing.occupancy_gap
        grid_padding = self.sizing.occupancy_padding
        frame_padding = self.sizing.frame_padding

        content_width = cols * cell_size + (cols - 1) * gap + 2 * grid_padding
        content_height = rows * cell_size + (rows - 1) * gap + 2 * grid_padding
        width = content_width + 2 * frame_padding
        height = content_height + 2 * frame_padding

        image = Image.new("RGB", (width, height), self.palette.image_background)
        draw = ImageDraw.Draw(image)
        _draw_rect(
            draw,
            frame_padding,
            frame_padding,
            content_width,
            content_height,
            self.palette.occupancy_container,
        )

        cell_name_by_value = _element_name_by_value(maze.config.cell_elements)
        wall_name_by_value = _element_name_by_value(maze.config.wall_elements)

        origin_x = frame_padding + grid_padding
        origin_y = frame_padding + grid_padding

        for row_index in range(rows):
            for col_index in range(cols):
                value = grid[row_index][col_index]
                if value in cell_name_by_value:
                    layer = "cell"
                    name = cell_name_by_value[value]
                elif value in wall_name_by_value:
                    layer = "wall"
                    name = wall_name_by_value[value]
                else:
                    layer = "cell"
                    name = "unknown"

                color = self.color_resolver.resolve(name, layer=layer)
                x = origin_x + col_index * (cell_size + gap)
                y = origin_y + row_index * (cell_size + gap)
                _draw_rect(draw, x, y, cell_size, cell_size, color)

        return image

    def _render_edge_grid(self, maze: Maze) -> Image.Image:
        cells = _validated_rect_grid(maze.layout.cells, context="layout.cells")
        vertical_walls = _validated_rect_grid(maze.layout.vertical_walls, context="layout.vertical_walls")
        horizontal_walls = _validated_rect_grid(
            maze.layout.horizontal_walls,
            context="layout.horizontal_walls",
        )

        rows = len(cells)
        cols = len(cells[0])
        _validate_edge_dimensions(rows, cols, vertical_walls, horizontal_walls)

        cell_size = _cell_size(rows, cols, self.sizing)
        wall_thickness = max(1, cell_size // 4)
        container_padding = self.sizing.edge_container_padding
        frame_padding = self.sizing.frame_padding

        grid_width = cols * (cell_size + wall_thickness) + wall_thickness
        grid_height = rows * (cell_size + wall_thickness) + wall_thickness
        content_width = grid_width + 2 * container_padding
        content_height = grid_height + 2 * container_padding
        width = content_width + 2 * frame_padding
        height = content_height + 2 * frame_padding

        image = Image.new("RGB", (width, height), self.palette.image_background)
        draw = ImageDraw.Draw(image)
        _draw_rect(
            draw,
            frame_padding,
            frame_padding,
            content_width,
            content_height,
            self.palette.edge_container,
        )

        cell_name_by_value = _element_name_by_value(maze.config.cell_elements)
        wall_name_by_value = _element_name_by_value(maze.config.wall_elements)

        grid_origin_x = frame_padding + container_padding
        grid_origin_y = frame_padding + container_padding
        corner_color = self.color_resolver.resolve("empty", layer="corner")

        corners: List[RectSpec] = []
        open_walls: List[RectSpec] = []
        cells_draw: List[RectSpec] = []
        solid_walls: List[RectSpec] = []

        for grid_row in range(rows * 2 + 1):
            is_wall_row = (grid_row % 2) == 0
            row_index = grid_row // 2

            for grid_col in range(cols * 2 + 1):
                is_wall_col = (grid_col % 2) == 0
                col_index = grid_col // 2

                if is_wall_row and is_wall_col:
                    x = _edge_offset(grid_col, cell_size, wall_thickness)
                    y = _edge_offset(grid_row, cell_size, wall_thickness)
                    corners.append((x, y, wall_thickness, wall_thickness, corner_color))
                    continue

                if is_wall_row:
                    value = horizontal_walls[row_index][col_index]
                    name = wall_name_by_value.get(value, "unknown")
                    color = self.color_resolver.resolve(name, layer="wall")
                    x = _edge_offset(grid_col, cell_size, wall_thickness)
                    y = _edge_offset(grid_row, cell_size, wall_thickness)
                    width_local = cell_size
                    height_local = wall_thickness
                    if value > 0:
                        x -= wall_thickness
                        width_local += 2 * wall_thickness
                    target = solid_walls if value > 0 else open_walls
                    target.append((x, y, width_local, height_local, color))
                    continue

                if is_wall_col:
                    value = vertical_walls[row_index][col_index]
                    name = wall_name_by_value.get(value, "unknown")
                    color = self.color_resolver.resolve(name, layer="wall")
                    x = _edge_offset(grid_col, cell_size, wall_thickness)
                    y = _edge_offset(grid_row, cell_size, wall_thickness)
                    width_local = wall_thickness
                    height_local = cell_size
                    if value > 0:
                        y -= wall_thickness
                        height_local += 2 * wall_thickness
                    target = solid_walls if value > 0 else open_walls
                    target.append((x, y, width_local, height_local, color))
                    continue

                value = cells[row_index][col_index]
                name = cell_name_by_value.get(value, "unknown")
                color = self.color_resolver.resolve(name, layer="cell")
                x = _edge_offset(grid_col, cell_size, wall_thickness)
                y = _edge_offset(grid_row, cell_size, wall_thickness)
                cells_draw.append((x, y, cell_size, cell_size, color))

        for specs in (corners, open_walls, cells_draw, solid_walls):
            for x, y, width_local, height_local, color in specs:
                _draw_rect(
                    draw,
                    grid_origin_x + x,
                    grid_origin_y + y,
                    width_local,
                    height_local,
                    color,
                )

        return image


def _validated_rect_grid(grid: Sequence[Sequence[int]], *, context: str) -> Sequence[Sequence[int]]:
    if not isinstance(grid, Sequence) or not grid:
        raise ValueError(f"{context} must be a non-empty sequence of rows")
    if not isinstance(grid[0], Sequence) or not grid[0]:
        raise ValueError(f"{context} first row must be non-empty")

    width = len(grid[0])
    for row_index, row in enumerate(grid):
        if not isinstance(row, Sequence):
            raise TypeError(f"{context}[{row_index}] must be a sequence")
        if len(row) != width:
            raise ValueError(f"{context} rows must all have the same length")
        for col_index, value in enumerate(row):
            if not isinstance(value, int):
                raise TypeError(f"{context}[{row_index}][{col_index}] must be an int")

    return grid


def _validate_edge_dimensions(
    rows: int,
    cols: int,
    vertical_walls: Sequence[Sequence[int]],
    horizontal_walls: Sequence[Sequence[int]],
) -> None:
    if len(vertical_walls) != rows:
        raise ValueError("layout.vertical_walls row count must match layout.cells")
    if len(horizontal_walls) != rows + 1:
        raise ValueError("layout.horizontal_walls row count must be layout.cells rows + 1")

    for row_index, row in enumerate(vertical_walls):
        if len(row) != cols + 1:
            raise ValueError(f"layout.vertical_walls[{row_index}] length must be layout.cells cols + 1")
    for row_index, row in enumerate(horizontal_walls):
        if len(row) != cols:
            raise ValueError(f"layout.horizontal_walls[{row_index}] length must match layout.cells cols")


def _element_name_by_value(element_set: Any) -> Dict[int, str]:
    return {element.value: element.name for element in element_set.elements()}


def _cell_size(rows: int, cols: int, sizing: RenderSizing) -> int:
    if rows <= 0 or cols <= 0:
        raise ValueError("rows and cols must be positive")
    size = sizing.target_dimension // max(rows, cols)
    return max(sizing.min_cell_size, min(sizing.max_cell_size, size))


def _edge_offset(index: int, cell_size: int, wall_thickness: int) -> int:
    if (index % 2) == 0:
        return (index // 2) * (cell_size + wall_thickness)
    return (index // 2) * (cell_size + wall_thickness) + wall_thickness


def _draw_rect(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int, color: RGB) -> None:
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")
    draw.rectangle((x, y, x + width - 1, y + height - 1), fill=color)
