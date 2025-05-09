"""
Configuration for the AntMaze environment.

This module provides configuration settings for the AntMaze environment
including physical properties and visualization settings.
"""
from typing import Dict, Any, Tuple, Optional, List


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
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'bsAntMazeDimensions':
        """
        Create a dimensions object from a dictionary.
        
        Args:
            config_dict: Dictionary containing dimension values
            
        Returns:
            bsAntMazeDimensions: New dimensions object
        """
        return cls(
            wall_height=config_dict.get('wall_height', 0.5),
            cell_size=config_dict.get('cell_size', 1.0),
            ant_scale=config_dict.get('ant_scale', 0.8)
        )


class bsAntMazeVisuals:
    """
    Visualization configuration for the maze environment.
    
    This class stores visualization settings like colors for different
    maze elements.
    """
    
    def __init__(self):
        """Initialize the visualization configuration."""
        # Color settings for visualization (RGB format)
        self.colors = {
            'wall': (0.8, 0.8, 0.8),    # Light gray
            'floor': (0.9, 0.9, 0.9),   # Very light gray
            'ant': (0.1, 0.3, 0.8),     # Blue
            'goal': (0.0, 0.8, 0.0),    # Green
            'start': (0.8, 0.0, 0.0),   # Red
        }
    
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
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert visualization settings to a dictionary.
        
        Returns:
            dict: Dictionary representation of the visualization settings
        """
        return {'colors': self.colors}
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'bsAntMazeVisuals':
        """
        Create a visualization config from a dictionary.
        
        Args:
            config_dict: Dictionary containing visualization settings
            
        Returns:
            bsAntMazeVisuals: New visualization config object
        """
        visuals = cls()
        if 'colors' in config_dict:
            for element, color in config_dict['colors'].items():
                visuals.set_color(element, color)
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
            **self.dimensions.to_dict(),
            **self.visuals.to_dict(),
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
        dim_keys = {'wall_height', 'cell_size', 'ant_scale'}
        vis_keys = {'colors'}
        
        dim_dict = {k: config_dict[k] for k in dim_keys if k in config_dict}
        vis_dict = {k: config_dict[k] for k in vis_keys if k in config_dict}
        
        # Create dimension and visual objects
        dimensions = bsAntMazeDimensions.from_dict(dim_dict)
        visuals = bsAntMazeVisuals.from_dict(vis_dict)
        
        # Extract custom settings
        custom_keys = set(config_dict.keys()) - dim_keys - vis_keys
        custom_settings = {k: config_dict[k] for k in custom_keys}
        
        return cls(dimensions, visuals, custom_settings)
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        Update configuration with values from a dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values to update
        """
        # Update dimensions
        dim_keys = {'wall_height', 'cell_size', 'ant_scale'}
        dim_updates = {k: v for k, v in config_dict.items() if k in dim_keys}
        if dim_updates:
            self.dimensions = bsAntMazeDimensions.from_dict({
                **self.dimensions.to_dict(),
                **dim_updates
            })
        
        # Update colors
        if 'colors' in config_dict:
            for element, color in config_dict['colors'].items():
                self.visuals.set_color(element, color)
        
        # Update custom settings
        custom_keys = set(config_dict.keys()) - dim_keys - {'colors'}
        for key in custom_keys:
            self.custom_settings[key] = config_dict[key]
