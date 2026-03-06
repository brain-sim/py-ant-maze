# py_ant_maze

Core Python package for maze parsing, validation, editing, serialization, runtime queries, and 2D image conversion.

## Install

```bash
cd py_ant_maze
pip install -e .
```

## Architecture

### 1) Immutable + mutable model

- `Maze`: immutable validated maze object for runtime and serialization.
- `MazeDraft`: mutable editing surface (`thaw()` -> edit -> `freeze()`).

### 2) Handler-based maze-type system

- `core/handlers.py` defines the handler interface.
- `core/registry.py` maps `maze_type` -> concrete handler.
- `mazes/two_d/*` and `mazes/three_d/*` implement per-type config/layout parsing and validation.

### 3) Runtime utilities on top of `Maze`

- `runtime/MazeRuntime`: rectangular cell view + element semantics index.
- `runtime/MazeSpatialRuntime`: wall-segment spatial queries (distance, sampling), currently for 2D `occupancy_grid` and `edge_grid`.
- `runtime/MazeFrameTransformer`: `config` vs `simulation` frame conversion.

## Code Structure

```text
src/py_ant_maze/
├── __init__.py                  # Public API exports
├── maze.py                      # Maze and MazeDraft
├── core/
│   ├── handlers.py              # MazeTypeHandler interface
│   ├── registry.py              # Handler registration/lookup
│   ├── parsing/                 # Shared parsing helpers
│   └── structures/              # ElementSet and grid parsing/formatting
├── mazes/
│   ├── two_d/                   # occupancy_grid, edge_grid, radial_arm
│   └── three_d/                 # occupancy_grid_3d, edge_grid_3d, radial_arm_3d
├── runtime/                     # Runtime, semantics, spatial queries, frames
└── io/                          # YAML dump helpers (literal blocks, token quoting)
```

## Supported Maze Types

- `occupancy_grid`
- `edge_grid`
- `radial_arm`
- `occupancy_grid_3d`
- `edge_grid_3d`
- `radial_arm_3d`

3D types require at least two levels and support validated `elevator`/`escalator` connectors.

## Typical Usage

```python
from py_ant_maze import Maze

# Parse and inspect
maze = Maze.from_file("maze.yaml")
print(maze.to_text(with_grid_numbers=True))

# Edit through draft API
draft = maze.thaw()
draft.set_cell(1, 2, 0)  # for occupancy_grid / edge_grid cell layers
updated = draft.freeze()
updated.to_file("updated_maze.yaml", with_grid_numbers=True)
```

Additional draft mutators:

- `set_wall(row, col, value, wall_type, level=...)`
- `set_arm_cell(arm, row, col, value, level=...)`
- `set_arm_wall(arm, row, col, value, wall_type, level=...)`

For `*_3d`, `level` is required. For wall editing, `wall_type` must be `vertical` or `horizontal`.

## Runtime Usage

```python
from py_ant_maze import Maze
from py_ant_maze.runtime import MazeRuntime, MazeSpatialRuntime

maze = Maze.from_file("maze.yaml")
runtime = MazeRuntime.from_maze(maze)
print(runtime.rows, runtime.cols, runtime.cell_size)

spatial = MazeSpatialRuntime.from_maze(maze)  # occupancy_grid or edge_grid
distances = spatial.get_wall_distances([[0.0, 0.0, 0.0]])
```

Runtime semantics index example:

```python
start_values = runtime.semantics.values_for_cell_names(["start", "spawn"])
wall_values = runtime.semantics.values_for_wall_names(["wall", "wall_1"])
```

## Notes

- YAML serialization preserves readable block formatting (`|`) for layouts and quoted single-char tokens.
- Examples live under `py_ant_maze/examples/`.
