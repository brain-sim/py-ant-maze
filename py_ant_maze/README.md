# py_ant_maze

Python package for maze definitions, validation, editing, and runtime utilities.

## Install

```bash
pip install -e .
```

## Design

`Maze` is the single source of truth.

- `Maze`: immutable parsed maze object for runtime and serialization.
- `MazeDraft`: mutable editing surface used only when changing maze content.
- `py_ant_maze.runtime`: derived runtime views and fast query utilities built from a `Maze` object.

Runtime code should consume `Maze`, not config file paths.

## Public API

```python
from py_ant_maze import (
    Maze,
    MazeDraft,
    config_file_to_image,
    maze_to_image_file,
    image_to_yaml_file,
    infer_maze_yaml_from_image,
)

maze = Maze.from_file("maze.yaml")
print(maze.to_text(with_grid_numbers=True))

draft = maze.thaw()
draft.set_cell(1, 2, 0)
updated = draft.freeze()
updated.to_file("updated_maze.yaml")

yaml_text = infer_maze_yaml_from_image("maze-layout.png", maze_type="auto")
written = image_to_yaml_file("maze-layout.png", "inferred.yaml", maze_type="edge_grid")

image_path = config_file_to_image("maze.yaml", "maze-layout.png")
maze_image_path = maze_to_image_file(updated, "updated-maze-layout.png")
```

## Runtime

### Build Runtime View From `Maze`

```python
from py_ant_maze import Maze
from py_ant_maze.runtime import MazeRuntime

maze = Maze.from_file("maze.yaml")
runtime = MazeRuntime.from_maze(maze)

print(runtime.maze_type)
print(runtime.rows, runtime.cols)
print(runtime.cell_size)
```

`runtime` contains derived metadata:
- `cells`: rectangular integer cell grid view.
- `semantics`: generic name -> values index from `cell_elements` and `wall_elements`.

```python
start_values = runtime.semantics.values_for_cell_names(["start", "spawn"])
wall_values = runtime.semantics.values_for_wall_names(["wall", "wall_1"])
```

Semantic meaning stays simulator/task-specific.

### Frame Conversion

```python
from py_ant_maze.runtime import MazeFrameTransformer

tf = MazeFrameTransformer("simulation")
x, y = tf.cell_center(row=2, col=3, rows=runtime.rows, cell_size=runtime.cell_size)
```

Supported frames:
- `config`: raw YAML/image indexing
- `simulation`: Y-only flip (`(x, y) -> (x, H - y)`)

### Precomputed Proximity Cost

```python
from py_ant_maze.runtime import CostSemanticTemplate, MazeCostCalculator

# Example: use most wall semantics, but exclude empty edges.
template = CostSemanticTemplate(
    include_all_walls=True,
    wall_exclude_names=("empty",),
)

calc = MazeCostCalculator.from_runtime(
    runtime,
    semantic_template=template,
    max_cost=1.0,
    distance_decay=0.75,
)

cost = calc.cost_at_xy([x, y], frame="simulation")
dist = calc.distance_at_xy([x, y], frame="simulation")
```

Cost function:
- `cost = max_cost * exp(-distance / distance_decay)`
- closer to selected sources => higher cost

Precomputed arrays:
- `distance_lattice`, `cost_lattice` (half-cell lattice)
- `distance_cells`, `cost_cells` (cell-center view)

`CostSemanticTemplate` defaults select nothing. If no sources are resolved, calculator creation raises `ValueError`.

## Image Inversion Scope

- maze types: `occupancy_grid`, `edge_grid`
- dimensionality: 2D only
- source: layout image (best effort for editor-exported images)
- generated names/tokens/values are canonical defaults

## Config-to-Image Scope

- maze types: `occupancy_grid`, `edge_grid`
- dimensionality: 2D only
- style: mirrors maze editor rendering rules for cell size, wall thickness, and color mapping
- source of truth: Python renderer implementation in this package

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
- `src/py_ant_maze/runtime/runtime.py`: `MazeRuntime`
- `src/py_ant_maze/runtime/cost.py`: precomputed cost field calculator
- `src/py_ant_maze/runtime/frames.py`: frame helpers
- `src/py_ant_maze/runtime/extractors.py`: maze-type cell extraction strategies
- `src/py_ant_maze/runtime/semantics.py`: generic semantics index builder
- `src/py_ant_maze/convert_img2config/`: 2D image-to-YAML inversion pipeline
- `src/py_ant_maze/convert_config2img/`: 2D config/YAML-to-image rendering pipeline
- `src/py_ant_maze/core/`: handler interfaces, registry, shared structures, parsing helpers
- `src/py_ant_maze/mazes/two_d/`: 2D maze handlers
- `src/py_ant_maze/mazes/three_d/`: 3D maze handlers
- `src/py_ant_maze/io/`: YAML serialization helpers
