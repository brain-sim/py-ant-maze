# py_ant_maze

Python package for maze definitions, validation, editing, and YAML serialization.

## Install

```bash
pip install -e .
```

## Public API

```python
from py_ant_maze import Maze, MazeDraft

maze = Maze.from_file("maze.yaml")
print(maze.to_text(with_grid_numbers=True))

# Mutable editing surface

draft = maze.thaw()
draft.set_cell(1, 2, 0)
updated = draft.freeze()
updated.to_file("updated_maze.yaml")
```

`Maze` is immutable. `MazeDraft` is mutable and validates on `freeze()`.

## Supported Maze Types

- `occupancy_grid`
- `edge_grid`
- `radial_arm`
- `occupancy_grid_3d`
- `edge_grid_3d`
- `radial_arm_3d`

## YAML Shape

Top-level keys:
- `maze_type`
- `config`
- `layout`

Minimal example:

```yaml
maze_type: occupancy_grid
config:
  cell_elements:
    - name: open
      token: '.'
  wall_elements:
    - name: wall
      token: '#'
layout:
  grid: |
    # # #
    # . #
    # # #
```

## Editing Helpers (`MazeDraft`)

- `set_cell(row, col, value, level=...)`
- `set_wall(row, col, value, wall_type, level=...)`
- `set_arm_cell(arm, row, col, value, level=...)`
- `set_arm_wall(arm, row, col, value, wall_type, level=...)`

For 3D types, `level` is required. For edge/radial wall editing, `wall_type` must be `vertical` or `horizontal`.

## Package Layout

- `src/py_ant_maze/maze.py`: `Maze` and `MazeDraft`
- `src/py_ant_maze/core/`: handler interfaces, registry, shared structures, parsing helpers
- `src/py_ant_maze/mazes/two_d/`: 2D maze handlers
- `src/py_ant_maze/mazes/three_d/`: 3D maze handlers
- `src/py_ant_maze/io/`: YAML serialization helpers
