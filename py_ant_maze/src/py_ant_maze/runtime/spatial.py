from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Mapping, Sequence

import numpy as np

from ..maze import Maze
from .runtime import MazeRuntime

if TYPE_CHECKING:
    import torch


@dataclass(frozen=True)
class MazeSegmentSet:
    segments: np.ndarray
    values: np.ndarray


@dataclass(frozen=True)
class SpatialWallSemantics:
    seed_with_default_walls: bool = True
    include_all: bool = False
    include_names: tuple[str, ...] = ()
    include_tokens: tuple[str, ...] = ()
    include_values: tuple[int, ...] = ()
    exclude_names: tuple[str, ...] = ()
    exclude_tokens: tuple[str, ...] = ()
    exclude_values: tuple[int, ...] = ()


class BaseSpatialRuntime:
    expected_maze_type: str = ""

    def __init__(
        self,
        runtime: MazeRuntime,
        *,
        origin_xy: tuple[float, float] | None = None,
        wall_semantics: SpatialWallSemantics | None = None,
    ):
        if runtime.maze_type != self.expected_maze_type:
            raise ValueError(
                f"{self.__class__.__name__} expects maze_type={self.expected_maze_type!r}, "
                f"got {runtime.maze_type!r}."
            )

        self.runtime = runtime
        self.maze_type = runtime.maze_type
        self.cell_size = runtime.cell_size
        self.rows = runtime.rows
        self.cols = runtime.cols
        self.width = runtime.width
        self.height = runtime.height
        self.wall_height = float(runtime.maze.config.wall_height)
        self.wall_thickness = float(
            getattr(runtime.maze.config, "wall_thickness", runtime.cell_size)
        )
        self.origin_xy = (
            (-0.5 * self.width, -0.5 * self.height)
            if origin_xy is None
            else (float(origin_xy[0]), float(origin_xy[1]))
        )
        self._cell_center_offset_xy = (
            self.origin_xy[0] + 0.5 * self.cell_size,
            self.origin_xy[1] + 0.5 * self.cell_size,
        )

        self._cells = np.asarray(runtime.cells.values, dtype=np.int64)
        self._cell_values_by_name = runtime.semantics.cell_values_by_name
        self._wall_values_by_name = runtime.semantics.wall_values_by_name
        self._cell_values_by_token = runtime.semantics.cell_values_by_token
        self._wall_values_by_token = runtime.semantics.wall_values_by_token
        self._all_wall_values = self._collect_all_wall_values()
        self._active_wall_values = self._resolve_wall_values(wall_semantics)

        segment_set = self._build_wall_segments_for_values(self._active_wall_values)
        self._wall_segments = segment_set.segments
        self._wall_segment_values = segment_set.values

        self._torch_device: torch.device | None = None
        self._wall_segments_torch: torch.Tensor | None = None
        self._wall_segment_values_torch: torch.Tensor | None = None

    @classmethod
    def from_maze(
        cls,
        maze: Maze,
        *,
        origin_xy: tuple[float, float] | None = None,
        wall_semantics: SpatialWallSemantics | None = None,
    ) -> BaseSpatialRuntime:
        return create_spatial_runtime(
            MazeRuntime.from_maze(maze),
            origin_xy=origin_xy,
            wall_semantics=wall_semantics,
        )

    def update_torch_device(self, device: str | torch.device):
        import torch

        torch_device = torch.device(device) if isinstance(device, str) else device
        if self._torch_device == torch_device:
            return
        self._torch_device = torch_device
        self._wall_segments_torch = torch.from_numpy(self._wall_segments).to(
            device=torch_device, dtype=torch.float32
        )
        self._wall_segment_values_torch = torch.from_numpy(
            self._wall_segment_values
        ).to(device=torch_device, dtype=torch.int32)

    def get_random_valid_position(self, valid_indicator: int | str = 0) -> np.ndarray:
        return self.get_random_valid_positions(1, valid_indicator=valid_indicator)[0]

    def get_random_valid_positions(
        self,
        num_positions: int,
        valid_indicator: int | str = 0,
    ) -> np.ndarray:
        if num_positions <= 0:
            raise ValueError("num_positions must be positive")

        indicator_values = self._resolve_cell_indicator_values(valid_indicator)
        centers = self._collect_cell_centers(indicator_values)
        if not centers:
            raise ValueError(f"No cells found for indicator {valid_indicator!r}")

        if num_positions > len(centers):
            selected = random.choices(centers, k=num_positions)
        else:
            selected = random.sample(centers, num_positions)

        margin = min(0.45 * self.cell_size, 0.5)
        delta = max(0.0, 0.5 * self.cell_size - margin)
        points: list[list[float]] = []
        for cx, cy in selected:
            px = cx + random.uniform(-delta, delta)
            py = cy + random.uniform(-delta, delta)
            points.append([px, py, 0.0])
        return np.asarray(points, dtype=np.float32)

    def get_indicator_positions(self, valid_indicator: int | str) -> np.ndarray:
        indicator_values = self._resolve_cell_indicator_values(valid_indicator)
        centers = self._collect_cell_centers(indicator_values)
        if not centers:
            return np.empty((0, 3), dtype=np.float32)
        return np.asarray([[x, y, 0.0] for x, y in centers], dtype=np.float32)

    def get_wall_indices_by_indicator(
        self, indicators: int | str | Sequence[int | str]
    ) -> list[int]:
        if isinstance(indicators, (int, str)):
            values = self._resolve_wall_indicator_values(indicators)
        else:
            values = set()
            for indicator in indicators:
                values.update(self._resolve_wall_indicator_values(indicator))
            values = frozenset(values)

        if self._wall_segment_values.size == 0:
            return []
        mask = np.isin(self._wall_segment_values, np.fromiter(values, dtype=np.int64))
        return np.flatnonzero(mask).astype(int).tolist()

    def get_wall_distances(self, robot_positions: np.ndarray) -> np.ndarray:
        points = np.asarray(robot_positions, dtype=np.float64)
        if points.ndim != 2 or points.shape[1] < 2:
            raise ValueError(
                "robot_positions must have shape (N, 2) or (N, >=2) for wall distance queries."
            )

        if self._wall_segments.size == 0:
            return np.full((points.shape[0],), np.inf, dtype=np.float64)

        robot_xy = points[:, :2]
        segments = self._wall_segments.astype(np.float64, copy=False)
        seg_start = segments[:, :2][None, :, :]
        seg_end = segments[:, 2:][None, :, :]
        seg_vec = seg_end - seg_start
        robot_pts = robot_xy[:, None, :]
        robot_to_start = robot_pts - seg_start

        seg_len_sq = np.sum(seg_vec * seg_vec, axis=2)
        seg_len_sq = np.maximum(seg_len_sq, 1.0e-12)

        t = np.sum(robot_to_start * seg_vec, axis=2) / seg_len_sq
        t = np.clip(t, 0.0, 1.0)

        closest = seg_start + t[:, :, None] * seg_vec
        dists = np.linalg.norm(robot_pts - closest, axis=2)
        return np.min(dists, axis=1)

    def get_wall_distances_torch(self, robot_positions: torch.Tensor) -> torch.Tensor:
        import torch

        if robot_positions.ndim != 2 or robot_positions.shape[1] < 2:
            raise ValueError(
                "robot_positions must have shape (N, 2) or (N, >=2) for wall distance queries."
            )

        if self._wall_segments.size == 0:
            return torch.full(
                (robot_positions.shape[0],),
                float("inf"),
                dtype=torch.float32,
                device=robot_positions.device,
            )

        if (
            self._wall_segments_torch is None
            or self._torch_device != robot_positions.device
        ):
            self.update_torch_device(robot_positions.device)

        robot_xy = robot_positions[:, :2]
        segments = self._wall_segments_torch

        seg_start = segments[:, :2].unsqueeze(0)
        seg_end = segments[:, 2:].unsqueeze(0)
        seg_vec = seg_end - seg_start

        robot_pts = robot_xy.unsqueeze(1)
        robot_to_start = robot_pts - seg_start

        seg_len_sq = torch.sum(seg_vec * seg_vec, dim=2)
        seg_len_sq = torch.clamp(seg_len_sq, min=1.0e-12)

        t = torch.sum(robot_to_start * seg_vec, dim=2) / seg_len_sq
        t = torch.clamp(t, min=0.0, max=1.0)

        closest = seg_start + t.unsqueeze(2) * seg_vec
        dists = torch.norm(robot_pts - closest, dim=2)
        return torch.min(dists, dim=1)[0]

    def get_random_valid_positions_torch(
        self,
        num_positions: int,
        valid_indicator: int | str = 0,
        device: str | torch.device | None = None,
    ) -> torch.Tensor:
        import torch

        points = self.get_random_valid_positions(
            num_positions,
            valid_indicator=valid_indicator,
        )
        out_device = torch.device("cpu") if device is None else torch.device(device)
        return torch.tensor(points, dtype=torch.float32, device=out_device)

    def get_indicator_positions_torch(
        self,
        valid_indicator: int | str,
        device: str | torch.device | None = None,
    ) -> torch.Tensor:
        import torch

        points = self.get_indicator_positions(valid_indicator)
        out_device = torch.device("cpu") if device is None else torch.device(device)
        return torch.tensor(points, dtype=torch.float32, device=out_device)

    def _build_wall_segments_for_values(
        self, wall_values: frozenset[int]
    ) -> MazeSegmentSet:
        raise NotImplementedError

    def _collect_all_wall_values(self) -> frozenset[int]:
        all_values: set[int] = set()
        for values in self._wall_values_by_name.values():
            all_values.update(int(value) for value in values)
        return frozenset(all_values)

    def _default_wall_values(self) -> frozenset[int]:
        values: set[int] = set()
        for element in self.runtime.maze.config.wall_elements.elements():
            name = str(element.name).strip().lower()
            value = int(element.value)
            if name in {"open", "empty"}:
                continue
            if value == 0:
                continue
            values.add(value)
        if values:
            return frozenset(values)
        return frozenset(value for value in self._all_wall_values if value != 0)

    def _resolve_wall_values(
        self, wall_semantics: SpatialWallSemantics | None
    ) -> frozenset[int]:
        default_values = set(self._default_wall_values())
        if wall_semantics is None:
            if not default_values:
                raise ValueError("No wall values resolved from default semantics.")
            return frozenset(default_values)

        selected: set[int] = (
            set(default_values) if wall_semantics.seed_with_default_walls else set()
        )

        if wall_semantics.include_all:
            selected.update(self._all_wall_values)
        selected.update(
            self._resolve_values_by_names(
                wall_semantics.include_names,
                by_name=self._wall_values_by_name,
                kind="wall",
            )
        )
        selected.update(
            self._resolve_values_by_tokens(
                wall_semantics.include_tokens,
                by_token=self._wall_values_by_token,
                kind="wall",
            )
        )
        selected.update(
            self._resolve_values_by_int(
                wall_semantics.include_values,
                valid_values=self._all_wall_values,
                kind="wall",
            )
        )

        selected.difference_update(
            self._resolve_values_by_names(
                wall_semantics.exclude_names,
                by_name=self._wall_values_by_name,
                kind="wall",
            )
        )
        selected.difference_update(
            self._resolve_values_by_tokens(
                wall_semantics.exclude_tokens,
                by_token=self._wall_values_by_token,
                kind="wall",
            )
        )
        selected.difference_update(
            self._resolve_values_by_int(
                wall_semantics.exclude_values,
                valid_values=self._all_wall_values,
                kind="wall",
            )
        )

        if not selected:
            raise ValueError("No wall values resolved from provided SpatialWallSemantics.")
        return frozenset(selected)

    def _resolve_values_by_names(
        self,
        names: Sequence[str],
        *,
        by_name: Mapping[str, frozenset[int]],
        kind: str,
    ) -> frozenset[int]:
        values: set[int] = set()
        for name in names:
            key = str(name).strip().lower()
            if not key:
                raise ValueError(f"{kind} name selector cannot be empty.")
            matched = by_name.get(key)
            if matched is None:
                raise ValueError(f"Unknown {kind} name selector: {name!r}")
            values.update(int(value) for value in matched)
        return frozenset(values)

    def _resolve_values_by_tokens(
        self,
        tokens: Sequence[str],
        *,
        by_token: Mapping[str, frozenset[int]],
        kind: str,
    ) -> frozenset[int]:
        values: set[int] = set()
        for token in tokens:
            key = str(token).strip()
            if not key:
                raise ValueError(f"{kind} token selector cannot be empty.")
            matched = by_token.get(key)
            if matched is None:
                matched = by_token.get(key.lower())
            if matched is None:
                raise ValueError(f"Unknown {kind} token selector: {token!r}")
            values.update(int(value) for value in matched)
        return frozenset(values)

    def _resolve_values_by_int(
        self,
        raw_values: Sequence[int],
        *,
        valid_values: frozenset[int],
        kind: str,
    ) -> frozenset[int]:
        values: set[int] = set()
        for raw in raw_values:
            value = int(raw)
            if value not in valid_values:
                raise ValueError(f"Unknown {kind} value selector: {value!r}")
            values.add(value)
        return frozenset(values)

    def _collect_cell_centers(
        self, indicator_values: frozenset[int]
    ) -> list[tuple[float, float]]:
        centers: list[tuple[float, float]] = []
        for row in range(self.rows):
            for col in range(self.cols):
                value = int(self._cells[row][col])
                if value not in indicator_values:
                    continue
                x = self._cell_center_offset_xy[0] + col * self.cell_size
                y = self._cell_center_offset_xy[1] + row * self.cell_size
                centers.append((x, y))
        return centers

    def _resolve_indicator_values(
        self,
        indicator: int | str,
        *,
        by_name: Mapping[str, frozenset[int]],
        by_token: Mapping[str, frozenset[int]],
        kind: str,
    ) -> frozenset[int]:
        if isinstance(indicator, int):
            return frozenset((indicator,))
        if not isinstance(indicator, str):
            raise TypeError(f"{kind} indicator must be int or str, got {type(indicator)}")

        key = indicator.strip()
        if not key:
            raise ValueError(f"{kind} indicator cannot be empty")

        if key.lstrip("+-").isdigit():
            return frozenset((int(key),))

        token_values = by_token.get(key)
        if token_values is not None:
            return token_values

        name_values = by_name.get(key.lower())
        if name_values is not None:
            return name_values

        raise ValueError(f"Unknown {kind} indicator: {indicator!r}")

    def _resolve_cell_indicator_values(self, indicator: int | str) -> frozenset[int]:
        return self._resolve_indicator_values(
            indicator,
            by_name=self._cell_values_by_name,
            by_token=self._cell_values_by_token,
            kind="cell",
        )

    def _resolve_wall_indicator_values(self, indicator: int | str) -> frozenset[int]:
        return self._resolve_indicator_values(
            indicator,
            by_name=self._wall_values_by_name,
            by_token=self._wall_values_by_token,
            kind="wall",
        )


