"""Grid shape and maze-type estimation from an RGB image crop."""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from .models import GridEstimate, SUPPORTED_MAZE_TYPES


def estimate_grid(image: np.ndarray, *, maze_type: str = "auto") -> GridEstimate:
    if maze_type not in SUPPORTED_MAZE_TYPES:
        raise ValueError(f"Unsupported maze_type: {maze_type!r}")
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("image must be an RGB array")

    gradient_x = _gradient_profile_x(image)
    gradient_y = _gradient_profile_y(image)
    period_x = _estimate_period(gradient_x)
    period_y = _estimate_period(gradient_y)
    cols = _estimate_count(image.shape[1], period_x)
    rows = _estimate_count(image.shape[0], period_y)

    resolved_type = maze_type
    if maze_type == "auto":
        resolved_type = _infer_maze_type(image, rows, cols)

    return GridEstimate(
        maze_type=resolved_type,
        rows=rows,
        cols=cols,
        period_x=period_x,
        period_y=period_y,
    )


def _gradient_profile_x(image: np.ndarray) -> np.ndarray:
    diff = np.abs(np.diff(image, axis=1))
    return np.mean(diff, axis=(0, 2))


def _gradient_profile_y(image: np.ndarray) -> np.ndarray:
    diff = np.abs(np.diff(image, axis=0))
    return np.mean(diff, axis=(1, 2))


def _estimate_period(signal: np.ndarray) -> float:
    if signal.size < 10:
        raise ValueError("Image is too small for period estimation")
    period_from_peaks = _period_from_peak_clusters(_peak_positions(signal))
    if period_from_peaks is not None:
        return period_from_peaks

    smoothed = _smooth_signal(signal)
    centered = smoothed - float(np.mean(smoothed))
    if np.allclose(centered, 0.0):
        raise ValueError("Insufficient signal variation for period estimation")

    autocorrelation = np.correlate(centered, centered, mode="full")[centered.size - 1 :]
    min_period = max(4, centered.size // 200)
    max_period = min(centered.size // 2, 220)
    if max_period <= min_period:
        raise ValueError("Cannot estimate period from the provided signal")

    lags = np.arange(min_period, max_period + 1, dtype=np.int32)
    scores = autocorrelation[min_period : max_period + 1] / np.sqrt(lags)
    best_lag = int(lags[int(np.argmax(scores))])
    return float(best_lag)


def _smooth_signal(signal: np.ndarray) -> np.ndarray:
    window = max(5, (signal.size // 80) | 1)
    if window >= signal.size:
        window = max(3, (signal.size // 2) | 1)
    kernel = np.ones(window, dtype=np.float32) / float(window)
    return np.convolve(signal, kernel, mode="same")


def _estimate_count(length: int, period: float) -> int:
    if period <= 0:
        raise ValueError("period must be positive")
    return max(1, int(round(length / period)))


def _period_from_peak_clusters(peaks: np.ndarray) -> Optional[float]:
    if peaks.size < 2:
        return None
    cluster_gap = 5
    clusters: List[List[int]] = [[int(peaks[0])]]
    for peak in peaks[1:]:
        value = int(peak)
        if value - clusters[-1][-1] <= cluster_gap:
            clusters[-1].append(value)
        else:
            clusters.append([value])
    if len(clusters) < 2:
        return None
    centers = np.asarray([sum(cluster) / len(cluster) for cluster in clusters], dtype=np.float32)
    intervals = np.diff(centers)
    intervals = intervals[intervals >= 4]
    if intervals.size == 0:
        return None
    return float(np.median(intervals))


def _infer_maze_type(image: np.ndarray, rows: int, cols: int) -> str:
    cell_luminance = _sample_cell_luminance(image, rows, cols)
    threshold = _binary_threshold(cell_luminance.reshape(-1))
    dark_ratio = float(np.mean(cell_luminance <= threshold))
    if dark_ratio < 0.08:
        return "edge_grid"
    return "occupancy_grid"


def _peak_positions(signal: np.ndarray) -> np.ndarray:
    smoothed = _smooth_signal(signal)
    threshold = float(np.percentile(smoothed, 92))
    min_distance = max(2, smoothed.size // 300)
    peaks: List[int] = []

    for index in range(1, smoothed.size - 1):
        value = smoothed[index]
        if value < threshold:
            continue
        if value < smoothed[index - 1] or value < smoothed[index + 1]:
            continue
        if peaks and index - peaks[-1] < min_distance:
            if value > smoothed[peaks[-1]]:
                peaks[-1] = index
            continue
        peaks.append(index)

    return np.asarray(peaks, dtype=np.int32)


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
    luminance = patch[..., 0] * 0.2126 + patch[..., 1] * 0.7152 + patch[..., 2] * 0.0722
    return float(np.mean(luminance))


def _binary_threshold(values: np.ndarray) -> float:
    low = float(np.percentile(values, 20))
    high = float(np.percentile(values, 80))
    if high - low < 6.0:
        return low - 1.0
    return (low + high) * 0.5
