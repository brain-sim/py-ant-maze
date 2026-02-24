"""Public API for maze_generator."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from py_ant_maze import Maze

from .export_options import ExportOptions
from .maze_geometry.extractor import extract_geometry
from .maze_materials.color import MaterialMap
from .maze_materials.discovery import (
    discover_all_default_materials,
    discover_default_materials,
    get_default_assets_path,
)
from .maze_materials.source import MaterialSource, UsdMaterialRef
from .maze_obj.writer import write_obj_bundle
from .maze_usd.writer import write_usd

__all__ = [
    "ExportOptions",
    "MaterialSource",
    "UsdMaterialRef",
    "discover_all_default_materials",
    "discover_default_materials",
    "get_default_assets_path",
    "maze_to_obj",
    "maze_to_usd",
]


def maze_to_usd(
    maze_or_path: Maze | str | Path,
    output_path: str,
    *,
    export_options: ExportOptions | None = None,
    material_map: MaterialMap | None = None,
    material_source: MaterialSource | None = None,
) -> str:
    maze = _coerce_maze(maze_or_path)
    resolved_export_options = _resolve_export_options(export_options)
    resolved_material_source = _resolve_material_source(material_source)

    geometry = extract_geometry(maze)
    geometry = resolved_export_options.apply_to_geometry(geometry)
    write_usd(
        geometry,
        output_path,
        material_map=material_map,
        material_source=resolved_material_source,
    )
    return str(Path(output_path).resolve())


def maze_to_obj(
    maze_or_path: Maze | str | Path,
    output_dir: str,
    *,
    export_options: ExportOptions | None = None,
    material_map: MaterialMap | None = None,
    material_source: MaterialSource | None = None,
) -> str:
    maze = _coerce_maze(maze_or_path)
    resolved_export_options = _resolve_export_options(export_options)
    resolved_material_source = _resolve_material_source(material_source)

    geometry = extract_geometry(maze)
    geometry = resolved_export_options.apply_to_geometry(geometry)
    write_obj_bundle(
        geometry,
        output_dir,
        material_map=material_map,
        material_source=resolved_material_source,
    )
    return str(Path(output_dir).resolve())


def _coerce_maze(maze_or_path: Any):
    if isinstance(maze_or_path, Maze):
        return maze_or_path
    if isinstance(maze_or_path, (str, Path)):
        maze_path = Path(maze_or_path)
        if not maze_path.is_file():
            raise FileNotFoundError(f"Maze file not found: {maze_path}")
        return Maze.from_file(str(maze_path))
    raise TypeError("maze_or_path must be a py_ant_maze.Maze instance or a path")


def _resolve_material_source(material_source: MaterialSource | None) -> MaterialSource:
    if material_source is not None and not isinstance(material_source, MaterialSource):
        raise TypeError("material_source must be MaterialSource")
    if material_source is None:
        return discover_default_materials(allow_empty=True)
    return material_source


def _resolve_export_options(export_options: ExportOptions | None) -> ExportOptions:
    if export_options is None:
        return ExportOptions()
    if not isinstance(export_options, ExportOptions):
        raise TypeError("export_options must be ExportOptions")
    return export_options
