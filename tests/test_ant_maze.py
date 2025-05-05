"""
Unit tests for the bsAntMaze class.
"""
import os
import unittest
import tempfile
import numpy as np
from py_ant_maze import bsAntMaze, bsAntMazeConfig


class TestAntMaze(unittest.TestCase):
    """Test cases for the bsAntMaze class."""
    
    def setUp(self):
        """Set up test environment."""
        self.maze = bsAntMaze()
        
        # Sample maze for testing
        self.sample_maze = [
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1]
        ]
    
    def test_default_maze(self):
        """Test default maze initialization."""
        maze = self.maze.get_maze()
        self.assertEqual(maze.shape, (5, 4))
        self.assertEqual(maze[1, 1], 0)  # Empty space
        self.assertEqual(maze[0, 0], 1)  # Wall
        
        # Check default start and goal positions
        self.assertEqual(self.maze.get_start_position(), (1, 1))
        self.assertEqual(self.maze.get_goal_position(), (3, 1))
    
    def test_create_maze(self):
        """Test creating a custom maze."""
        self.maze.create_maze(self.sample_maze)
        maze = self.maze.get_maze()
        
        self.assertEqual(maze.shape, (5, 5))
        np.testing.assert_array_equal(maze, np.array(self.sample_maze))
    
    def test_set_positions(self):
        """Test setting start and goal positions."""
        self.maze.create_maze(self.sample_maze)
        
        # Set valid positions
        self.maze.set_start_position((1, 1))
        self.maze.set_goal_position((3, 3))
        
        self.assertEqual(self.maze.get_start_position(), (1, 1))
        self.assertEqual(self.maze.get_goal_position(), (3, 3))
        
        # Test invalid positions
        with self.assertRaises(ValueError):
            self.maze.set_start_position((0, 0))  # Wall
        
        with self.assertRaises(ValueError):
            self.maze.set_goal_position((10, 10))  # Outside maze
    
    def test_save_and_load(self):
        """Test saving and loading maze configurations."""
        self.maze.create_maze(self.sample_maze)
        self.maze.set_start_position((1, 1))
        self.maze.set_goal_position((3, 3))
        
        # Save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file_path = tmp.name
        
        self.maze.save_to_txt(file_path)
        
        # Load in a new maze object
        new_maze = bsAntMaze()
        new_maze.build_from_txt(file_path)
        
        # Check if loaded maze matches the original
        np.testing.assert_array_equal(new_maze.get_maze(), np.array(self.sample_maze))
        self.assertEqual(new_maze.get_start_position(), (1, 1))
        self.assertEqual(new_maze.get_goal_position(), (3, 3))
        
        # Clean up
        os.unlink(file_path)
    
    def test_config(self):
        """Test maze configuration."""
        config = bsAntMazeConfig(
            wall_height=0.8,
            wall_width=0.15,
            cell_size=1.2
        )
        
        maze = bsAntMaze(config)
        maze_config = maze.get_config()
        
        self.assertEqual(maze_config.wall_height, 0.8)
        self.assertEqual(maze_config.wall_width, 0.15)
        self.assertEqual(maze_config.cell_size, 1.2)
        
        # Test updating config
        new_config = bsAntMazeConfig(wall_height=1.0)
        maze.set_config(new_config)
        maze_config = maze.get_config()
        
        self.assertEqual(maze_config.wall_height, 1.0)


if __name__ == '__main__':
    unittest.main()
