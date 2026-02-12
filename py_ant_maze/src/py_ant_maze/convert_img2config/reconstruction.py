"""Maze layout reconstruction from inferred grid geometry."""

from __future__ import annotations

import numpy as np

from .models import GridEstimate, MazeReconstruction


def reconstruct_maze(image: np.ndarray, estimate: GridEstimate) -> MazeReconstruction:
    if estimate.maze_type == "occupancy_grid":
        return _reconstruct_occupancy_grid(image, estimate.rows, estimate.cols)
    if estimate.maze_type == "edge_grid":
        return _reconstruct_edge_grid(image, estimate.rows, estimate.cols)
    raise ValueError(f"Unsupported maze type in estimate: {estimate.maze_type}")


def _reconstruct_occupancy_grid(image: np.ndarray, rows: int, cols: int) -> MazeReconstruction:
    cell_luminance = _sample_cell_luminance(image, rows, cols)
    threshold = _binary_threshold(cell_luminance.reshape(-1))
    grid = (cell_luminance <= threshold).astype(np.int32).tolist()
    return MazeReconstruction(
        maze_type="occupancy_grid",
        rows=rows,
        cols=cols,
        occupancy_grid=grid,
    )


def _reconstruct_edge_grid(image: np.ndarray, rows: int, cols: int) -> MazeReconstruction:
    cell_luminance = _sample_cell_luminance(image, rows, cols)
    vertical_luminance = _sample_vertical_wall_luminance(image, rows, cols)
    horizontal_luminance = _sample_horizontal_wall_luminance(image, rows, cols)

    cell_threshold = _binary_threshold(cell_luminance.reshape(-1))
    wall_threshold = _binary_threshold(
        np.concatenate((vertical_luminance.reshape(-1), horizontal_luminance.reshape(-1)), axis=0)
    )

    cells = (cell_luminance <= cell_threshold).astype(np.int32).tolist()
    vertical_walls = (vertical_luminance <= wall_threshold).astype(np.int32).tolist()
    horizontal_walls = (horizontal_luminance <= wall_threshold).astype(np.int32).tolist()

    return MazeReconstruction(
        maze_type="edge_grid",
        rows=rows,
        cols=cols,
        cells=cells,
        vertical_walls=vertical_walls,
        horizontal_walls=horizontal_walls,
    )


def _sample_cell_luminance(image: np.ndarray, rows: int, cols: int) -> np.ndarray:
    height, width, _ = image.shape
    y_step = height / rows
    x_step = width / cols
    radius = max(1, int(min(y_step, x_step) * 0.14))
    samples = np.zeros((rows, cols), dtype=np.float32)

    for row in range(rows):
        y = (row + 0.5) * y_step - 0.5
        for col in range(cols):
            x = (col + 0.5) * x_step - 0.5
            samples[row, col] = _sample_patch_luminance(image, y, x, radius)
    return samples


def _sample_vertical_wall_luminance(image: np.ndarray, rows: int, cols: int) -> np.ndarray:
    height, width, _ = image.shape
    y_step = height / rows
    x_step = width / cols
    radius = max(1, int(min(y_step, x_step) * 0.08))
    samples = np.zeros((rows, cols + 1), dtype=np.float32)

    for row in range(rows):
        y = (row + 0.5) * y_step - 0.5
        for col in range(cols + 1):
            x = col * x_step
            samples[row, col] = _sample_patch_luminance(image, y, x, radius)
    return samples


def _sample_horizontal_wall_luminance(image: np.ndarray, rows: int, cols: int) -> np.ndarray:
    height, width, _ = image.shape
    y_step = height / rows
    x_step = width / cols
    radius = max(1, int(min(y_step, x_step) * 0.08))
    samples = np.zeros((rows + 1, cols), dtype=np.float32)

    for row in range(rows + 1):
        y = row * y_step
        for col in range(cols):
            x = (col + 0.5) * x_step - 0.5
            samples[row, col] = _sample_patch_luminance(image, y, x, radius)
    return samples


def _sample_patch_luminance(image: np.ndarray, y: float, x: float, radius: int) -> float:
    y_index = int(round(y))
    x_index = int(round(x))
    y0 = max(0, y_index - radius)
    y1 = min(image.shape[0], y_index + radius + 1)
    x0 = max(0, x_index - radius)
    x1 = min(image.shape[1], x_index + radius + 1)
    patch = image[y0:y1, x0:x1]
    if patch.size == 0:
        raise ValueError("Failed to sample luminance patch")
    luminance = _rgb_to_luminance(patch)
    return float(np.mean(luminance))


def _rgb_to_luminance(values: np.ndarray) -> np.ndarray:
    return values[..., 0] * 0.2126 + values[..., 1] * 0.7152 + values[..., 2] * 0.0722


def _binary_threshold(values: np.ndarray) -> float:
    if values.size == 0:
        raise ValueError("Cannot compute threshold from empty values")
    low = float(np.percentile(values, 20))
    high = float(np.percentile(values, 80))
    if high - low < 6.0:
        return low - 1.0
    return (low + high) * 0.5
