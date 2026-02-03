from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import yaml

from .core.parsing.multi_level import LevelIdentifier, resolve_level
from .core.registry import get_handler
from .core.types import Grid
from .core.types import MazeSpec, MazeType
from .io.serialization import dump_yaml


@dataclass(frozen=True)
class Maze:
    maze_type: MazeType
    config: Any
    layout: Any

    @classmethod
    def from_text(cls, text: str) -> "Maze":
        return MazeDraft.from_text(text).freeze()

    @classmethod
    def from_file(cls, path: str) -> "Maze":
        return MazeDraft.from_file(path).freeze()

    def to_text(self, with_grid_numbers: bool = False) -> str:
        maze_spec = self.to_spec(with_grid_numbers=with_grid_numbers)
        return dump_yaml(maze_spec)

    def to_file(self, path: str, with_grid_numbers: bool = False) -> None:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(self.to_text(with_grid_numbers=with_grid_numbers))

    def to_spec(self, with_grid_numbers: bool = False) -> MazeSpec:
        handler = get_handler(self.maze_type)
        return handler.to_spec(self.config, self.layout, with_grid_numbers)

    @classmethod
    def from_spec(cls, maze_spec: MazeSpec) -> "Maze":
        return MazeDraft.from_spec(maze_spec).freeze()

    def validate(self) -> None:
        handler = get_handler(self.maze_type)
        handler.validate(self.config, self.layout)

    def thaw(self) -> "MazeDraft":
        return MazeDraft.from_maze(self)


