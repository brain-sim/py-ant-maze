"""Generate USD files from py-ant-maze configurations."""

from .types import WallBox, MazeGeometry
from .geometry import extract_geometry
from .usd_writer import write_usd

__all__ = [
    "WallBox",
    "MazeGeometry",
    "extract_geometry",
    "write_usd",
    "maze_to_usd",
]
__version__ = "0.1.0"


def maze_to_usd(
    maze_or_path,
    output_path: str,
    *,
    merge: bool = False,
    material_map=None,
) -> str:
    """Load a maze and write a USD file.

    Physical dimensions (cell_size, wall_height, wall_thickness)
    are read from the maze's config section in the YAML.

    Args:
        maze_or_path: A py_ant_maze.Maze object or a path to a YAML file.
        output_path: Where to write the .usda file.
        merge: If True, merge all walls sharing the same element_name
            into one mesh.
        material_map: Optional dict mapping element_name -> (r, g, b) color.

    Returns:
        The output path.
    """
    from py_ant_maze import Maze

    if isinstance(maze_or_path, (str,)):
        maze = Maze.from_file(maze_or_path)
    else:
        maze = maze_or_path

    geometry = extract_geometry(maze)
    write_usd(geometry, output_path, merge=merge, material_map=material_map)
    return output_path
