# maze

Monorepo for maze-related Python packages and tools.

## Packages

- `packages/py_ant_maze`: **Core Library**. Python library for defining, loading, and manipulating maze structures using YAML configuration.
- `packages/maze_editor`: **Visual Editor**. A web-based tool for creating and editing mazes interactively.

## Maze Editor Features

The **Maze Editor** runs entirely in the browser using [Pyodide](https://pyodide.org/) to interface directly with the `py_ant_maze` library.

-   **Visual Grid**: Paint mazes interactively with drag-and-paint support.
-   **Dynamic Configuration**: Add custom elements (e.g., "Fire", "Coin") on the fly.
-   **Real-time Sync**: Bidirectional synchronization between the visual grid and YAML code.
-   **Export**: Download your creations as YAML files or PNG images.

## Quick Start

### Python Library
```bash
pip install -e packages/py_ant_maze
```

### Web Editor (Pyodide)
```bash
# 1. Build the python wheel first
cd packages/py_ant_maze
pip install build  # Install the build tool if missing
python -m build

# 2. Run the editor
cd ../maze_editor
npm install
npm run dev
```
