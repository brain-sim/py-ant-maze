# py_ant_maze

Python library for defining and manipulating maze structures using YAML configuration.

## Installation

```bash
pip install -e .
```

## Package Structure

```
py_ant_maze/
  core/
    handlers.py          # MazeTypeHandler interface (parse/validate/serialize/freeze/thaw)
    registry.py          # Maze type registry
    types.py             # Shared type aliases
    structures/          # Core data structures (elements, grids, element sets)
    parsing/             # YAML/spec parsing helpers (levels, connectors, elements)
  mazes/
    two_d/               # 2D maze types (occupancy, edge, radial)
    three_d/             # 3D wrappers + shared multi-level base
  io/                    # YAML serialization helpers
  maze.py                # Maze (immutable) + MazeDraft (mutable)
```

## Design Overview

- **MazeDraft (mutable)**: The editing surface. You can update cells/walls directly or via helper methods,
  then call `freeze()` to produce an immutable snapshot.
- **Maze (immutable)**: A validated, frozen snapshot used by simulators and analysis code.
- **Handlers**: Each maze type is implemented by a `MazeTypeHandler` that:
  - parses config/layout from specs,
  - validates cross-field constraints,
  - serializes back to YAML,
  - freezes/thaws between mutable and immutable forms.
- **Data classes**: Each maze type defines explicit dataclasses for config and layout,
  plus frozen variants for runtime safety.
- **2D vs 3D**:
  - 2D types live under `mazes/two_d/`.
  - 3D types live under `mazes/three_d/` and reuse 2D layout parsing via the shared
    `MultiLevelHandler` base (levels + connectors).

## Understanding the Code

This section explains how the package is organized and how to navigate the codebase.

### Module Overview

```
py_ant_maze/
├── maze.py              # Entry points: Maze (frozen) and MazeDraft (mutable)
├── core/
│   ├── handlers.py      # Abstract MazeTypeHandler interface
│   ├── registry.py      # Handler registry (get_handler, register_handler)
│   ├── types.py         # Type aliases (MazeType, Grid, specs)
│   ├── structures/      # Reusable data structures
│   │   ├── elements.py      # MazeElement, CellElement, WallElement
│   │   ├── element_set.py   # ElementSet / FrozenElementSet collections
│   │   └── grid.py          # Grid parsing (parse_grid) and formatting (format_grid)
│   └── parsing/         # Parsing utilities
│       ├── maze_parsing.py      # parse_config helper
│       ├── level_connectors.py  # Connector parsing for 3D mazes
│       └── multi_level.py       # Level definition parsing
├── mazes/
│   ├── two_d/           # 2D maze type handlers
│   │   ├── occupancy_grid.py  # OccupancyGridHandler
│   │   ├── edge_grid.py       # EdgeGridHandler
│   │   └── radial_arm.py      # RadialArmHandler
│   └── three_d/         # 3D maze type handlers
│       ├── base.py            # MultiLevelHandler base class
│       ├── common.py          # Shared 3D utilities
│       ├── occupancy_grid.py  # OccupancyGrid3DHandler
│       ├── edge_grid.py       # EdgeGrid3DHandler
│       └── radial_arm.py      # RadialArm3DHandler
└── io/
    └── serialization.py # YAML dump utilities
```

### Control Flow

**Loading a Maze:**
```
YAML text
    ↓ yaml.safe_load()
MazeSpec (dict)
    ↓ get_handler(maze_type)
MazeTypeHandler
    ↓ handler.parse_config(spec['config'])
Config dataclass
    ↓ handler.parse_layout(spec['layout'], config)
Layout dataclass
    ↓ handler.freeze(config, layout)
FrozenConfig + FrozenLayout
    ↓
Maze(maze_type, config, layout)
```

**Editing a Maze (MazeDraft):**
```
Maze
    ↓ maze.thaw()
MazeDraft (mutable config/layout)
    ↓ draft.set_cell(row, col, value)
    ↓ draft.set_wall(row, col, value, wall_type)
MazeDraft (modified)
    ↓ draft.freeze()
Maze (new frozen snapshot)
```

**Saving a Maze:**
```
Maze
    ↓ handler.to_spec(config, layout, with_grid_numbers)
MazeSpec (dict)
    ↓ dump_yaml(spec)
YAML text
```

### Key Abstractions

#### MazeTypeHandler (`core/handlers.py`)

Abstract base class that every maze type must implement:

| Method | Purpose |
|--------|---------|
| `parse_config(spec)` | Convert config dict → Config dataclass |
| `parse_layout(spec, config)` | Convert layout dict → Layout dataclass |
| `validate(config, layout)` | Check cross-field constraints |
| `freeze(config, layout)` | Mutable → Frozen (immutable) |
| `thaw(config, layout)` | Frozen → Mutable |
| `config_to_spec(config)` | Config → dict for YAML |
| `layout_to_spec(layout, config, ...)` | Layout → dict for YAML |

Handlers are registered via `register_handler()` and retrieved via `get_handler(maze_type)`.

#### ElementSet / FrozenElementSet (`core/structures/element_set.py`)

Manage collections of maze elements (cells or walls):

