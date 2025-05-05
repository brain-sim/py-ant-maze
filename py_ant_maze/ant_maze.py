"""
AntMaze environment for reinforcement learning navigation tasks.

This module provides a configurable ant maze environment for RL research.
"""
import numpy as np
import os
from typing import List, Tuple, Optional, Dict, Any, Union

from .ant_maze_config import bsAntMazeConfig


class bsAntMaze:
    """
    Ant Maze environment for reinforcement learning.
    
    The environment represents a maze where:
    - 0: represents free space (where the ant can move)
    - 1: represents walls/obstacles
    
    Example maze structure:
    [
        [1, 1, 1, 1],
        [1, 0, 0, 1],
        [1, 0, 1, 1],
        [1, 0, 1, 1],
        [1, 1, 1, 1]
    ]
    """
    
    def __init__(self, maze_config: Optional[bsAntMazeConfig] = None):
        """
        Initialize the Ant Maze environment.
        
        Args:
            maze_config: Configuration object for the maze. If None, default config is used.
        """
        self._maze_txt = None
        self._maze_config = maze_config if maze_config else bsAntMazeConfig()
        self._maze = None
        self._start_pos = None
        self._goal_pos = None
        
        # Default maze if none is provided
        self._default_maze = np.array([
            [1, 1, 1, 1],
            [1, 0, 0, 1],
            [1, 0, 1, 1],
            [1, 0, 1, 1],
            [1, 1, 1, 1]
        ])
        
        # Initialize with default maze
        self._maze = self._default_maze
        self._start_pos = (1, 1)  # Default start position
        self._goal_pos = (3, 1)   # Default goal position
    
    def build_from_txt(self, file_path: str) -> None:
        """
        Build maze configuration from a text file.
        
        The text file should contain a grid of 0s and 1s, where:
        - 0: represents free space
        - 1: represents walls/obstacles
        - S: optionally marks the start position
        - G: optionally marks the goal position
        
        Args:
            file_path: Path to the text file containing maze configuration
        
        Raises:
            FileNotFoundError: If the specified file doesn't exist
            ValueError: If the maze format is invalid
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Maze file not found: {file_path}")
            
        with open(file_path, 'r') as f:
            self._maze_txt = f.read()
            
        # Parse the maze text
        lines = self._maze_txt.strip().split('\n')
        height = len(lines)
        if height == 0:
            raise ValueError("Empty maze file")
            
        width = len(lines[0])
        
        # Initialize maze with zeros
        maze = np.zeros((height, width), dtype=int)
        start_pos = None
        goal_pos = None
        
        # Parse each character
        for i, line in enumerate(lines):
            if len(line) != width:
                raise ValueError(f"Inconsistent maze width at line {i+1}")
                
            for j, char in enumerate(line):
                if char == '1':
                    maze[i, j] = 1
                elif char == '0':
                    maze[i, j] = 0
                elif char == 'S':
                    maze[i, j] = 0
                    start_pos = (i, j)
                elif char == 'G':
                    maze[i, j] = 0
                    goal_pos = (i, j)
                else:
                    raise ValueError(f"Invalid character '{char}' at position ({i}, {j})")
        
        self._maze = maze
        if start_pos:
            self._start_pos = start_pos
        if goal_pos:
            self._goal_pos = goal_pos
    
    def get_maze(self) -> np.ndarray:
        """
        Get the current maze configuration.
        
        Returns:
            numpy.ndarray: 2D array representing the maze
        """
        return self._maze.copy()
    
    def get_start_position(self) -> Tuple[int, int]:
        """
        Get the start position in the maze.
        
        Returns:
            tuple: (row, col) coordinates of the start position
        """
        return self._start_pos
    
    def get_goal_position(self) -> Tuple[int, int]:
        """
        Get the goal position in the maze.
        
        Returns:
            tuple: (row, col) coordinates of the goal position
        """
        return self._goal_pos
    
    def set_start_position(self, pos: Tuple[int, int]) -> None:
        """
        Set the start position in the maze.
        
        Args:
            pos: (row, col) coordinates for the start position
            
        Raises:
            ValueError: If the position is invalid (outside maze or in a wall)
        """
        row, col = pos
        if not (0 <= row < self._maze.shape[0] and 0 <= col < self._maze.shape[1]):
            raise ValueError(f"Start position {pos} is outside maze boundaries")
        if self._maze[row, col] == 1:
            raise ValueError(f"Start position {pos} is inside a wall")
        
        self._start_pos = pos
    
    def set_goal_position(self, pos: Tuple[int, int]) -> None:
        """
        Set the goal position in the maze.
        
        Args:
            pos: (row, col) coordinates for the goal position
            
        Raises:
            ValueError: If the position is invalid (outside maze or in a wall)
        """
        row, col = pos
        if not (0 <= row < self._maze.shape[0] and 0 <= col < self._maze.shape[1]):
            raise ValueError(f"Goal position {pos} is outside maze boundaries")
        if self._maze[row, col] == 1:
            raise ValueError(f"Goal position {pos} is inside a wall")
        
        self._goal_pos = pos
    
    def create_maze(self, maze_array: List[List[int]]) -> None:
        """
        Create a maze from a 2D array.
        
        Args:
            maze_array: 2D list representing the maze layout
            
        Raises:
            ValueError: If the maze format is invalid
        """
        maze = np.array(maze_array)
        if maze.ndim != 2:
            raise ValueError("Maze must be a 2D array")
        if not np.all(np.isin(maze, [0, 1])):
            raise ValueError("Maze can only contain 0s and 1s")
            
        self._maze = maze
        
        # Reset start and goal positions if they're now invalid
        if self._start_pos:
            row, col = self._start_pos
            if not (0 <= row < maze.shape[0] and 0 <= col < maze.shape[1]) or maze[row, col] == 1:
                # Find the first empty cell for start
                for i in range(maze.shape[0]):
                    for j in range(maze.shape[1]):
                        if maze[i, j] == 0:
                            self._start_pos = (i, j)
                            break
                    if self._start_pos != (row, col):
                        break
        
        # Similar check and reset for goal position
        if self._goal_pos:
            row, col = self._goal_pos
            if not (0 <= row < maze.shape[0] and 0 <= col < maze.shape[1]) or maze[row, col] == 1:
                # Find the last empty cell for goal (different from start)
                for i in range(maze.shape[0]-1, -1, -1):
                    for j in range(maze.shape[1]-1, -1, -1):
                        if maze[i, j] == 0 and (i, j) != self._start_pos:
                            self._goal_pos = (i, j)
                            break
                    if self._goal_pos != (row, col):
                        break
    
    def save_to_txt(self, file_path: str) -> None:
        """
        Save the current maze configuration to a text file.
        
        Args:
            file_path: Path where the maze configuration will be saved
        """
        with open(file_path, 'w') as f:
            for i in range(self._maze.shape[0]):
                for j in range(self._maze.shape[1]):
                    if (i, j) == self._start_pos:
                        f.write('S')
                    elif (i, j) == self._goal_pos:
                        f.write('G')
                    else:
                        f.write(str(self._maze[i, j]))
                f.write('\n')
    
    def get_config(self) -> bsAntMazeConfig:
        """
        Get the current maze configuration object.
        
        Returns:
            bsAntMazeConfig: Configuration object for the maze
        """
        return self._maze_config
    
    def set_config(self, maze_config: bsAntMazeConfig) -> None:
        """
        Set a new maze configuration.
        
        Args:
            maze_config: New configuration object for the maze
        """
        self._maze_config = maze_config