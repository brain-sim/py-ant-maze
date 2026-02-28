from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

import numpy as np

from ..maze import Maze
from .extractors import MazeCellsExtractorRegistry
from .frames import FRAME_CONFIG, FRAME_SIMULATION, normalize_frame
from .model import MazeSemantics
from .runtime import MazeRuntime
from .semantics import MazeSemanticsBuilder


@dataclass(frozen=True)
class ResolvedCostSemantics:
    cell_values: frozenset[int]
    wall_values: frozenset[int]


@dataclass(frozen=True)
class CostSemanticTemplate:
    cell_include_names: tuple[str, ...] = ()
    wall_include_names: tuple[str, ...] = ()
    cell_exclude_names: tuple[str, ...] = ()
    wall_exclude_names: tuple[str, ...] = ()
    include_all_cells: bool = False
    include_all_walls: bool = False

    def resolve(self, semantics: MazeSemantics) -> ResolvedCostSemantics:
        cell_values = self._resolve_values(
            values_by_name=semantics.cell_values_by_name,
            include_names=self.cell_include_names,
            exclude_names=self.cell_exclude_names,
            include_all=self.include_all_cells,
        )
        wall_values = self._resolve_values(
            values_by_name=semantics.wall_values_by_name,
            include_names=self.wall_include_names,
            exclude_names=self.wall_exclude_names,
            include_all=self.include_all_walls,
        )
        return ResolvedCostSemantics(cell_values=cell_values, wall_values=wall_values)

    @staticmethod
    def _resolve_values(
        values_by_name: Mapping[str, frozenset[int]],
        include_names: Iterable[str],
        exclude_names: Iterable[str],
        include_all: bool,
    ) -> frozenset[int]:
        selected: set[int] = set()
        if include_all:
            for values in values_by_name.values():
                selected.update(values)
        else:
            for name in include_names:
                selected.update(values_by_name.get(str(name).strip().lower(), ()))

        for name in exclude_names:
            selected.difference_update(values_by_name.get(str(name).strip().lower(), ()))
        return frozenset(selected)


