from typing import Dict, Tuple, Type, TypeAlias

from ..mazes.occupancy_grid import OccupancyGridConfig, OccupancyGridLayout
from ..mazes.edge_grid import EdgeGridConfig, EdgeGridLayout
from ..mazes.radial_arm import RadialArmConfig, RadialArmLayout
from .types import MazeType


ConfigType = Type[object]
LayoutType = Type[object]
MazeTypes: TypeAlias = Tuple[ConfigType, LayoutType]
MazeRegistry: TypeAlias = Dict[MazeType, MazeTypes]


MAZE_REGISTRY: MazeRegistry = {
    "occupancy_grid": (OccupancyGridConfig, OccupancyGridLayout),
    "edge_grid": (EdgeGridConfig, EdgeGridLayout),
    "radial_arm": (RadialArmConfig, RadialArmLayout),
}


def get_types(maze_type: MazeType) -> MazeTypes:
    try:
        return MAZE_REGISTRY[maze_type]
    except KeyError as exc:
        raise KeyError(f"unknown maze_type: {maze_type}") from exc
