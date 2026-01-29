# py-ant-maze

Minimal utilities for maze definitions.

## Install

```bash
pip install -e .
```

## Maze Format

The configuration file is YAML with three top-level keys:

- `maze_type` selects the maze representation.
- `config` lists elements and their tokens.
- `layout` contains the grids using those tokens.

Each element entry includes `name` and `token`. `value` is optional; when omitted,
values are auto-assigned in order, with `open=0` and `wall=1` reserved by default.
If you need stable IDs across edits, set explicit values.

Layout rows may be plain or use grid numbers with a table-style header and row labels.
Grid numbers are padded to the widest index; for large grids (size > 100), numbers
are shown every 10 rows/columns. The header uses `_` as a visible padding character.

### Maze Types

- `occupancy_grid`: classic blocked/open cells.
- `edge_grid`: thin walls between cells (vertical and horizontal walls).

## Config Layout Rules

**YAML structure**
- Top-level keys: `maze_type`, `config`, `layout`.
- `maze_type` is required.

**Element definition**
- Required: `name`, `token`.
- Optional: `value` (auto-assigned if omitted).
- `token` must be a single, non-whitespace character and cannot be `|`.
- `open` defaults to value `0`. `wall` defaults to value `1` when present.
- Values must be unique within each element set.

**Occupancy Grid**
- `config.cell_elements` defines the cell tokens (required).
- `layout.grid` holds the cell grid.

**Edge Grid**
- `config.cell_elements` defines cell tokens (required).
- `config.wall_elements` defines wall tokens (required).
- `layout.cells` holds the cell grid.
- `layout.walls.vertical` is `height x (width+1)`.
- `layout.walls.horizontal` is `(height+1) x width`.

**Grid format**
- Grids can be:
  - a YAML block string (`|`) containing the grid, or
  - a list of strings, or
  - a list of lists of single-character strings.
- All rows must have the same number of cells.
- Tokens must match the corresponding element set.

**Grid numbering (optional)**
- You may include a header row and row labels using the `|` separator:
  - Header example: `___ 0 1 2 3`
  - Row example: `0 | # . . #`
- Use `_` as the explicit padding character in the header (and for skipped row labels) to keep alignment.
- For large grids (>100 rows/cols), show numbers every 10; fill the rest with `_`.

**Spacing**
- Whitespace is ignored when parsing tokens, so spacing is only for readability.
- Prefer spaces (not tabs) inside the block string for consistent YAML parsing.

## Usage

```python
from py_ant_maze import Maze

text = """
maze_type: occupancy_grid
config:
  cell_elements:
    - name: wall
      token: "#"
      value: 1
    - name: open
      token: "."
      value: 0
layout:
  grid: |
    ___ 0 1 2 3 4
    0 | # # # # #
    1 | # . . . #
    2 | # # # # #
"""

maze = Maze.from_text(text)
print(maze.to_text(with_grid_numbers=True))

maze.to_file("maze.yaml", with_grid_numbers=True)
maze2 = Maze.from_file("maze.yaml")
```

### Edge Grid Example

```yaml
maze_type: edge_grid
config:
  cell_elements:
    - name: open
      token: "."
  wall_elements:
    - name: wall
      token: "#"
    - name: open
      token: "."
    - name: door
      token: "D"
layout:
  cells: |
    . . .
    . . .
    . . .
  walls:
    vertical: |
      # # # #
      # . D #
      # # # #
    horizontal: |
      # # #
      # . #
      # . #
      # # #
```