@dataclass
class MazeDraft:
    maze_type: MazeType
    config: Any
    layout: Any

    @classmethod
    def from_text(cls, text: str) -> "MazeDraft":
        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            raise TypeError("maze YAML must be a dict")
        return cls.from_spec(data)

    @classmethod
    def from_file(cls, path: str) -> "MazeDraft":
        with open(path, "r", encoding="utf-8") as handle:
            return cls.from_text(handle.read())

    def to_text(self, with_grid_numbers: bool = False) -> str:
        maze_spec = self.to_spec(with_grid_numbers=with_grid_numbers)
        return dump_yaml(maze_spec)

    def to_file(self, path: str, with_grid_numbers: bool = False) -> None:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(self.to_text(with_grid_numbers=with_grid_numbers))

    def to_spec(self, with_grid_numbers: bool = False) -> MazeSpec:
        handler = get_handler(self.maze_type)
        return handler.to_spec(self.config, self.layout, with_grid_numbers)

    @classmethod
    def from_spec(cls, maze_spec: MazeSpec) -> "MazeDraft":
        maze_type = maze_spec.get("maze_type")
        if not maze_type:
            raise ValueError("maze_type is required")
        config_spec = maze_spec.get("config", {})
        layout_spec = maze_spec.get("layout")
        if layout_spec is None:
            raise ValueError("layout is required")

        handler = get_handler(maze_type)
        config = handler.parse_config(config_spec)
        layout = handler.parse_layout(layout_spec, config)
        return cls(handler.maze_type, config, layout)

    @classmethod
    def from_maze(cls, maze: Maze) -> "MazeDraft":
        handler = get_handler(maze.maze_type)
        config, layout = handler.thaw(maze.config, maze.layout)
        return cls(handler.maze_type, config, layout)

    def validate(self) -> None:
        handler = get_handler(self.maze_type)
        handler.validate(self.config, self.layout)

    def freeze(self) -> Maze:
        self._ensure_mutable()
        handler = get_handler(self.maze_type)
        handler.validate(self.config, self.layout)
        config, layout = handler.freeze(self.config, self.layout)
        return Maze(handler.maze_type, config, layout)

    def set_cell(self, row: int, col: int, value: int, *, level: Optional[LevelIdentifier] = None) -> None:
        self._ensure_mutable()
        if self.maze_type == "occupancy_grid":
            _set_grid_value(self.layout.grid, row, col, value, context="layout.grid")
            return
        if self.maze_type == "edge_grid":
            _set_grid_value(self.layout.cells, row, col, value, context="layout.cells")
            return
        if self.maze_type == "occupancy_grid_3d":
            level_layout = self._get_level_layout(level)
            _set_grid_value(level_layout.layout.grid, row, col, value, context="layout.levels[].layout.grid")
            return
        if self.maze_type == "edge_grid_3d":
            level_layout = self._get_level_layout(level)
            _set_grid_value(level_layout.layout.cells, row, col, value, context="layout.levels[].layout.cells")
            return
        raise ValueError(f"set_cell is not supported for maze_type: {self.maze_type}")

    def set_wall(
        self,
        row: int,
        col: int,
        value: int,
        wall_type: str,
        *,
        level: Optional[LevelIdentifier] = None,
    ) -> None:
        self._ensure_mutable()
        if wall_type not in {"vertical", "horizontal"}:
            raise ValueError("wall_type must be 'vertical' or 'horizontal'")

        if self.maze_type == "edge_grid":
            grid = self.layout.vertical_walls if wall_type == "vertical" else self.layout.horizontal_walls
            _set_grid_value(grid, row, col, value, context=f"layout.walls.{wall_type}")
            return
        if self.maze_type == "edge_grid_3d":
            level_layout = self._get_level_layout(level)
            grid = (
                level_layout.layout.vertical_walls
                if wall_type == "vertical"
                else level_layout.layout.horizontal_walls
            )
            _set_grid_value(grid, row, col, value, context=f"layout.levels[].layout.walls.{wall_type}")
            return
        raise ValueError(f"set_wall is not supported for maze_type: {self.maze_type}")

    def set_arm_cell(
        self,
        arm: int,
        row: int,
        col: int,
        value: int,
        *,
        level: Optional[LevelIdentifier] = None,
    ) -> None:
        self._ensure_mutable()
        if self.maze_type == "radial_arm":
            arm_layout = self._get_arm_layout(arm)
            _set_grid_value(arm_layout.cells, row, col, value, context="layout.arms[].layout.cells")
            return
        if self.maze_type == "radial_arm_3d":
            level_layout = self._get_level_layout(level)
            arm_layout = self._get_arm_layout(arm, level_layout=level_layout)
            _set_grid_value(arm_layout.cells, row, col, value, context="layout.levels[].layout.arms[].layout.cells")
            return
        raise ValueError(f"set_arm_cell is not supported for maze_type: {self.maze_type}")

    def set_arm_wall(
        self,
        arm: int,
        row: int,
        col: int,
        value: int,
        wall_type: str,
        *,
        level: Optional[LevelIdentifier] = None,
    ) -> None:
        self._ensure_mutable()
        if wall_type not in {"vertical", "horizontal"}:
            raise ValueError("wall_type must be 'vertical' or 'horizontal'")

        if self.maze_type == "radial_arm":
            arm_layout = self._get_arm_layout(arm)
            grid = arm_layout.vertical_walls if wall_type == "vertical" else arm_layout.horizontal_walls
            _set_grid_value(grid, row, col, value, context=f"layout.arms[].layout.walls.{wall_type}")
            return
        if self.maze_type == "radial_arm_3d":
            level_layout = self._get_level_layout(level)
            arm_layout = self._get_arm_layout(arm, level_layout=level_layout)
            grid = arm_layout.vertical_walls if wall_type == "vertical" else arm_layout.horizontal_walls
            _set_grid_value(grid, row, col, value, context=f"layout.levels[].layout.arms[].layout.walls.{wall_type}")
            return
        raise ValueError(f"set_arm_wall is not supported for maze_type: {self.maze_type}")

    def _ensure_mutable(self) -> None:
        handler = get_handler(self.maze_type)
        self.config, self.layout = handler.thaw(self.config, self.layout)

    def _get_level_layout(self, level: Optional[LevelIdentifier]):
        if level is None:
            raise ValueError("level is required for 3D maze types")
        levels = self.layout.levels
        definitions = [entry.definition for entry in levels]
        resolved = resolve_level(definitions, level, context="level")
        return levels[resolved.index]

    def _get_arm_layout(self, arm: int, *, level_layout: Any = None):
        if level_layout is None:
            arms = self.layout.arms
        else:
            arms = level_layout.layout.arms
        if arm < 0 or arm >= len(arms):
            raise ValueError("arm index out of range")
        return arms[arm]


def _set_grid_value(grid: Grid, row: int, col: int, value: int, *, context: str) -> None:
    if not isinstance(row, int) or not isinstance(col, int):
        raise TypeError(f"{context} row/col must be integers")
    if row < 0 or col < 0:
        raise ValueError(f"{context} row/col must be >= 0")
    if row >= len(grid):
        raise ValueError(f"{context} row is out of range")
    if col >= len(grid[row]):
        raise ValueError(f"{context} col is out of range")
    grid[row][col] = value
