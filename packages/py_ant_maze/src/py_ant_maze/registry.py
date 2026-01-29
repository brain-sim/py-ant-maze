from typing import Dict, Tuple, Type

from .types.occupancy_grid import OccupancyGridConfig, OccupancyGridLayout
from .types.edge_grid import EdgeGridConfig, EdgeGridLayout


ConfigType = Type[object]
LayoutType = Type[object]


MAZE_REGISTRY: Dict[str, Tuple[ConfigType, LayoutType]] = {
    "occupancy_grid": (OccupancyGridConfig, OccupancyGridLayout),
    "edge_grid": (EdgeGridConfig, EdgeGridLayout),
}


def get_types(maze_type: str) -> Tuple[ConfigType, LayoutType]:
    try:
        return MAZE_REGISTRY[maze_type]
    except KeyError as exc:
        raise KeyError(f"unknown maze_type: {maze_type}") from exc
