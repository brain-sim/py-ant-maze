"""Public config-to-image conversion pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Union

from PIL import Image

from ..maze import Maze, MazeDraft
from .renderer import MazeConfigImageRenderer

PathLike = Union[str, Path]

_SUFFIX_TO_FORMAT: Dict[str, str] = {
    ".png": "PNG",
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".bmp": "BMP",
    ".tif": "TIFF",
    ".tiff": "TIFF",
    ".webp": "WEBP",
}


def maze_to_image(
    maze: Maze | MazeDraft,
    *,
    renderer: MazeConfigImageRenderer | None = None,
) -> Image.Image:
    active_renderer = renderer or MazeConfigImageRenderer()
    return active_renderer.render(maze)


def config_text_to_image(
    yaml_text: str,
    *,
    renderer: MazeConfigImageRenderer | None = None,
) -> Image.Image:
    maze = Maze.from_text(yaml_text)
    return maze_to_image(maze, renderer=renderer)


def config_file_to_image(
    config_path: PathLike,
    output_path: PathLike,
    *,
    image_format: str | None = None,
    renderer: MazeConfigImageRenderer | None = None,
) -> str:
    maze = Maze.from_file(str(config_path))
    return maze_to_image_file(
        maze,
        output_path,
        image_format=image_format,
        renderer=renderer,
    )


def maze_to_image_file(
    maze: Maze | MazeDraft,
    output_path: PathLike,
    *,
    image_format: str | None = None,
    renderer: MazeConfigImageRenderer | None = None,
) -> str:
    image = maze_to_image(maze, renderer=renderer)
    output = Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    resolved_format = _resolve_image_format(output, image_format=image_format)
    image.save(output, format=resolved_format)

    if not output.is_file():
        raise RuntimeError(f"Failed to write image file: {output}")
    return str(output)


def _resolve_image_format(output_path: Path, *, image_format: str | None) -> str:
    if image_format is not None:
        normalized = image_format.strip().upper()
        if not normalized:
            raise ValueError("image_format cannot be empty")
        return normalized

    suffix = output_path.suffix.lower()
    if suffix == "":
        return "PNG"
    if suffix not in _SUFFIX_TO_FORMAT:
        supported = ", ".join(sorted(_SUFFIX_TO_FORMAT.keys()))
        raise ValueError(
            f"Unsupported output file extension: {suffix}. "
            f"Set image_format explicitly or use one of: {supported}"
        )
    return _SUFFIX_TO_FORMAT[suffix]