class EdgeGridSpatialRuntime(BaseSpatialRuntime):
    expected_maze_type = "edge_grid"

    def _build_wall_segments_for_values(
        self, wall_values: frozenset[int]
    ) -> MazeSegmentSet:
        vertical = np.asarray(self.runtime.maze.layout.vertical_walls, dtype=np.int64)
        horizontal = np.asarray(self.runtime.maze.layout.horizontal_walls, dtype=np.int64)

        if vertical.shape != (self.rows, self.cols + 1):
            raise ValueError(
                "Invalid edge_grid vertical wall shape: "
                f"expected {(self.rows, self.cols + 1)}, got {vertical.shape}."
            )
        if horizontal.shape != (self.rows + 1, self.cols):
            raise ValueError(
                "Invalid edge_grid horizontal wall shape: "
                f"expected {(self.rows + 1, self.cols)}, got {horizontal.shape}."
            )

        ox, oy = self.origin_xy
        segments: list[list[float]] = []
        values: list[int] = []

        for row in range(self.rows):
            y0 = oy + row * self.cell_size
            y1 = y0 + self.cell_size
            for col in range(self.cols + 1):
                value = int(vertical[row, col])
                if value not in wall_values:
                    continue
                x = ox + col * self.cell_size
                segments.append([x, y0, x, y1])
                values.append(value)

        for row in range(self.rows + 1):
            y = oy + row * self.cell_size
            for col in range(self.cols):
                value = int(horizontal[row, col])
                if value not in wall_values:
                    continue
                x0 = ox + col * self.cell_size
                x1 = x0 + self.cell_size
                segments.append([x0, y, x1, y])
                values.append(value)

        if not segments:
            return MazeSegmentSet(
                segments=np.empty((0, 4), dtype=np.float32),
                values=np.empty((0,), dtype=np.int32),
            )
        return MazeSegmentSet(
            segments=np.asarray(segments, dtype=np.float32),
            values=np.asarray(values, dtype=np.int32),
        )


