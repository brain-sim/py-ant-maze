# maze_generator

Generate USD files from [py-ant-maze](../py_ant_maze) YAML configurations.

## Installation

```bash
pip install -e .
```

Requires `py-ant-maze` and `usd-core` (OpenUSD).

## Usage

### Python API

```python
from maze_generator import maze_to_usd

# From a YAML file
maze_to_usd("maze.yaml", "output.usda")

# Merge walls by element name
maze_to_usd("maze.yaml", "output.usda", merge=True)
```

### CLI

```bash
maze-generator input.yaml -o output.usda
maze-generator input.yaml --merge

# Or via python -m
python -m maze_generator input.yaml -o output.usda
```

Options:
- `-o, --output`: Output file path (default: `<input>.usda`)
- `--merge`: Merge walls sharing the same element name into one mesh

### Physical Dimensions

Dimensions are defined in the maze YAML config section:

```yaml
maze_type: occupancy_grid
config:
  cell_size: 1.0       # meters (default: 1.0)
  wall_height: 0.5     # meters (default: 0.5)
  cell_elements:
    - name: open
      token: "."
    - name: wall
      token: "#"
```

For `edge_grid`, you can also set `wall_thickness`:

```yaml
maze_type: edge_grid
config:
  cell_size: 1.0
  wall_height: 0.5
  wall_thickness: 0.05  # meters (default: 0.05)
  cell_elements: [...]
  wall_elements: [...]
```

### Materials

Walls are assigned colors by their element name:
- `wall` → gray
- `door` → brown
- Other elements → auto-assigned from a palette

Override with a custom material map:

```python
maze_to_usd(
    "maze.yaml",
    "output.usda",
    material_map={"wall": (0.8, 0.8, 0.8), "door": (0.4, 0.2, 0.0)},
)
```

## Supported Maze Types

| Type | Description |
|------|-------------|
| `occupancy_grid` | Non-open cells become full-size wall boxes |
| `edge_grid` | Vertical/horizontal wall grids become thin wall boxes |

## Viewing Output

```bash
usdview output.usda
```

Or load the `.usda` file in Isaac Sim, Blender, or any USD-compatible tool.
