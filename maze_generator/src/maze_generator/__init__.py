"""Public API for maze_generator."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from py_ant_maze import Maze

from .maze_geometry.extractor import extract_geometry
from .maze_materials.color import MaterialMap
from .maze_materials.discovery import (
    discover_all_default_materials,
    discover_default_materials,
    get_default_assets_path,
)
from .maze_materials.source import MaterialSource, UsdMaterialRef
from .maze_usd.writer import write_usd

__all__ = [
    "MaterialSource",
    "UsdMaterialRef",
    "discover_all_default_materials",
    "discover_default_materials",
    "get_default_assets_path",
    "maze_to_usd",
]


def maze_to_usd(
    maze_or_path: Maze | str | Path,
    output_path: str,
    *,
    merge: bool = False,
    material_map: MaterialMap | None = None,
    material_source: MaterialSource | None = None,
) -> str:
    maze = _coerce_maze(maze_or_path)
    if material_source is not None and not isinstance(material_source, MaterialSource):
        raise TypeError("material_source must be MaterialSource")
    resolved_material_source = material_source
    if resolved_material_source is None:
        resolved_material_source = discover_default_materials(allow_empty=True)

    geometry = extract_geometry(maze)
    write_usd(
        geometry,
        output_path,
        merge=merge,
        material_map=material_map,
        material_source=resolved_material_source,
    )
    return str(Path(output_path).resolve())


def _coerce_maze(maze_or_path: Any):
    if isinstance(maze_or_path, Maze):
        return maze_or_path
    if isinstance(maze_or_path, (str, Path)):
        maze_path = Path(maze_or_path)
        if not maze_path.is_file():
            raise FileNotFoundError(f"Maze file not found: {maze_path}")
        return Maze.from_file(str(maze_path))
    raise TypeError("maze_or_path must be a py_ant_maze.Maze instance or a path")
