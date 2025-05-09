# py-ant-maze: Comprehensive Guide

This guide provides comprehensive information on using the `py-ant-maze` package for creating and managing maze environments.

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Maze Creation](#maze-creation)
4. [Configuration](#configuration)
5. [Examples](#examples)
6. [Development and Contribution](#development-and-contribution)

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

## Examples

The package includes several examples in the `examples` directory:

### Basic Usage Example

See `examples/basic_usage.py` for a simple demonstration of creating and manipulating maze environments.

### Maze Visualization

See `examples/maze_visualization.py` for an example of visualizing the maze using matplotlib.

## Development and Contribution

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Code Style

The project follows PEP 8 style guidelines. You can use Ruff for linting:

```bash
ruff check .
```

### Adding Features

1. Fork the repository
2. Create a feature branch
3. Implement your feature with tests
4. Submit a pull request

### Building Documentation

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation
```