- **ElementSet**: Mutable, supports `add()` and lookup by name/token/value
- **FrozenElementSet**: Immutable snapshot with same lookup capabilities
- Both provide `to_list()` for YAML serialization
- `from_list()` handles reserved defaults (e.g., `open=0`, `wall=1`)

#### Grid Utilities (`core/structures/grid.py`)

- `parse_grid(input, element_set)`: Parse text/list into 2D integer grid
- `format_grid(grid, element_set, with_grid_numbers)`: Format grid back to text

### Adding a New Maze Type

1. **Define Config and Layout dataclasses** (mutable + frozen variants)
2. **Create a Handler class** extending `MazeTypeHandler`:
   - Implement all abstract methods
   - Set `maze_type` class attribute
   - Optionally set `aliases` for alternative type names
3. **Register the handler** in `mazes/__init__.py`:
   - Add handler instance to `HANDLERS` tuple
   - Export Config/Layout classes

For 3D types, extend `MultiLevelHandler` instead and implement:
- `parse_level_layout()`
- `level_layout_to_spec()`
- `freeze_level_layout()` / `thaw_level_layout()`
- `freeze_config()` / `thaw_config()`
- `cell_grid_for_location()` (for connector validation)

### Mutable vs Frozen

The package uses a pattern where each data structure has two variants:

| Mutable | Frozen | Purpose |
|---------|--------|---------|
| `ElementSet` | `FrozenElementSet` | Element collections |
| `OccupancyGridConfig` | `FrozenOccupancyGridConfig` | Config dataclasses |
| `EdgeGridLayout` | `FrozenEdgeGridLayout` | Layout dataclasses |
| `MazeDraft` | `Maze` | Top-level maze object |

**MazeDraft** holds mutable config/layout and provides editing methods.
**Maze** holds frozen config/layout for runtime safety.

Transitions:
- `draft.freeze()` → `Maze`
- `maze.thaw()` → `MazeDraft`


## Maze Types

| Type | Description |
|------|-------------|
| `occupancy_grid` / `occupancy_grid_2d` | Classic blocked/open cell representation |
| `edge_grid` / `edge_grid_2d` | Thin walls between cells |
| `radial_arm` / `radial_arm_2d` | Center hub with multiple arms (each arm has its own edge-style grid) |
| `occupancy_grid_3d` | Multi-level occupancy grid |
| `edge_grid_3d` | Multi-level edge grid |
| `radial_arm_3d` | Multi-level radial arm |

## YAML Format

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
    ___ 0 1 2 3 4
    0 | # # # # #
    1 | # . . . #
    2 | # # # # #
```

### Structure

- `maze_type`: Required. One of the 2D or 3D maze types listed above
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
- `config.cell_elements`: non-wall cell tokens (required)
- `config.wall_elements`: wall tokens (required)
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
- `layout.arms`: list of arm layouts (required)
  - `arm.layout.cells`: cell grid for this arm (arm_width × length)
  - `arm.layout.walls.vertical`: wall grid (arm_width × (length + 1))
  - `arm.layout.walls.horizontal`: wall grid ((arm_width + 1) × length)
  - arm width is the number of rows in `arm.layout.cells` (arms may have different widths)

**Grid Parsing**
- All rows must have the same number of cells
- Tokens must match the corresponding element set
- Whitespace is ignored when parsing tokens

## 3D Layouts

3D maze types use a list of levels plus optional connectors between floors.

**Required cell elements (3D only)**
- `elevator` and `escalator` must be defined in `config.cell_elements`

**Level Layouts**
- `layout.levels`: list of per-floor layouts
- Each level entry supports `id` and `layout`

**Connectors**
- `layout.connectors`: list of connector definitions
- `connector.type`: `elevator` or `escalator`
- `connector.from` / `connector.to`: level + coordinates
  - `level`: level index or id
  - `row`, `col`: cell coordinates
  - `arm` (radial arm only): arm index
- Elevators must connect adjacent levels with the same coordinates
- Escalators must connect adjacent levels with different coordinates

Example (occupancy grid 3D):

```yaml
maze_type: occupancy_grid_3d
config:
  cell_elements:
    - name: wall
      token: '#'
    - name: open
      token: '.'
    - name: elevator
      token: 'E'
    - name: escalator
      token: 'S'
layout:
  levels:
    - id: ground
      layout:
        grid: |
          # # #
          # E #
          # # #
    - id: upper
      layout:
        grid: |
          # # #
          # E #
          # # #
  connectors:
    - type: elevator
      from: {level: ground, row: 1, col: 1}
      to: {level: upper, row: 1, col: 1}
```

```python
from py_ant_maze import Maze, MazeDraft

maze = Maze.from_text(yaml_text)
maze = Maze.from_file("maze.yaml")

print(maze.to_text(with_grid_numbers=True))
maze.to_file("output.yaml", with_grid_numbers=True)

# Editing workflow (mutable draft -> immutable snapshot)
draft = MazeDraft.from_text(yaml_text)
draft.set_cell(1, 2, 0)
maze = draft.freeze()

# Round-trip back to a draft if needed
draft = maze.thaw()
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
