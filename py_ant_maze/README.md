# py_ant_maze

Python package for maze definitions, validation, editing, and YAML serialization.

## Install

```bash
pip install -e .
```

## Public API

```python
from py_ant_maze import (
    Maze,
    MazeDraft,
    image_to_yaml_file,
    infer_maze_yaml_from_image,
)

maze = Maze.from_file("maze.yaml")
print(maze.to_text(with_grid_numbers=True))

# Mutable editing surface

draft = maze.thaw()
draft.set_cell(1, 2, 0)
updated = draft.freeze()
updated.to_file("updated_maze.yaml")

# 2D image -> YAML (occupancy_grid / edge_grid)
yaml_text = infer_maze_yaml_from_image("maze-layout.png", maze_type="auto")
written = image_to_yaml_file("maze-layout.png", "inferred.yaml", maze_type="edge_grid")
```

`Maze` is immutable. `MazeDraft` is mutable and validates on `freeze()`.

## Image Inversion Scope

- maze types: `occupancy_grid`, `edge_grid`
- dimensionality: 2D only
- source: layout image (best effort for editor-exported images)
- generated names/tokens/values are canonical defaults

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
- `src/py_ant_maze/convert_img2config/`: 2D image-to-YAML inversion pipeline
- `src/py_ant_maze/core/`: handler interfaces, registry, shared structures, parsing helpers
- `src/py_ant_maze/mazes/two_d/`: 2D maze handlers
- `src/py_ant_maze/mazes/three_d/`: 3D maze handlers
- `src/py_ant_maze/io/`: YAML serialization helpers
