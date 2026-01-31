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
| `radial_arm` | Center hub with multiple arms (each arm has its own edge-style grid) |

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

- `maze_type`: Required. One of `occupancy_grid`, `edge_grid`, or `radial_arm`
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

**Radial Arm**
- `config.cell_elements`: shared cell tokens (required)
- `config.wall_elements`: shared wall tokens (required)
- `layout.center_hub`: hub specification (required)
  - `center_hub.shape`: `circular` or `polygon`
  - `center_hub.angle_degrees`: span of the hub (default 360)
  - `center_hub.radius`: circular hub size (must meet minimum based on sum of arm widths)
  - `center_hub.side_length`: polygon hub side length (must meet minimum based on max arm width)
  - `center_hub.sides`: number of polygon sides (defaults to # of arms)
- `layout.arms`: list of arm layouts (required)
  - `arm.layout.cells`: cell grid for this arm (arm_width × length)
  - `arm.layout.walls.vertical`: wall grid (arm_width × (length + 1))
  - `arm.layout.walls.horizontal`: wall grid ((arm_width + 1) × length)
  - arm width is the number of rows in `arm.layout.cells` (arms may have different widths)

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

## Radial Arm Example

```yaml
maze_type: radial_arm
config:
  cell_elements:
    - name: open
      token: '.'
  wall_elements:
    - name: wall
      token: '#'
    - name: open
      token: '.'
layout:
  center_hub:
    shape: circular
    angle_degrees: 180
    radius: 2.0
  arms:
    - layout:
        cells: |
          . . . .
        walls:
          vertical: |
            # # # # #
          horizontal: |
            # # # #
            # # # #
    - layout:
        cells: |
          . . . .
          . . . .
          . . . .
        walls:
          vertical: |
            # # # # #
            # . . . #
            # . . . #
          horizontal: |
            # # # #
            # . . #
            # # # #
            # # # #
```
