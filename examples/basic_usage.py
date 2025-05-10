"""
Basic usage example for the py-ant-maze package.

This example demonstrates how to:
1. Create a maze with default configuration
2. Load a maze from a text file
3. Load configuration from a JSON file
4. Save maze and configuration
"""
import os
from py_ant_maze import bsAntMaze, bsAntMazeConfig

def main():
    # Create a maze with default configuration
    maze = bsAntMaze()
    print("Default maze created")
    
    # Create a simple maze layout
    maze_layout = [
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1]
    ]
    maze.create_maze(maze_layout)
    print("Maze layout created")
    
    # Save the maze to a text file
    maze.save_to_txt("example_maze.txt")
    print("Maze saved to example_maze.txt")
    
    # Create a custom configuration
    config = bsAntMazeConfig()
    config.dimensions.wall_height = 0.7
    config.dimensions.cell_size = 1.2
    config.visuals.set_color('wall', (0.7, 0.7, 0.7))
    config.visuals.set_color('ant', (0.2, 0.4, 0.9))
    
    # Save configuration to JSON
    config.save_to_json("example_config.json")
    print("Configuration saved to example_config.json")
    
    # Create a new maze with the saved configuration
    new_maze = bsAntMaze.from_config_file("example_config.json")
    new_maze.build_from_txt("example_maze.txt")
    print("New maze created with custom configuration")
    
    # Demonstrate configuration access
    print("\nMaze Configuration:")
    print(f"Wall Height: {new_maze.get_config().dimensions.wall_height}")
    print(f"Cell Size: {new_maze.get_config().dimensions.cell_size}")
    print(f"Ant Color: {new_maze.get_config().visuals.get_color('ant')}")
    
    # # Clean up example files
    # os.remove("example_maze.txt")
    # os.remove("example_config.json")
    # print("\nExample files cleaned up")

if __name__ == "__main__":
    main()
