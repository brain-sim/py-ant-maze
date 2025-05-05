"""
Example of visualizing the AntMaze environment using matplotlib.

This example demonstrates how to visualize a maze configuration
using matplotlib for a simple 2D representation.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from py_ant_maze import bsAntMaze, bsAntMazeConfig


def visualize_maze(maze, start_pos, goal_pos, config):
    """
    Visualize the maze using matplotlib.
    
    Args:
        maze (np.ndarray): 2D array representing the maze
        start_pos (tuple): (row, col) start position
        goal_pos (tuple): (row, col) goal position
        config (bsAntMazeConfig): Configuration object with visualization settings
    """
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Get colors from config
    colors = config.colors
    wall_color = colors['wall']
    floor_color = colors['floor']
    start_color = colors['start']
    goal_color = colors['goal']
    
    # Set background color
    ax.set_facecolor(floor_color)
    
    # Draw walls
    for i in range(maze.shape[0]):
        for j in range(maze.shape[1]):
            if maze[i, j] == 1:  # Wall
                ax.add_patch(Rectangle((j, maze.shape[0] - i - 1), 1, 1, 
                                      facecolor=wall_color, edgecolor='black', linewidth=0.5))
    
    # Draw start and goal positions
    start_row, start_col = start_pos
    goal_row, goal_col = goal_pos
    
    # Convert to plotting coordinates
    start_y = maze.shape[0] - start_row - 1
    goal_y = maze.shape[0] - goal_row - 1
    
    # Draw start position (circle)
    start_circle = plt.Circle((start_col + 0.5, start_y + 0.5), 0.3, color=start_color)
    ax.add_patch(start_circle)
    
    # Draw goal position (star)
    ax.scatter(goal_col + 0.5, goal_y + 0.5, color=goal_color, marker='*', s=500, zorder=5)
    
    # Set grid
    ax.grid(True, linestyle='-', alpha=0.2)
    ax.set_xticks(np.arange(0, maze.shape[1] + 1, 1))
    ax.set_yticks(np.arange(0, maze.shape[0] + 1, 1))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
    # Set limits and aspect ratio
    ax.set_xlim(0, maze.shape[1])
    ax.set_ylim(0, maze.shape[0])
    ax.set_aspect('equal')
    
    # Add title
    plt.title('Ant Maze Environment')
    
    return fig, ax


def main():
    """
    Main function to demonstrate maze visualization.
    """
    # Create a custom maze
    custom_maze = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    
    # Create maze object and set the maze
    maze = bsAntMaze()
    maze.create_maze(custom_maze)
    
    # Set start and goal positions
    maze.set_start_position((1, 1))
    maze.set_goal_position((5, 7))
    
    # Create custom configuration with different colors
    config = bsAntMazeConfig(
        wall_height=0.8,
        wall_width=0.15,
        cell_size=1.2
    )
    
    # Customize colors
    config.set_color('wall', (0.5, 0.5, 0.7))    # Bluish walls
    config.set_color('floor', (0.95, 0.95, 0.9))  # Light cream floor
    config.set_color('start', (1.0, 0.3, 0.3))    # Brighter red start
    config.set_color('goal', (0.2, 0.8, 0.2))     # Brighter green goal
    
    # Visualize the maze
    fig, ax = visualize_maze(
        maze.get_maze(),
        maze.get_start_position(),
        maze.get_goal_position(),
        config
    )
    
    # Save the visualization
    plt.savefig('maze_visualization.png', dpi=200, bbox_inches='tight')
    print("Maze visualization saved as 'maze_visualization.png'")
    
    # Show the visualization
    plt.show()


if __name__ == "__main__":
    main()