class OccupancyGridSpatialRuntime(BaseSpatialRuntime):
    expected_maze_type = "occupancy_grid"

    def _build_wall_segments_for_values(
        self, wall_values: frozenset[int]
    ) -> MazeSegmentSet:
        grid = self._cells
        if grid.shape != (self.rows, self.cols):
            raise ValueError(
                f"Invalid occupancy_grid shape: expected {(self.rows, self.cols)}, got {grid.shape}."
            )

        ox, oy = self.origin_xy
        segments: list[list[float]] = []
        values: list[int] = []

        for row in range(self.rows):
            y0 = oy + row * self.cell_size
            y1 = y0 + self.cell_size
            for col in range(self.cols):
                value = int(grid[row, col])
                if value not in wall_values:
                    continue

                x0 = ox + col * self.cell_size
                x1 = x0 + self.cell_size

                if col == 0 or int(grid[row, col - 1]) not in wall_values:
                    segments.append([x0, y0, x0, y1])
                    values.append(value)
                if col == self.cols - 1 or int(grid[row, col + 1]) not in wall_values:
                    segments.append([x1, y0, x1, y1])
                    values.append(value)
                if row == 0 or int(grid[row - 1, col]) not in wall_values:
                    segments.append([x0, y0, x1, y0])
                    values.append(value)
                if row == self.rows - 1 or int(grid[row + 1, col]) not in wall_values:
                    segments.append([x0, y1, x1, y1])
                    values.append(value)

        if not segments:
            return MazeSegmentSet(
                segments=np.empty((0, 4), dtype=np.float32),
                values=np.empty((0,), dtype=np.int32),
            )
        return MazeSegmentSet(
            segments=np.asarray(segments, dtype=np.float32),
            values=np.asarray(values, dtype=np.int32),
        )


