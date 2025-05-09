"""
Configuration for the AntMaze environment.

This module provides configuration settings for the AntMaze environment
including physical properties and visualization settings.
"""
from typing import Dict, Any, Tuple, Optional, List


class bsAntMazeConfig:
    """
    Configuration class for the AntMaze environment.
    
    This class stores the configuration parameters for the maze environment,
    including wall dimensions and visualization settings.
    """
    
    def __init__(self, 
                 wall_height: float = 0.5,
                 wall_width: float = 0.1,
                 cell_size: float = 1.0,
                 ant_scale: float = 0.8,
                 render_walls: bool = True,
                 custom_settings: Optional[Dict[str, Any]] = None):
        """
        Initialize the Ant Maze configuration.
        
        Args:
            wall_height: Height of maze walls
            wall_width: Width/thickness of maze walls
            cell_size: Size of each cell in the maze
            ant_scale: Scale factor for the ant agent
            render_walls: Whether to render the walls in visualization
            custom_settings: Additional custom configuration settings
        """
        # Wall and maze physical properties
        self.wall_height = wall_height
        self.wall_width = wall_width
        self.cell_size = cell_size
        
        # Agent properties
        self.ant_scale = ant_scale
        
        # Rendering settings
        self.render_walls = render_walls
        
        # Store any additional custom settings
        self.custom_settings = custom_settings or {}
        
        # Color settings for visualization (RGB format)
        self.colors = {
            'wall': (0.8, 0.8, 0.8),    # Light gray
            'floor': (0.9, 0.9, 0.9),   # Very light gray
            'ant': (0.1, 0.3, 0.8),     # Blue
            'goal': (0.0, 0.8, 0.0),    # Green
            'start': (0.8, 0.0, 0.0),   # Red
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to a dictionary.
        
        Returns:
            dict: Dictionary representation of the configuration
        """
        config_dict = {
            'wall_height': self.wall_height,
            'wall_width': self.wall_width,
            'cell_size': self.cell_size,
            'ant_scale': self.ant_scale,
            'render_walls': self.render_walls,
            'colors': self.colors,
            **self.custom_settings
        }
        return config_dict
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'bsAntMazeConfig':
        """
        Create a configuration object from a dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values
            
        Returns:
            bsAntMazeConfig: New configuration object
        """
        # Extract the known parameters
        wall_height = config_dict.get('wall_height', 0.5)
        wall_width = config_dict.get('wall_width', 0.1)
        cell_size = config_dict.get('cell_size', 1.0)
        ant_scale = config_dict.get('ant_scale', 0.8)
        render_walls = config_dict.get('render_walls', True)
        
        # Create a new config object
        config = cls(
            wall_height=wall_height,
            wall_width=wall_width,
            cell_size=cell_size,
            ant_scale=ant_scale,
            render_walls=render_walls
        )
        
        # Add colors if present
        if 'colors' in config_dict:
            config.colors = config_dict['colors']
        
        # Add any remaining custom settings
        custom_keys = set(config_dict.keys()) - {
            'wall_height', 'wall_width', 'cell_size', 'ant_scale',
            'render_walls', 'colors'
        }
        
        for key in custom_keys:
            config.custom_settings[key] = config_dict[key]
        
        return config
    
    def set_color(self, element: str, color: Tuple[float, float, float]) -> None:
        """
        Set color for a specific element in the visualization.
        
        Args:
            element: Element name ('wall', 'floor', 'ant', 'goal', 'start')
            color: RGB color tuple with values in [0, 1]
            
        Raises:
            ValueError: If the element is unknown or color format is invalid
        """
        if element not in self.colors:
            raise ValueError(f"Unknown element: {element}. Available elements: {list(self.colors.keys())}")
            
        if not (isinstance(color, tuple) and len(color) == 3):
            raise ValueError("Color must be an RGB tuple with 3 values between 0 and 1")
            
        if not all(0 <= c <= 1 for c in color):
            raise ValueError("Color values must be between 0 and 1")
            
        self.colors[element] = color
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        Update configuration with values from a dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values to update
        """
        for key, value in config_dict.items():
            if key == 'colors' and isinstance(value, dict):
                for element, color in value.items():
                    self.set_color(element, color)
            elif hasattr(self, key):
                setattr(self, key, value)
            else:
                self.custom_settings[key] = value
