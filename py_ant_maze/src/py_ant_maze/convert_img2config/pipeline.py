"""Public image-to-YAML conversion pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Union

from ..maze import Maze

from .grid_estimator import estimate_grid
from .image_io import crop_to_content, load_rgb_image
from .models import SUPPORTED_MAZE_TYPES
from .reconstruction import reconstruct_maze
from .yaml_builder import to_yaml_text


def infer_maze_yaml_from_image(image_path: Union[str, Path], *, maze_type: str = "auto") -> str:
    if maze_type not in SUPPORTED_MAZE_TYPES:
        raise ValueError(f"maze_type must be one of: {', '.join(SUPPORTED_MAZE_TYPES)}")

    image = load_rgb_image(image_path)
    content = crop_to_content(image)
    estimate = estimate_grid(content, maze_type=maze_type)
    reconstruction = reconstruct_maze(content, estimate)
    yaml_text = to_yaml_text(reconstruction)

    Maze.from_text(yaml_text)
    return yaml_text


def image_to_yaml_file(
    image_path: Union[str, Path],
    output_path: Union[str, Path],
    *,
    maze_type: str = "auto",
) -> str:
    yaml_text = infer_maze_yaml_from_image(image_path, maze_type=maze_type)
    output = Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(yaml_text, encoding="utf-8")
    if not output.is_file():
        raise RuntimeError(f"Failed to write maze YAML: {output}")
    return str(output)
