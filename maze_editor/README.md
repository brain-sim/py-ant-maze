# maze_editor

Browser-based maze editor built with React, Vite, and Pyodide.

## Features

- Edit occupancy, edge-grid, and radial-arm mazes
- 2D and 3D level editing
- Connector editing for 3D (`elevator`, `escalator`)
- YAML import/export
- PNG export
- Real-time visual and YAML sync

## Demo Gallery

| Demo | Preview |
| --- | --- |
| Maze families and templates | ![Maze families and templates](media/maze_types.gif) |
| 2D and 3D editing | ![2D and 3D editing](media/2d_3d_mazes.gif) |
| Add start/end points | ![Add start/end points](media/exp_add_start_end.gif) |
| Occupancy cell size controls | ![Occupancy cell size controls](media/occupancy_cell_size.gif) |
| Paint occupancy cells | ![Paint occupancy cells](media/paint_cells.gif) |
| Edge-grid editing | ![Edge-grid editing](media/edge_grid.gif) |
| Add elements and connectors | ![Add elements and connectors](media/add_elements.gif) |
| Radial-arm editing | ![Radial-arm editing](media/radial_arm.gif) |
| Radial-arm polygon editing | ![Radial-arm polygon editing](media/radial_arm_polygon.gif) |
| Save YAML config | ![Save YAML config](media/save_config.gif) |
| Save PNG image | ![Save PNG image](media/save_image.gif) |

## Prerequisites

- Node.js 18+
- Python 3.10+ (to build the `py_ant_maze` wheel used by Pyodide)

## Use the Editor

### Option 1: Deployed

Open https://maze.yihao.one in your browser.

### Option 2: Local Development

1. Build the Python wheel:

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

The `predev` script copies `../py_ant_maze/dist/py_ant_maze-0.1.1-py3-none-any.whl` into `public/`.
Then open the Vite URL shown in the terminal (usually `http://localhost:5173`).

## Build

```bash
npm run build
```

Artifacts are emitted to `dist/`.

## Source Layout

- `src/components/`: UI components
- `src/hooks/`: editor state and file operation hooks
- `src/services/pyodide.ts`: Pyodide bridge to `py_ant_maze`
- `src/constants/`: default templates and static values
