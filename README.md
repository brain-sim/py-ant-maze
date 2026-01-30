# py-ant-maze

Monorepo for maze definition and editing tools.

## Packages

| Package | Description |
|---------|-------------|
| [py_ant_maze](py_ant_maze) | Python library for defining and manipulating maze structures using YAML |
| [maze_editor](maze_editor) | Web-based visual editor for creating mazes |

## Quick Start

### Python Library

```bash
pip install -e py_ant_maze
```

### Web Editor

```bash
# Build the Python wheel
cd py_ant_maze
pip install build
python -m build

# Run the editor
cd ../maze_editor
npm install
npm run dev
```

## Overview

The **py_ant_maze** library supports two maze types:
- **Occupancy Grid**: Classic blocked/open cell representation
- **Edge Grid**: Thin walls between cells (vertical and horizontal walls)

The **Maze Editor** runs in the browser using [Pyodide](https://pyodide.org/) to interface directly with the Python library.

Features:
- Visual drag-and-paint editing
- Bidirectional YAML synchronization  
- Custom element creation
- Export to YAML and PNG
