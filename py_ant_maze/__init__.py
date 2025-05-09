"""
py-ant-maze: A package for building and managing ant maze environments.

This package provides tools for creating, manipulating, and visualizing
maze environments for ant navigation tasks.
"""

from .ant_maze import bsAntMaze
from .ant_maze_config import bsAntMazeConfig

__version__ = "0.1.0"
__all__ = ["bsAntMaze", "bsAntMazeConfig"]
