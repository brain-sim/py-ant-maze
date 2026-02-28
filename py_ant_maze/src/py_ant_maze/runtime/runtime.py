from __future__ import annotations

from dataclasses import dataclass

from ..maze import Maze
from .extractors import MazeCellsExtractorRegistry
from .model import MazeCells, MazeSemantics
from .semantics import MazeSemanticsBuilder


@dataclass(frozen=True)
class MazeRuntime:
    maze: Maze
    cells: MazeCells
    semantics: MazeSemantics
    cell_size: float

    @classmethod
    def from_maze(
        cls,
        maze: Maze,
        cells_registry: MazeCellsExtractorRegistry | None = None,
        semantics_builder: MazeSemanticsBuilder | None = None,
    ) -> "MazeRuntime":
        cells_registry = cells_registry or MazeCellsExtractorRegistry()
        semantics_builder = semantics_builder or MazeSemanticsBuilder()

        cells = cells_registry.extract_cells(maze.maze_type, maze.layout)
        semantics = semantics_builder.build(maze.config)
        cell_size = float(maze.config.cell_size)
        if cell_size <= 0.0:
            raise ValueError(f"config.cell_size must be positive; got {cell_size}")
        return cls(maze=maze, cells=cells, semantics=semantics, cell_size=cell_size)

    @property
    def maze_type(self) -> str:
        return self.maze.maze_type

    @property
    def rows(self) -> int:
        return self.cells.rows

    @property
    def cols(self) -> int:
        return self.cells.cols

    @property
    def width(self) -> float:
        return float(self.cols) * self.cell_size

    @property
    def height(self) -> float:
        return float(self.rows) * self.cell_size
