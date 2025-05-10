"""
Configuration for the AntMaze environment.

This module provides configuration settings for the AntMaze environment
including physical properties and visualization settings.
"""
from typing import Dict, Any, Tuple, Optional, List
import json


class bsAntMazeDimensions:
    """
    Physical dimensions configuration for the maze environment.
    
    This class stores the physical dimensions and properties of the maze
    that would be relevant for visualization or simulation.
    
    Note: The wall width is always equal to the cell size, as the maze
    is generated using a grid of squares. Only the wall height can be
    configured independently.
    """
    
    def __init__(self, 
                 wall_height: float = 0.5,
                 cell_size: float = 1.0,
                 ant_scale: float = 0.8):
        """
        Initialize the maze dimensions configuration.
        
        Args:
            wall_height: Height of maze walls
            cell_size: Size of each cell in the maze (also determines wall width)
            ant_scale: Scale factor for the ant agent
        """
        self.wall_height = wall_height
        self.cell_size = cell_size
        self.ant_scale = ant_scale
        
        # Wall width is always equal to cell size
        self.wall_width = cell_size
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert dimensions to a dictionary.
        
        Returns:
            dict: Dictionary representation of the dimensions
        """
        return {
            'wall_height': self.wall_height,
            'cell_size': self.cell_size,
            'ant_scale': self.ant_scale
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'bsAntMazeDimensions':
        """
        Create dimensions from a dictionary.
        
        Args:
            data: Dictionary containing dimension values
            
        Returns:
            bsAntMazeDimensions: New dimensions object
        """
        return cls(
            wall_height=data.get('wall_height', 0.5),
            cell_size=data.get('cell_size', 1.0),
            ant_scale=data.get('ant_scale', 0.8)
        )


class bsAntMazeVisuals:
    """
    Visualization configuration for the maze environment.
    
    This class stores visualization settings like colors for different
    maze elements. Colors are stored in 0-1 range.
    """
    
    def __init__(self):
        """Initialize the visualization configuration."""
        # Default colors in 0-1 range
        self._colors = {
            'wall': (0.8, 0.8, 0.8),
            'floor': (0.9, 0.9, 0.9),
            'ant': (0.1, 0.3, 0.8),
            'goal': (0.0, 0.8, 0.0),
            'start': (0.8, 0.0, 0.0)
        }
    
    def set_color(self, element: str, color: Tuple[float, float, float]) -> None:
        """
        Set color for a specific element.
        
        Args:
            element: Element name ('wall', 'floor', 'ant', 'goal', 'start')
            color: RGB color tuple in 0-1 range
            
        Raises:
            ValueError: If the element is unknown or color format is invalid
        """
        if element not in self._colors:
            raise ValueError(f"Unknown element: {element}")
        if not (isinstance(color, tuple) and len(color) == 3):
            raise ValueError("Color must be an RGB tuple with 3 values")
        if not all(0 <= c <= 1 for c in color):
            raise ValueError("Color values must be between 0 and 1")
        self._colors[element] = color
    
    def get_color(self, element: str) -> Tuple[float, float, float]:
        """
        Get color for a specific element.
        
        Args:
            element: Element name ('wall', 'floor', 'ant', 'goal', 'start')
            
        Returns:
            tuple: RGB color tuple in 0-1 range
            
        Raises:
            ValueError: If the element is unknown
        """
        if element not in self._colors:
            raise ValueError(f"Unknown element: {element}")
        return self._colors[element]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert visualization settings to a dictionary.
        
        Returns:
            dict: Dictionary representation of the visualization settings
        """
        return {'colors': self._colors}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'bsAntMazeVisuals':
        """
        Create visuals from a dictionary.
        
        Args:
            data: Dictionary containing visualization settings
            
        Returns:
            bsAntMazeVisuals: New visuals object
        """
        visuals = cls()
        if 'colors' in data:
            for element, color in data['colors'].items():
                visuals.set_color(element, tuple(color))
        return visuals


class bsAntMazeConfig:
    """
    Main configuration class for the AntMaze environment.
    
    This class combines physical dimensions and visualization settings,
    along with any custom settings.
    """
    
    def __init__(self, 
                 dimensions: Optional[bsAntMazeDimensions] = None,
                 visuals: Optional[bsAntMazeVisuals] = None,
                 custom_settings: Optional[Dict[str, Any]] = None):
        """
        Initialize the maze configuration.
        
        Args:
            dimensions: Physical dimensions configuration
            visuals: Visualization configuration
            custom_settings: Additional custom configuration settings
        """
        self.dimensions = dimensions if dimensions else bsAntMazeDimensions()
        self.visuals = visuals if visuals else bsAntMazeVisuals()
        self.custom_settings = custom_settings or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to a dictionary.
        
        Returns:
            dict: Dictionary representation of the configuration
        """
        return {
            'dimensions': self.dimensions.to_dict(),
            'colors': self.visuals.to_dict()['colors'],
            **self.custom_settings
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'bsAntMazeConfig':
        """
        Create a configuration object from a dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values
            
        Returns:
            bsAntMazeConfig: New configuration object
        """
        # Extract dimension and visual settings
        dim_dict = config_dict.get('dimensions', {})
        vis_dict = {'colors': config_dict.get('colors', {})}
        
        # Create dimension and visual objects
        dimensions = bsAntMazeDimensions.from_dict(dim_dict)
        visuals = bsAntMazeVisuals.from_dict(vis_dict)
        
        # Extract custom settings
        custom_keys = set(config_dict.keys()) - {'dimensions', 'colors'}
        custom_settings = {k: config_dict[k] for k in custom_keys}
        
        return cls(dimensions, visuals, custom_settings)
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        Update configuration with values from a dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values to update
        """
        # Update dimensions
        if 'dimensions' in config_dict:
            self.dimensions = bsAntMazeDimensions.from_dict(config_dict['dimensions'])
        
        # Update colors
        if 'colors' in config_dict:
            for element, color in config_dict['colors'].items():
                self.visuals.set_color(element, tuple(color))
        
        # Update custom settings
        custom_keys = set(config_dict.keys()) - {'dimensions', 'colors'}
        for key in custom_keys:
            self.custom_settings[key] = config_dict[key]

    @classmethod
    def from_json(cls, file_path: str) -> 'bsAntMazeConfig':
        """
        Load configuration from a JSON file.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            bsAntMazeConfig: Configuration object
            
        Raises:
            FileNotFoundError: If the config file doesn't exist
            ValueError: If the JSON format is invalid
        """
        try:
            with open(file_path, 'r') as f:
                config_dict = json.load(f)
            return cls.from_dict(config_dict)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {file_path}: {str(e)}")
            
    def save_to_json(self, file_path: str) -> None:
        """
        Save configuration to a JSON file.
        
        Args:
            file_path: Path where the configuration will be saved
            
        Raises:
            IOError: If the file cannot be written
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=4)
        except IOError as e:
            raise IOError(f"Failed to save configuration to {file_path}: {str(e)}")
