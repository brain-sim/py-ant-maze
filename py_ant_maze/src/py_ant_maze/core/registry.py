from typing import Dict, Tuple, Type, TypeAlias

from ..mazes.occupancy_grid import OccupancyGridConfig, OccupancyGridLayout
from ..mazes.edge_grid import EdgeGridConfig, EdgeGridLayout
from ..mazes.radial_arm import RadialArmConfig, RadialArmLayout
from ..mazes.occupancy_grid_3d import OccupancyGrid3DConfig, OccupancyGrid3DLayout
from ..mazes.edge_grid_3d import EdgeGrid3DConfig, EdgeGrid3DLayout
from ..mazes.radial_arm_3d import RadialArm3DConfig, RadialArm3DLayout
from .types import MazeType


ConfigType = Type[object]
LayoutType = Type[object]
MazeTypes: TypeAlias = Tuple[ConfigType, LayoutType]
MazeRegistry: TypeAlias = Dict[MazeType, MazeTypes]


MAZE_REGISTRY: MazeRegistry = {
    "occupancy_grid": (OccupancyGridConfig, OccupancyGridLayout),
    "edge_grid": (EdgeGridConfig, EdgeGridLayout),
    "radial_arm": (RadialArmConfig, RadialArmLayout),
    "occupancy_grid_2d": (OccupancyGridConfig, OccupancyGridLayout),
    "edge_grid_2d": (EdgeGridConfig, EdgeGridLayout),
    "radial_arm_2d": (RadialArmConfig, RadialArmLayout),
    "occupancy_grid_3d": (OccupancyGrid3DConfig, OccupancyGrid3DLayout),
    "edge_grid_3d": (EdgeGrid3DConfig, EdgeGrid3DLayout),
    "radial_arm_3d": (RadialArm3DConfig, RadialArm3DLayout),
}


def get_types(maze_type: MazeType) -> MazeTypes:
    try:
        return MAZE_REGISTRY[maze_type]
    except KeyError as exc:
        raise KeyError(f"unknown maze_type: {maze_type}") from exc
