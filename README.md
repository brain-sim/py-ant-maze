# py-ant-maze

A Python package for creating and managing ant maze environments.

## Installation

You can install the package directly from PyPI:

```bash
pip install py-ant-maze
```

Or install from source:

```bash
git clone https://github.com/brain-sim/py-ant-maze.git
cd py-ant-maze
pip install -e .
```

## Features

- Create customizable maze environments
- Load and save maze configurations from/to text files
- Configure physical properties and visualization settings
- Visualize mazes with customizable colors and styles

## Basic Usage

Here's a simple example of how to use the `bsAntMaze` class:

```python
from py_ant_maze import bsAntMaze, bsAntMazeConfig

# Create a maze with default configuration
maze = bsAntMaze()

# Print the default maze
print(maze.get_maze())

# Create a custom maze
custom_maze = [
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1]
]
maze.create_maze(custom_maze)

# Set start and goal positions
maze.set_start_position((1, 1))
maze.set_goal_position((3, 3))

# Save maze to a text file
maze.save_to_txt("custom_maze.txt")

# Load a maze from a text file
new_maze = bsAntMaze()
new_maze.build_from_txt("custom_maze.txt")
```

## Customizing the Maze Configuration

You can customize the physical properties and visualization settings:

```python
from py_ant_maze import bsAntMazeConfig

# Create a custom configuration
config = bsAntMazeConfig(
    wall_height=0.8,
    wall_width=0.15,
    cell_size=1.2,
    ant_scale=0.7
)

# Change colors for visualization
config.set_color("wall", (0.5, 0.5, 0.5))  # Darker gray walls
config.set_color("goal", (0.0, 1.0, 0.0))  # Bright green goal

# Create a maze with the custom configuration
maze = bsAntMaze(config)
```

## Creating a Text File Maze

You can create a maze using a simple text file format:

```
11111
10001
11101
10001
11111
```

Or with explicit start (S) and goal (G) positions:

```
11111
1S001
11101
100G1
11111
```

Then load it with:

```python
maze = bsAntMaze()
maze.build_from_txt("maze_file.txt")
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
