# maze_editor

Browser maze editor built with React + Vite + Pyodide.

Runs `py_ant_maze` directly in the browser by loading a local wheel into Pyodide, so YAML parsing/validation/editing behavior matches the Python package.

## Features

- Edit all maze families:
  - 2D: `occupancy_grid`, `edge_grid`, `radial_arm`
  - 3D: `occupancy_grid_3d`, `edge_grid_3d`, `radial_arm_3d`
- Switch 2D/3D mode and maze family from one UI.
- Visual paint tools for cells/walls with click-drag editing.
- Radial-arm controls (arm count, arm size, hub angle, hub size, circular/polygon hub).
- 3D level controls (level selection and level count changes).
- Add new cell/wall elements with token shortcuts.
- YAML editor + format + parse ("Sync to Grid").
- YAML import/export and PNG export (for 3D, exports each level).

## Architecture

```text
src/
├── App.tsx                      # Main shell and panel orchestration
├── services/pyodide.ts          # Pyodide init + Python mutation helpers
├── hooks/
│   ├── useMaze.ts               # Main state/actions for parse/edit/create
│   ├── useFileOperations.ts     # Upload/download/export image
│   └── useKeyboardShortcuts.ts  # Token key -> element selection
├── components/
│   ├── editor/                  # Code panel + visual panel wrappers
│   ├── controls/                # Type, size, level, palette, add-element controls
│   ├── layout/                  # Header/loading shells
│   ├── MazeGrid.tsx             # Occupancy/edge rendering + paint
│   └── RadialArmGrid.tsx        # SVG radial-arm rendering + paint
├── constants/defaults.ts        # Default YAML templates and render constants
└── types/maze.ts                # Shared TS maze types
```

Data flow:

1. `useMaze` loads Pyodide and installs `py_ant_maze` wheel.
2. Python-side helpers parse YAML into normalized JSON for the UI.
3. UI actions call Python mutation helpers and round-trip updated YAML/data back.

## Use the Editor

### Option 1: Deployed

Open https://maze.yihao.one.

### Option 2: Local Development

Prerequisites:

- Node.js 18+
- Python 3.10+ (for building the wheel consumed by Pyodide)

1. Build the wheel:

```bash
cd ../py_ant_maze
python -m build
```

2. Start the editor:

```bash
cd ../maze_editor
npm install
npm run dev
```

`predev` copies `../py_ant_maze/dist/py_ant_maze-0.1.1-py3-none-any.whl` into `public/` automatically.

Then open the Vite URL shown in terminal (usually `http://localhost:5173`).

## Editing Workflow

1. Choose maze type (and radial hub shape when relevant).
2. Paint cells/walls in the visual grid.
3. Use element palette or keyboard token shortcuts for fast selection.
4. Edit YAML directly in the code panel as needed.
5. `Format` and `Sync to Grid` to normalize and re-parse.
6. Export YAML or PNG from the toolbar.

## Demo Gallery

| Demo | Preview |
| --- | --- |
| Maze families and templates | ![Maze families and templates](maze_editor/media/maze_types.gif) |
| 2D and 3D editing | ![2D and 3D editing](maze_editor/media/2d_3d_mazes.gif) |
| Add start/end points | ![Add start/end points](maze_editor/media/exp_add_start_end.gif) |
| Occupancy cell size controls | ![Occupancy cell size controls](maze_editor/media/occupancy_cell_size.gif) |
| Paint occupancy cells | ![Paint occupancy cells](maze_editor/media/paint_cells.gif) |
| Edge-grid editing | ![Edge-grid editing](maze_editor/media/edge_grid.gif) |
| Add elements and connectors | ![Add elements and connectors](maze_editor/media/add_elements.gif) |
| Radial-arm editing | ![Radial-arm editing](maze_editor/media/radial_arm.gif) |
| Radial-arm polygon editing | ![Radial-arm polygon editing](maze_editor/media/radial_arm_polygon.gif) |
| Save YAML config | ![Save YAML config](maze_editor/media/save_config.gif) |
| Save PNG image | ![Save PNG image](maze_editor/media/save_image.gif) |

