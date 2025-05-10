"""
Maze visualization example using matplotlib.

This example demonstrates how to:
1. Load a maze and configuration from files
2. Visualize the maze with custom colors
3. Show start and goal positions
"""
import numpy as np
import matplotlib.pyplot as plt
from py_ant_maze import bsAntMaze

def visualize_maze(maze, title="Maze Visualization", save_path=None):
    """
    Visualize the maze using matplotlib.
    
    Args:
        maze: bsAntMaze instance
        title: Plot title
        save_path: Optional path to save the visualization image. If None, image is not saved.
    """
    # Get maze data
    maze_grid = maze.get_maze()
    start_pos = maze.get_start_position()
    goal_pos = maze.get_goal_position()
    config = maze.get_config()
    
    # Get cell size from config
    cell_size = config.dimensions.cell_size
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Get colors from config
    wall_color = config.visuals.get_color('wall')
    floor_color = config.visuals.get_color('floor')
    start_color = config.visuals.get_color('start')
    goal_color = config.visuals.get_color('goal')
    
    # Create color matrix
    colors = np.zeros((maze_grid.shape[0], maze_grid.shape[1], 3))
    for i in range(maze_grid.shape[0]):
        for j in range(maze_grid.shape[1]):
            if maze_grid[i, j] == 1:  # 1 represents walls
                colors[i, j] = wall_color
            else:  # 0 represents floor
                colors[i, j] = floor_color
    
    # Plot the maze with proper scaling
    ax.imshow(colors, extent=[0, maze_grid.shape[1] * cell_size, 0, maze_grid.shape[0] * cell_size])
    
    # Convert positions to cell centers
    start_x = (start_pos[1] + 0.5) * cell_size
    start_y = (maze_grid.shape[0] - start_pos[0] - 0.5) * cell_size
    goal_x = (goal_pos[1] + 0.5) * cell_size
    goal_y = (maze_grid.shape[0] - goal_pos[0] - 0.5) * cell_size
    
    # Plot start and goal positions with proper scaling
    ax.plot(start_x, start_y, 'o', color=start_color, markersize=10, label='Start')
    ax.plot(goal_x, goal_y, 'o', color=goal_color, markersize=10, label='Goal')
    
    # Add grid
    ax.grid(True, which='both', color='gray', linewidth=0.5)
    ax.set_xticks(np.arange(0, maze_grid.shape[1] * cell_size + cell_size, cell_size))
    ax.set_yticks(np.arange(0, maze_grid.shape[0] * cell_size + cell_size, cell_size))
    
    # Set axis labels
    ax.set_xlabel('X (units)')
    ax.set_ylabel('Y (units)')
    
    # Customize plot
    ax.set_title(title)
    ax.legend()
    
    # Save the plot if save_path is provided
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Maze visualization saved to: {save_path}")
    
    # Show plot
    plt.show()

def main():
    # Create maze from config file
    maze = bsAntMaze.from_config_file("example_config.json")
    
    # Create a sample maze layout
    maze_layout = [
        [1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1]
    ]
    maze.create_maze(maze_layout)
    
    # Set start and goal positions
    maze.set_start_position((1, 1))
    maze.set_goal_position((5, 5))
    
    # Visualize the maze and save it
    visualize_maze(maze, "Maze with Custom Configuration", save_path="maze_visualization.png")

if __name__ == "__main__":
    main()