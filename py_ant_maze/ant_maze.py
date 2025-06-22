"""
AntMaze environment builder for creating and managing maze layouts.

This module provides a configurable ant maze environment builder for creating
and managing maze layouts with walls, start positions, goal positions, and
button-door mechanisms.
"""
import numpy as np
import os
import json
from typing import List, Tuple, Optional, Dict, Any, Union

from .ant_maze_config import bsAntMazeConfig


class bsAntMaze:
    """
    Ant Maze environment builder.
    
    The environment represents a maze where:
    - 0: represents free space (where the ant can move)
    - 1: represents walls/obstacles
    - S: represents start position
    - G: represents goal position  
    - B: represents button positions
    
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
        Initialize the Ant Maze environment builder.
        
        Args:
            maze_config: Configuration object for the maze. If None, default config is used.
        """
        self._maze_txt = None
        self._config = maze_config if maze_config else bsAntMazeConfig()
        self._maze = None
        self._start_pos = None
        self._goal_pos = None
        self._buttons = []  # List of button positions
        self._button_door_mapping = {}  # Dict mapping button positions to door positions
        self._door_states = {}  # Dict tracking door states (True = closed/wall, False = open)
        self._original_maze = None  # Store original maze without door modifications
        
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
        self._original_maze = self._default_maze.copy()
        self._start_pos = (1, 1)  # Default start position
        self._goal_pos = (3, 1)   # Default goal position

    @classmethod
    def from_config_file(cls, config_file_path: str) -> 'bsAntMaze':
        """
        Create a maze instance from a configuration file.
        
        Args:
            config_file_path: Path to the configuration file
            
        Returns:
            bsAntMaze: New maze instance with loaded configuration
            
        Raises:
            FileNotFoundError: If the config file doesn't exist
            ValueError: If the config file format is invalid
        """
        config = bsAntMazeConfig.from_json(config_file_path)
        return cls(config)
    
    def build_from_txt(self, file_path: str, buttons_config_path: Optional[str] = None) -> None:
        """
        Build maze configuration from a text file.
        
        The text file should contain a grid of 0s and 1s, where:
        - 0: represents free space
        - 1: represents walls/obstacles
        - S: optionally marks the start position
        - G: optionally marks the goal position
        - B: optionally marks button positions
        
        Args:
            file_path: Path to the text file containing maze configuration
            buttons_config_path: Optional path to JSON file containing button-door mappings
        
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
        buttons = []
        
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
                elif char == 'B':
                    maze[i, j] = 0  # Buttons are on free space
                    buttons.append((i, j))
                else:
                    raise ValueError(f"Invalid character '{char}' at position ({i}, {j})")
        
        self._maze = maze
        self._original_maze = maze.copy()
        self._buttons = buttons
        
        if start_pos:
            self._start_pos = start_pos
        if goal_pos:
            self._goal_pos = goal_pos
            
        # Load button-door mappings if provided
        if buttons_config_path:
            self.load_button_door_mapping(buttons_config_path)

    def load_button_door_mapping(self, config_path: str) -> None:
        """
        Load button-door mapping from a JSON configuration file.
        
        Args:
            config_path: Path to JSON file containing button-door mappings
            
        Raises:
            FileNotFoundError: If the config file doesn't exist
            ValueError: If the config format is invalid
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Button config file not found: {config_path}")
            
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        if 'button_mapping' not in config:
            raise ValueError("Invalid button config: missing 'button_mapping' key")
            
        self._button_door_mapping = {}
        self._door_states = {}
        
        for mapping in config['button_mapping']:
            if 'button' not in mapping or 'door' not in mapping:
                raise ValueError("Invalid button mapping: missing 'button' or 'door' key")
                
            button_pos = tuple(mapping['button'])
            door_pos = tuple(mapping['door'])
            
            # Validate button position
            if button_pos not in self._buttons:
                raise ValueError(f"Button position {button_pos} not found in maze")
                
            # Validate door position is within maze bounds
            row, col = door_pos
            if not (0 <= row < self._maze.shape[0] and 0 <= col < self._maze.shape[1]):
                raise ValueError(f"Door position {door_pos} is outside maze boundaries")
                
            self._button_door_mapping[button_pos] = door_pos
            # Initialize door as closed (wall) - doors start closed by default
            self._door_states[door_pos] = True
        
    def _update_maze_with_doors(self) -> None:
        """Update the maze representation based on current door states."""
        # Start with original maze
        self._maze = self._original_maze.copy()
        
        # Apply door states
        for door_pos, is_closed in self._door_states.items():
            row, col = door_pos
            if is_closed:
                self._maze[row, col] = 1  # Closed door = wall
            else:
                self._maze[row, col] = 0  # Open door = free space

    def get_maze(self) -> np.ndarray:
        """
        Get the current maze configuration.
        
        Returns:
            numpy.ndarray: 2D array representing the maze
        """
        return self._maze.copy()

    def get_buttons(self) -> List[Tuple[int, int]]:
        """
        Get all button positions in the maze.
        
        Returns:
            list: List of (row, col) tuples representing button positions
        """
        return self._buttons.copy()
        
    def get_button_door_mapping(self) -> Dict[Tuple[int, int], Tuple[int, int]]:
        """
        Get the button-door mapping.
        
        Returns:
            dict: Dictionary mapping button positions to door positions
        """
        return self._button_door_mapping.copy()
        
    def get_door_states(self) -> Dict[Tuple[int, int], bool]:
        """
        Get current door states.
        
        Returns:
            dict: Dictionary mapping door positions to their states (True=closed, False=open)
        """
        return self._door_states.copy()
        
    def is_door_open(self, door_pos: Tuple[int, int]) -> bool:
        """
        Check if a door is open.
        
        Args:
            door_pos: (row, col) coordinates of the door
            
        Returns:
            bool: True if door is open, False if closed or not a door
        """
        return not self._door_states.get(door_pos, True)

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
        self._original_maze = maze.copy()
        
        # Clear button/door data when creating new maze
        self._buttons = []
        self._button_door_mapping = {}
        self._door_states = {}
        
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
            
        Raises:
            IOError: If the file cannot be written
        """
        try:
            with open(file_path, 'w') as f:
                # Convert maze to text representation
                for i in range(self._original_maze.shape[0]):
                    for j in range(self._original_maze.shape[1]):
                        if (i, j) == self._start_pos:
                            f.write('S')
                        elif (i, j) == self._goal_pos:
                            f.write('G')
                        elif (i, j) in self._buttons:
                            f.write('B')
                        else:
                            f.write(str(self._original_maze[i, j]))
                    f.write('\n')
        except IOError as e:
            raise IOError(f"Failed to save maze to {file_path}: {str(e)}")
    
    def get_config(self) -> bsAntMazeConfig:
        """
        Get the current maze configuration.
        
        Returns:
            bsAntMazeConfig: Current configuration object
        """
        return self._config
    
    def set_config(self, maze_config: bsAntMazeConfig) -> None:
        """
        Set a new maze configuration.
        
        Args:
            maze_config: New configuration object
            
        Raises:
            ValueError: If the configuration is invalid
        """
        if not isinstance(maze_config, bsAntMazeConfig):
            raise ValueError("Configuration must be an instance of bsAntMazeConfig")
        self._config = maze_config