def create_spatial_runtime(
    runtime: MazeRuntime,
    *,
    origin_xy: tuple[float, float] | None = None,
    wall_semantics: SpatialWallSemantics | None = None,
) -> BaseSpatialRuntime:
    if runtime.maze_type == "edge_grid":
        return EdgeGridSpatialRuntime(
            runtime,
            origin_xy=origin_xy,
            wall_semantics=wall_semantics,
        )
    if runtime.maze_type == "occupancy_grid":
        return OccupancyGridSpatialRuntime(
            runtime,
            origin_xy=origin_xy,
            wall_semantics=wall_semantics,
        )
    raise ValueError(
        "Spatial runtime supports only 'edge_grid' and 'occupancy_grid'; "
        f"got {runtime.maze_type!r}."
    )


class MazeSpatialRuntime:
    def __new__(
        cls,
        runtime: MazeRuntime,
        *,
        origin_xy: tuple[float, float] | None = None,
        wall_semantics: SpatialWallSemantics | None = None,
    ) -> BaseSpatialRuntime:
        return create_spatial_runtime(
            runtime,
            origin_xy=origin_xy,
            wall_semantics=wall_semantics,
        )

    @classmethod
    def from_maze(
        cls,
        maze: Maze,
        *,
        origin_xy: tuple[float, float] | None = None,
        wall_semantics: SpatialWallSemantics | None = None,
    ) -> BaseSpatialRuntime:
        return create_spatial_runtime(
            MazeRuntime.from_maze(maze),
            origin_xy=origin_xy,
            wall_semantics=wall_semantics,
        )
