"""
Unit tests for the AntMaze configuration classes.
"""
import unittest
from py_ant_maze import bsAntMazeConfig, bsAntMazeDimensions, bsAntMazeVisuals


class TestAntMazeDimensions(unittest.TestCase):
    """Test cases for the bsAntMazeDimensions class."""
    
    def setUp(self):
        """Set up test environment."""
        self.dimensions = bsAntMazeDimensions()
    
    def test_default_dimensions(self):
        """Test default dimension values."""
        self.assertEqual(self.dimensions.wall_height, 0.5)
        self.assertEqual(self.dimensions.cell_size, 1.0)
        self.assertEqual(self.dimensions.ant_scale, 0.8)
        # Wall width should equal cell size
        self.assertEqual(self.dimensions.wall_width, self.dimensions.cell_size)
    
    def test_custom_dimensions(self):
        """Test custom dimension values."""
        custom_dims = bsAntMazeDimensions(
            wall_height=0.8,
            cell_size=1.2,
            ant_scale=0.7
        )
        
        self.assertEqual(custom_dims.wall_height, 0.8)
        self.assertEqual(custom_dims.cell_size, 1.2)
        self.assertEqual(custom_dims.ant_scale, 0.7)
        # Wall width should equal cell size
        self.assertEqual(custom_dims.wall_width, custom_dims.cell_size)
    
    def test_to_dict(self):
        """Test converting dimensions to dictionary."""
        dim_dict = self.dimensions.to_dict()
        
        self.assertIn('wall_height', dim_dict)
        self.assertIn('cell_size', dim_dict)
        self.assertIn('ant_scale', dim_dict)
        # wall_width should not be in the dictionary as it's derived from cell_size
        self.assertNotIn('wall_width', dim_dict)
    
    def test_from_dict(self):
        """Test creating dimensions from dictionary."""
        dim_dict = {
            'wall_height': 0.8,
            'cell_size': 1.2,
            'ant_scale': 0.7
        }
        
        dimensions = bsAntMazeDimensions.from_dict(dim_dict)
        
        self.assertEqual(dimensions.wall_height, 0.8)
        self.assertEqual(dimensions.cell_size, 1.2)
        self.assertEqual(dimensions.ant_scale, 0.7)
        # Wall width should equal cell size
        self.assertEqual(dimensions.wall_width, dimensions.cell_size)


class TestAntMazeVisuals(unittest.TestCase):
    """Test cases for the bsAntMazeVisuals class."""
    
    def setUp(self):
        """Set up test environment."""
        self.visuals = bsAntMazeVisuals()
    
    def test_default_colors(self):
        """Test default color values."""
        self.assertEqual(len(self.visuals.colors), 5)
        self.assertIn('wall', self.visuals.colors)
        self.assertIn('floor', self.visuals.colors)
        self.assertIn('ant', self.visuals.colors)
        self.assertIn('goal', self.visuals.colors)
        self.assertIn('start', self.visuals.colors)
    
    def test_set_color(self):
        """Test setting colors for visualization."""
        # Valid color
        self.visuals.set_color('wall', (0.5, 0.5, 0.5))
        self.assertEqual(self.visuals.colors['wall'], (0.5, 0.5, 0.5))
        
        # Invalid element
        with self.assertRaises(ValueError):
            self.visuals.set_color('invalid_element', (0, 0, 0))
        
        # Invalid color format
        with self.assertRaises(ValueError):
            self.visuals.set_color('wall', (0, 0))  # Too few values
        
        with self.assertRaises(ValueError):
            self.visuals.set_color('wall', (0, 0, 2))  # Value out of range
    
    def test_to_dict(self):
        """Test converting visuals to dictionary."""
        vis_dict = self.visuals.to_dict()
        self.assertIn('colors', vis_dict)
    
    def test_from_dict(self):
        """Test creating visuals from dictionary."""
        vis_dict = {
            'colors': {
                'wall': (0.5, 0.5, 0.5),
                'floor': (0.8, 0.8, 0.8)
            }
        }
        
        visuals = bsAntMazeVisuals.from_dict(vis_dict)
        self.assertEqual(visuals.colors['wall'], (0.5, 0.5, 0.5))
        self.assertEqual(visuals.colors['floor'], (0.8, 0.8, 0.8))


class TestAntMazeConfig(unittest.TestCase):
    """Test cases for the bsAntMazeConfig class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = bsAntMazeConfig()
    
    def test_default_config(self):
        """Test default configuration values."""
        # Check dimensions
        self.assertEqual(self.config.dimensions.wall_height, 0.5)
        self.assertEqual(self.config.dimensions.cell_size, 1.0)
        self.assertEqual(self.config.dimensions.ant_scale, 0.8)
        
        # Check visuals
        self.assertEqual(len(self.config.visuals.colors), 5)
        
        # Check custom settings
        self.assertEqual(self.config.custom_settings, {})
    
    def test_custom_config(self):
        """Test custom configuration values."""
        dimensions = bsAntMazeDimensions(wall_height=0.8, cell_size=1.2)
        visuals = bsAntMazeVisuals()
        visuals.set_color('wall', (0.5, 0.5, 0.5))
        
        config = bsAntMazeConfig(
            dimensions=dimensions,
            visuals=visuals,
            custom_settings={"custom_param": 123}
        )
        
        self.assertEqual(config.dimensions.wall_height, 0.8)
        self.assertEqual(config.dimensions.cell_size, 1.2)
        self.assertEqual(config.visuals.colors['wall'], (0.5, 0.5, 0.5))
        self.assertEqual(config.custom_settings["custom_param"], 123)
    
    def test_to_dict(self):
        """Test converting config to dictionary."""
        config_dict = self.config.to_dict()
        
        # Check dimensions
        self.assertIn('wall_height', config_dict)
        self.assertIn('cell_size', config_dict)
        self.assertIn('ant_scale', config_dict)
        
        # Check visuals
        self.assertIn('colors', config_dict)
    
    def test_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {
            'wall_height': 0.8,
            'cell_size': 1.2,
            'colors': {
                'wall': (0.5, 0.5, 0.5)
            },
            'custom_param': 123
        }
        
        config = bsAntMazeConfig.from_dict(config_dict)
        
        self.assertEqual(config.dimensions.wall_height, 0.8)
        self.assertEqual(config.dimensions.cell_size, 1.2)
        self.assertEqual(config.visuals.colors['wall'], (0.5, 0.5, 0.5))
        self.assertEqual(config.custom_settings['custom_param'], 123)
    
    def test_update(self):
        """Test updating config values."""
        update_dict = {
            'wall_height': 0.8,
            'colors': {
                'wall': (0.5, 0.5, 0.5),
                'floor': (0.8, 0.8, 0.8)
            },
            'custom_param': 123
        }
        
        self.config.update(update_dict)
        
        self.assertEqual(self.config.dimensions.wall_height, 0.8)
        self.assertEqual(self.config.visuals.colors['wall'], (0.5, 0.5, 0.5))
        self.assertEqual(self.config.visuals.colors['floor'], (0.8, 0.8, 0.8))
        self.assertEqual(self.config.custom_settings['custom_param'], 123)


if __name__ == '__main__':
    unittest.main()
