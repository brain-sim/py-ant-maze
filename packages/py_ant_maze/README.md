# py_ant_maze

Python library for defining and manipulating maze structures using YAML configuration.

## Installation

```bash
pip install -e .
```

## Maze Types

| Type | Description |
|------|-------------|
| `occupancy_grid` | Classic blocked/open cell representation |
| `edge_grid` | Thin walls between cells |

## YAML Format

```yaml
maze_type: occupancy_grid
config:
  cell_elements:
    - name: wall
      token: '#'
    - name: open
      token: '.'
layout:
  grid: |
    ___ 0 1 2 3 4
    0 | # # # # #
    1 | # . . . #
    2 | # # # # #
```

### Structure

- `maze_type`: Required. Either `occupancy_grid` or `edge_grid`
- `config`: Element definitions with `name`, `token`, and optional `value`
- `layout`: Grid data using element tokens

### Elements

- `name`: Unique identifier
- `token`: Single character (non-whitespace, not `|`)
- `value`: Optional integer (auto-assigned if omitted)

Reserved defaults: `open=0`, `wall=1`

### Grid Format

Grids can be:
- YAML block string with `|`
- List of strings
- List of lists of single characters

Grid numbering (optional):
- Header row: `___ 0 1 2 3`
- Row labels: `0 | # . . #`

## Config Layout Rules

**YAML Structure**
- Top-level keys: `maze_type`, `config`, `layout`
- `maze_type` is required

**Element Definition**
- Required: `name`, `token`
- Optional: `value` (auto-assigned if omitted)
- `token` must be a single, non-whitespace character (cannot be `|`)
- Reserved defaults: `open=0`, `wall=1`
- Values must be unique within each element set

**Occupancy Grid**
- `config.cell_elements`: cell tokens (required)
- `layout.grid`: cell grid

**Edge Grid**
- `config.cell_elements`: cell tokens (required)
- `config.wall_elements`: wall tokens (required)
- `layout.cells`: cell grid
- `layout.walls.vertical`: height × (width + 1)
- `layout.walls.horizontal`: (height + 1) × width

**Grid Parsing**
- All rows must have the same number of cells
- Tokens must match the corresponding element set
- Whitespace is ignored when parsing tokens

```python
from py_ant_maze import Maze

maze = Maze.from_text(yaml_text)
maze = Maze.from_file("maze.yaml")

print(maze.to_text(with_grid_numbers=True))
maze.to_file("output.yaml", with_grid_numbers=True)
```

## Edge Grid Example

```yaml
maze_type: edge_grid
config:
  cell_elements:
    - name: open
      token: '.'
  wall_elements:
    - name: wall
      token: '#'
    - name: empty
      token: '-'
layout:
  cells: |
    . . .
    . . .
  walls:
    vertical: |
      # - - #
      # - - #
    horizontal: |
      # # #
      - - -
      # # #
```

Wall grid dimensions:
- `vertical`: height × (width + 1)
- `horizontal`: (height + 1) × width
