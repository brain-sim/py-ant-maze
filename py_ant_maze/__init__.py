"""
py-ant-maze: A package for ant maze navigation in reinforcement learning.

This package provides tools for creating and manipulating maze environments
for ant navigation tasks in reinforcement learning research.
"""

from .ant_maze import bsAntMaze
from .ant_maze_config import bsAntMazeConfig

__version__ = "0.1.0"
__all__ = ["bsAntMaze", "bsAntMazeConfig"]
