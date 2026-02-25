from __future__ import annotations

from pathlib import Path

from ..maze import Maze
from .extractors import MazeCellsExtractorRegistry
from .model import LoadedMazeLayout
from .semantics import MazeSemanticsBuilder


class MazeRuntimeLoader:
    def __init__(
        self,
        maze_file: str | Path,
        cells_registry: MazeCellsExtractorRegistry | None = None,
        semantics_builder: MazeSemanticsBuilder | None = None,
    ):
        self.maze_file = Path(maze_file)
        self.cells_registry = cells_registry or MazeCellsExtractorRegistry()
        self.semantics_builder = semantics_builder or MazeSemanticsBuilder()

    def load(self) -> LoadedMazeLayout:
        maze = Maze.from_file(str(self.maze_file))
        cells = self.cells_registry.extract_cells(maze.maze_type, maze.layout)
        semantics = self.semantics_builder.build(maze.config)
        cell_size = float(maze.config.cell_size)
        if cell_size <= 0.0:
            raise ValueError(f"config.cell_size must be positive; got {cell_size} in {self.maze_file}")
        return LoadedMazeLayout(
            maze_type=maze.maze_type,
            cells=cells,
            semantics=semantics,
            cell_size=cell_size,
        )
