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

## Maze Types

| Type | Description | Variants |
|------|-------------|----------|
| **Occupancy Grid** | Classic blocked/open cell representation | 2D, 3D |
| **Edge Grid** | Thin walls between cells | 2D, 3D |
| **Radial Arm** | Center hub with configurable arms | 2D, 3D |

All types support both 2D (single layer) and 3D (multi-level with connectors).

## Web Editor Features

- **Visual Editing**: Click and drag to paint cells and walls
- **3D Multi-Level**: Add/remove levels, switch between floors
- **Radial Arm Controls**: Adjust hub shape/size, arm count, and per-arm dimensions
- **Connectors**: Place elevators and escalators between levels
- **Import/Export**: Load and save YAML files, export as PNG images
- **Real-time Sync**: Bidirectional YAML ↔ Grid synchronization

The editor runs entirely in the browser using [Pyodide](https://pyodide.org/) to interface with the Python library.

## License

MIT
