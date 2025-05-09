"""
Unit tests for the bsAntMazeConfig class.
"""
import unittest
from py_ant_maze import bsAntMazeConfig


class TestAntMazeConfig(unittest.TestCase):
    """Test cases for the bsAntMazeConfig class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = bsAntMazeConfig()
    
    def test_default_config(self):
        """Test default configuration values."""
        self.assertEqual(self.config.wall_height, 0.5)
        self.assertEqual(self.config.wall_width, 0.1)
        self.assertEqual(self.config.cell_size, 1.0)
        self.assertEqual(self.config.ant_scale, 0.8)
        self.assertEqual(self.config.custom_settings, {})
        
        # Check default colors
        self.assertEqual(len(self.config.colors), 5)
        self.assertIn('wall', self.config.colors)
        self.assertIn('floor', self.config.colors)
        self.assertIn('ant', self.config.colors)
        self.assertIn('goal', self.config.colors)
        self.assertIn('start', self.config.colors)
    
    def test_custom_config(self):
        """Test custom configuration values."""
        custom_config = bsAntMazeConfig(
            wall_height=0.8,
            wall_width=0.15,
            cell_size=1.2,
            ant_scale=0.7,
            render_walls=False,
            custom_settings={"custom_param": 123}
        )
        
        self.assertEqual(custom_config.wall_height, 0.8)
        self.assertEqual(custom_config.wall_width, 0.15)
        self.assertEqual(custom_config.cell_size, 1.2)
        self.assertEqual(custom_config.ant_scale, 0.7)
        self.assertEqual(custom_config.render_walls, False)
        self.assertEqual(custom_config.custom_settings, {"custom_param": 123})
    
    def test_set_color(self):
        """Test setting colors for visualization."""
        # Valid color
        self.config.set_color('wall', (0.5, 0.5, 0.5))
        self.assertEqual(self.config.colors['wall'], (0.5, 0.5, 0.5))
        
        # Invalid element
        with self.assertRaises(ValueError):
            self.config.set_color('invalid_element', (0, 0, 0))
        
        # Invalid color format
        with self.assertRaises(ValueError):
            self.config.set_color('wall', (0, 0))  # Too few values
        
        with self.assertRaises(ValueError):
            self.config.set_color('wall', (0, 0, 2))  # Value out of range
    
    def test_to_dict(self):
        """Test converting config to dictionary."""
        config_dict = self.config.to_dict()
        
        self.assertIn('wall_height', config_dict)
        self.assertIn('wall_width', config_dict)
        self.assertIn('cell_size', config_dict)
        self.assertIn('ant_scale', config_dict)
        self.assertIn('render_walls', config_dict)
        self.assertIn('colors', config_dict)
    
    def test_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {
            'wall_height': 0.8,
            'wall_width': 0.15,
            'cell_size': 1.2,
            'custom_param': 123
        }
        
        config = bsAntMazeConfig.from_dict(config_dict)
        
        self.assertEqual(config.wall_height, 0.8)
        self.assertEqual(config.wall_width, 0.15)
        self.assertEqual(config.cell_size, 1.2)
        self.assertEqual(config.custom_settings, {'custom_param': 123})
        
        # Check that unspecified values use defaults
        self.assertEqual(config.ant_scale, 0.8)
        self.assertEqual(config.render_walls, True)
    
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
        
        self.assertEqual(self.config.wall_height, 0.8)
        self.assertEqual(self.config.colors['wall'], (0.5, 0.5, 0.5))
        self.assertEqual(self.config.colors['floor'], (0.8, 0.8, 0.8))
        self.assertEqual(self.config.custom_settings, {'custom_param': 123})


if __name__ == '__main__':
    unittest.main()