class MazeCostCalculator:
    def __init__(
        self,
        runtime: MazeRuntime,
        distance_lattice: np.ndarray,
        max_cost: float,
        distance_decay: float,
    ):
        if distance_decay <= 0.0:
            raise ValueError(f"distance_decay must be positive; got {distance_decay}")
        if max_cost < 0.0:
            raise ValueError(f"max_cost must be >= 0; got {max_cost}")

        self.runtime = runtime
        self.maze_type = runtime.maze_type
        self.cell_size = runtime.cell_size
        self.max_cost = float(max_cost)
        self.distance_decay = float(distance_decay)

        if distance_lattice.ndim != 2:
            raise ValueError("distance_lattice must be 2D")
        if distance_lattice.shape[0] < 3 or distance_lattice.shape[1] < 3:
            raise ValueError(f"distance_lattice is too small: {distance_lattice.shape}")

        self.rows = int((distance_lattice.shape[0] - 1) // 2)
        self.cols = int((distance_lattice.shape[1] - 1) // 2)
        self.width = self.cols * self.cell_size
        self.height = self.rows * self.cell_size
        self._meters_per_step = 0.5 * self.cell_size

        self._distance_lattice = np.asarray(distance_lattice, dtype=np.float64)
        self._cost_lattice = self.max_cost * np.exp(-self._distance_lattice / self.distance_decay)
        self._distance_cells = self._distance_lattice[1::2, 1::2]
        self._cost_cells = self._cost_lattice[1::2, 1::2]

        self._distance_lattice.setflags(write=False)
        self._cost_lattice.setflags(write=False)
        self._distance_cells.setflags(write=False)
        self._cost_cells.setflags(write=False)

    @classmethod
    def from_runtime(
        cls,
        runtime: MazeRuntime,
        semantic_template: CostSemanticTemplate,
        *,
        max_cost: float = 1.0,
        distance_decay: float = 0.5,
    ) -> "MazeCostCalculator":
        resolved = semantic_template.resolve(runtime.semantics)

        source_mask = _build_source_mask(
            maze_type=runtime.maze_type,
            layout=runtime.maze.layout,
            cells=np.asarray(runtime.cells.values, dtype=np.int64),
            resolved=resolved,
        )
        if not np.any(source_mask):
            raise ValueError("Resolved cost semantics produced no source elements.")

        distance_lattice = _distance_lattice(source_mask, meters_per_step=0.5 * runtime.cell_size)
        return cls(
            runtime=runtime,
            distance_lattice=distance_lattice,
            max_cost=max_cost,
            distance_decay=distance_decay,
        )

    @classmethod
    def from_maze(
        cls,
        maze: Maze,
        semantic_template: CostSemanticTemplate,
        *,
        max_cost: float = 1.0,
        distance_decay: float = 0.5,
        cells_registry: MazeCellsExtractorRegistry | None = None,
        semantics_builder: MazeSemanticsBuilder | None = None,
    ) -> "MazeCostCalculator":
        runtime = MazeRuntime.from_maze(
            maze,
            cells_registry=cells_registry,
            semantics_builder=semantics_builder,
        )
        return cls.from_runtime(
            runtime=runtime,
            semantic_template=semantic_template,
            max_cost=max_cost,
            distance_decay=distance_decay,
        )

    @property
    def distance_lattice(self) -> np.ndarray:
        return self._distance_lattice

    @property
    def cost_lattice(self) -> np.ndarray:
        return self._cost_lattice

    @property
    def distance_cells(self) -> np.ndarray:
        return self._distance_cells

    @property
    def cost_cells(self) -> np.ndarray:
        return self._cost_cells

    def distance_at_xy(self, xy: np.ndarray, frame: str = FRAME_CONFIG) -> np.ndarray | float:
        single, points = _normalize_xy(xy)
        points_cfg = self._to_config_frame(points, frame)
        values = _bilinear_interpolate(self._distance_lattice, points_cfg, self._meters_per_step)
        return float(values[0]) if single else values

    def cost_at_xy(self, xy: np.ndarray, frame: str = FRAME_CONFIG) -> np.ndarray | float:
        single, points = _normalize_xy(xy)
        points_cfg = self._to_config_frame(points, frame)
        values = _bilinear_interpolate(self._cost_lattice, points_cfg, self._meters_per_step)
        return float(values[0]) if single else values

    def _to_config_frame(self, points: np.ndarray, frame: str) -> np.ndarray:
        normalized = normalize_frame(frame)
        if normalized == FRAME_CONFIG:
            return points

        points_cfg = points.copy()
        if normalized == FRAME_SIMULATION:
            points_cfg[:, 1] = self.height - points_cfg[:, 1]
            return points_cfg

        raise ValueError(f"Unsupported frame: {frame}")


def _normalize_xy(xy: np.ndarray) -> tuple[bool, np.ndarray]:
    points = np.asarray(xy, dtype=np.float64)
    if points.ndim == 1:
        if points.shape[0] != 2:
            raise ValueError(f"Expected xy shape (2,), got {points.shape}")
        return True, points[None, :]
    if points.ndim == 2 and points.shape[1] == 2:
        return False, points
    raise ValueError(f"Expected xy shape (N,2) or (2,), got {points.shape}")


def _build_source_mask(
    maze_type: str,
    layout: object,
    cells: np.ndarray,
    resolved: ResolvedCostSemantics,
) -> np.ndarray:
    rows, cols = cells.shape
    source_mask = np.zeros((2 * rows + 1, 2 * cols + 1), dtype=bool)

    cell_source_values = set(resolved.cell_values)
    if maze_type == "occupancy_grid":
        cell_source_values.update(resolved.wall_values)

    if len(cell_source_values) > 0:
        source_values = np.fromiter(cell_source_values, dtype=np.int64)
        source_mask[1::2, 1::2] |= np.isin(cells, source_values)

    if maze_type == "edge_grid" and len(resolved.wall_values) > 0:
        wall_values = np.fromiter(resolved.wall_values, dtype=np.int64)
        vertical = np.asarray(layout.vertical_walls, dtype=np.int64)
        horizontal = np.asarray(layout.horizontal_walls, dtype=np.int64)

        if vertical.shape != (rows, cols + 1):
            raise ValueError(f"edge_grid vertical_walls shape mismatch: {vertical.shape} vs ({rows}, {cols + 1})")
        if horizontal.shape != (rows + 1, cols):
            raise ValueError(f"edge_grid horizontal_walls shape mismatch: {horizontal.shape} vs ({rows + 1}, {cols})")

        source_mask[1::2, ::2] |= np.isin(vertical, wall_values)
        source_mask[::2, 1::2] |= np.isin(horizontal, wall_values)

    return source_mask


def _distance_lattice(source_mask: np.ndarray, meters_per_step: float) -> np.ndarray:
    large = 1.0e20
    values = np.where(source_mask, 0.0, large).astype(np.float64)

    for col in range(values.shape[1]):
        values[:, col] = _edt_1d(values[:, col])
    for row in range(values.shape[0]):
        values[row, :] = _edt_1d(values[row, :])

    return np.sqrt(values) * meters_per_step


def _edt_1d(values: np.ndarray) -> np.ndarray:
    n = values.shape[0]
    v = np.zeros(n, dtype=np.int64)
    z = np.zeros(n + 1, dtype=np.float64)
    d = np.zeros(n, dtype=np.float64)

    k = 0
    v[0] = 0
    z[0] = -np.inf
    z[1] = np.inf

    for q in range(1, n):
        s = _intersection(values, q, v[k])
        while s <= z[k]:
            k -= 1
            s = _intersection(values, q, v[k])
        k += 1
        v[k] = q
        z[k] = s
        z[k + 1] = np.inf

    k = 0
    for q in range(n):
        while z[k + 1] < q:
            k += 1
        diff = q - v[k]
        d[q] = diff * diff + values[v[k]]
    return d


def _intersection(values: np.ndarray, q: int, p: int) -> float:
    return ((values[q] + q * q) - (values[p] + p * p)) / (2.0 * (q - p))


def _bilinear_interpolate(grid: np.ndarray, xy_config: np.ndarray, meters_per_step: float) -> np.ndarray:
    max_row = grid.shape[0] - 1
    max_col = grid.shape[1] - 1

    col_f = np.clip(xy_config[:, 0] / meters_per_step, 0.0, float(max_col))
    row_f = np.clip(xy_config[:, 1] / meters_per_step, 0.0, float(max_row))

    col0 = np.floor(col_f).astype(np.int64)
    row0 = np.floor(row_f).astype(np.int64)
    col1 = np.minimum(col0 + 1, max_col)
    row1 = np.minimum(row0 + 1, max_row)

    col_w = col_f - col0
    row_w = row_f - row0

    g00 = grid[row0, col0]
    g10 = grid[row1, col0]
    g01 = grid[row0, col1]
    g11 = grid[row1, col1]

    top = g00 * (1.0 - col_w) + g01 * col_w
    bottom = g10 * (1.0 - col_w) + g11 * col_w
    return top * (1.0 - row_w) + bottom * row_w
