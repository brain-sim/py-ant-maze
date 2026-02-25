from __future__ import annotations

from typing import Protocol, Sequence

from .model import MazeCells


class MazeCellsExtractor(Protocol):
    maze_type: str

    def extract(self, layout: object) -> Sequence[Sequence[int]]:
        ...


class EdgeGridCellsExtractor:
    maze_type = "edge_grid"

    def extract(self, layout: object) -> Sequence[Sequence[int]]:
        return layout.cells


class OccupancyGridCellsExtractor:
    maze_type = "occupancy_grid"

    def extract(self, layout: object) -> Sequence[Sequence[int]]:
        return layout.grid


class MazeCellsExtractorRegistry:
    def __init__(self, extractors: Sequence[MazeCellsExtractor] | None = None):
        if extractors is None:
            extractors = (EdgeGridCellsExtractor(), OccupancyGridCellsExtractor())
        self._extractors = {extractor.maze_type: extractor for extractor in extractors}

    def extract_cells(self, maze_type: str, layout: object) -> MazeCells:
        extractor = self._extractors.get(maze_type)
        if extractor is None:
            supported = ", ".join(sorted(self._extractors))
            raise ValueError(f"Unsupported maze_type={maze_type!r}; supported types: {supported}")

        values = extractor.extract(layout)
        rows = len(values)
        if rows == 0:
            raise ValueError("Maze layout has no rows.")
        cols = len(values[0])
        if cols == 0:
            raise ValueError("Maze layout has no columns.")
        for row_idx, row in enumerate(values):
            if len(row) != cols:
                raise ValueError(
                    f"Maze layout is not rectangular: row 0 has {cols} values but row {row_idx} has {len(row)} values."
                )

        return MazeCells(values=values, rows=rows, cols=cols)
