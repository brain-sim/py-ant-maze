# py-ant-maze

A Python package for creating and managing ant maze environments.

## Table of Contents

1. [Installation](#installation)
2. [Features](#features)
3. [Basic Usage](#basic-usage)
4. [Maze Creation](#maze-creation)
5. [Configuration](#configuration)
6. [Visualization](#visualization)
7. [Examples](#examples)
8. [Development and Contribution](#development-and-contribution)
9. [License](#license)

## Installation

### From PyPI

```bash
pip install py-ant-maze
```

### From Source

```bash
git clone https://github.com/brain-sim/py-ant-maze.git
cd py-ant-maze
pip install -e .
```

### For Isaac Sim Users

Run the following in Window->Script Editor:

```Python
import os
from pathlib import Path
import omni.kit.pipapi

def install_local_package(package_path):
    package_path = Path(package_path).resolve()
    if not package_path.exists():
        print(f"Package path does not exist: {package_path}")
        return

    print(f"Installing local package from: {package_path}")
    result = omni.kit.pipapi.call_pip(["install", str(package_path)])

    if result == 0:
        print("Package installed successfully!")
    else:
        print(f"pip install failed with exit code {result}")

if __name__ == "__main__":
    # Replace with the path to your local package
    install_local_package("/path/to/py-ant-maze")
```

## Features

- Create customizable maze environments
- Load and save maze configurations from/to text files
- Configure physical properties and visualization settings
- Visualize mazes with customizable colors and styles
- Support for both Python and Isaac Sim environments

## Basic Usage

Here's a simple example of how to use the `bsAntMaze` class:

```python
from py_ant_maze import bsAntMaze, bsAntMazeConfig

# Create a maze with default configuration
maze = bsAntMaze()

# Print the default maze
print(maze.get_maze())
```

## Maze Creation

There are multiple ways to create a maze:

### Using a 2D Array

```python
custom_maze = [
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1]
]
maze = bsAntMaze()
maze.create_maze(custom_maze)

# Set start and goal positions
maze.set_start_position((1, 1))
maze.set_goal_position((3, 3))
```

### Loading from a Text File

Create a text file with the maze layout:

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

Then load it:

```python
maze = bsAntMaze()
maze.build_from_txt("maze_file.txt")
```

### Saving to a Text File

```python
maze.save_to_txt("output_maze.txt")
```

## Configuration

The `bsAntMazeConfig` class allows customization of various maze properties:

```python
config = bsAntMazeConfig(
    wall_height=0.8,        # Height of maze walls
    wall_width=0.15,        # Width/thickness of maze walls
    cell_size=1.2,          # Size of each cell in the maze
    ant_scale=0.7,          # Scale factor for the ant agent
    render_walls=True,      # Whether to render walls in visualization
    custom_settings={}      # Additional custom configuration settings
)

# Create a maze with custom configuration
maze = bsAntMaze(config)
```

### Updating Configuration

```python
# Update individual settings
config.wall_height = 1.0

# Update multiple settings at once
config.update({
    'wall_height': 0.8,
    'custom_param': 123
})
```

### Customizing Colors

```python
# Set colors for visualization (RGB values between 0 and 1)
config.set_color('wall', (0.5, 0.5, 0.5))   # Gray walls
config.set_color('floor', (0.9, 0.9, 0.9))  # Light gray floor
config.set_color('ant', (0.2, 0.4, 0.8))    # Blue ant
config.set_color('goal', (0.0, 0.8, 0.0))   # Green goal
config.set_color('start', (0.8, 0.0, 0.0))  # Red start
```

## Visualization

The package includes a visualization module that uses matplotlib to create and save maze visualizations:

```python
from py_ant_maze import bsAntMaze
from py_ant_maze.examples.maze_visualization import visualize_maze

# Create and configure your maze
maze = bsAntMaze()
maze.create_maze([
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 1, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1]
])
maze.set_start_position((1, 1))
maze.set_goal_position((3, 3))

# Visualize and save the maze
visualize_maze(
    maze,
    title="My Custom Maze",
    save_path="maze_visualization.png"  # Optional: save as high-quality image
)
```

The visualization includes:
- Walls and floor spaces with customizable colors
- Start and goal positions marked with colored markers
- Grid lines for better spatial reference
- Proper scaling based on cell size
- High-quality image output (300 DPI) when saving

## Examples

The package includes several examples in the `examples` directory:

- `basic_usage.py`: Simple demonstration of creating and manipulating maze environments
- `maze_visualization.py`: Example of visualizing and saving maze layouts

## Development and Contribution

### Running Tests

```