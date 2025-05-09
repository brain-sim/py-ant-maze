"""
Basic usage example for the py-ant-maze package.

This script demonstrates how to create, manipulate, and save maze configurations.
"""
import numpy as np
from py_ant_maze import bsAntMaze, bsAntMazeConfig


def main():
    # Create a maze with default configuration
    print("Creating default maze...")
    maze = bsAntMaze()
    
    # Print the default maze
    print("\nDefault maze layout:")
    print(maze.get_maze())
    
    # Print start and goal positions
    print(f"\nStart position: {maze.get_start_position()}")
    print(f"Goal position: {maze.get_goal_position()}")
    
    # Create a custom maze
    print("\nCreating custom maze...")
    custom_maze = [
        [1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1]
    ]
    maze.create_maze(custom_maze)
    
    # Set start and goal positions
    maze.set_start_position((1, 1))
    maze.set_goal_position((5, 5))
    
    # Print the custom maze
    print("\nCustom maze layout:")
    print(maze.get_maze())
    print(f"Start position: {maze.get_start_position()}")
    print(f"Goal position: {maze.get_goal_position()}")
    
    # Save maze to a text file
    file_path = "custom_maze.txt"
    maze.save_to_txt(file_path)
    print(f"\nMaze saved to {file_path}")
    
    # Create a new maze with custom configuration
    print("\nCreating maze with custom configuration...")
    config = bsAntMazeConfig(
        wall_height=0.8,
        wall_width=0.15,
        cell_size=1.2,
        ant_scale=0.7
    )
    
    # Change colors for visualization
    config.set_color("wall", (0.5, 0.5, 0.5))  # Darker gray walls
    config.set_color("goal", (0.0, 1.0, 0.0))  # Bright green goal
    
    # Print the configuration
    print("\nCustom configuration:")
    print(config.to_dict())
    
    # Load the saved maze
    print(f"\nLoading maze from {file_path}...")
    new_maze = bsAntMaze(config)
    new_maze.build_from_txt(file_path)
    
    # Print the loaded maze
    print("\nLoaded maze layout:")
    print(new_maze.get_maze())
    print(f"Start position: {new_maze.get_start_position()}")
    print(f"Goal position: {new_maze.get_goal_position()}")


if __name__ == "__main__":
    main()
