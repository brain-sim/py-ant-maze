"""Image loading and foreground extraction utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Union

import numpy as np
from PIL import Image


def load_rgb_image(image_path: Union[str, Path]) -> np.ndarray:
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"Image file not found: {path}")
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        array = np.asarray(rgb, dtype=np.float32)
    if array.ndim != 3 or array.shape[2] != 3:
        raise ValueError(f"Invalid RGB image array shape: {array.shape}")
    return array


def crop_to_content(
    image: np.ndarray,
    *,
    distance_threshold: float = 18.0,
    padding: int = 2,
) -> np.ndarray:
    if distance_threshold <= 0:
        raise ValueError("distance_threshold must be positive")
    if padding < 0:
        raise ValueError("padding must be >= 0")
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("image must be an RGB array")

    background_color = estimate_background_color(image)
    distance = np.linalg.norm(image - background_color, axis=2)
    mask = distance > distance_threshold
    if not np.any(mask):
        raise ValueError("Unable to find maze content in image")

    ys, xs = np.where(mask)
    y0 = max(0, int(np.min(ys)) - padding)
    y1 = min(image.shape[0] - 1, int(np.max(ys)) + padding)
    x0 = max(0, int(np.min(xs)) - padding)
    x1 = min(image.shape[1] - 1, int(np.max(xs)) + padding)
    cropped = image[y0 : y1 + 1, x0 : x1 + 1]
    if cropped.size == 0:
        raise ValueError("Content crop is empty")
    return cropped


def estimate_background_color(image: np.ndarray) -> np.ndarray:
    height, width, _ = image.shape
    patch = max(1, min(height, width) // 30)
    top_left = image[:patch, :patch].reshape(-1, 3)
    top_right = image[:patch, width - patch :].reshape(-1, 3)
    bottom_left = image[height - patch :, :patch].reshape(-1, 3)
    bottom_right = image[height - patch :, width - patch :].reshape(-1, 3)
    corners = np.concatenate((top_left, top_right, bottom_left, bottom_right), axis=0)
    return np.median(corners, axis=0)
