# maze_editor

Browser-based maze editor built with React, Vite, and Pyodide.

## Features

- Edit occupancy, edge-grid, and radial-arm mazes
- 2D and 3D level editing
- Connector editing for 3D (`elevator`, `escalator`)
- YAML import/export
- PNG export
- Real-time visual and YAML sync

## Prerequisites

- Node.js 18+
- Python 3.10+ (to build the `py_ant_maze` wheel used by Pyodide)

## Run Locally

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
