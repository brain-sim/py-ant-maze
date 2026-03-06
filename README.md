# py-ant-maze

Monorepo for maze definition, editing, image conversion, and geometry export.

## Packages

| Package | Purpose |
| --- | --- |
| [`py_ant_maze`](py_ant_maze) | Core Python model/parsing/editing runtime for maze YAML (2D + 3D types) |
| [`maze_generator`](maze_generator) | Geometry export pipeline (YAML -> USD/OBJ) with material |
| [`maze_editor`](maze_editor) | Browser editor (React + Pyodide) for interactive authoring and visualization |

## Repository Structure

```text
py-ant-maze/
├── README.md
├── LICENSE
├── examples/                    # Sample YAML/PNG/USD/OBJ outputs
├── py_ant_maze/                 # Core Python package
│   ├── src/py_ant_maze/
│   └── examples/
├── maze_generator/              # USD/OBJ export package
│   └── src/maze_generator/
└── maze_editor/                 # React + Pyodide web editor
    ├── src/
    ├── public/
    └── media/                   # Demo GIFs
```

## Features

| Capability | `py_ant_maze` | `maze_generator` | `maze_editor` |
| --- | --- | --- | --- |
| Parse + validate maze YAML | Yes | Via `py_ant_maze` | Yes (via Pyodide) |
| Mutable editing API | Yes (`MazeDraft`) | No | Yes (visual + YAML) |
| 2D maze families (`occupancy_grid`, `edge_grid`, `radial_arm`) | Yes | `occupancy_grid`, `edge_grid` | Yes |
| 3D maze families (`*_3d`) | Yes | Not exported yet | Yes |
| YAML -> image | Yes (2D occupancy/edge) | No | Yes (PNG export) |
| USD/OBJ export | No | Yes | No |

## Quick Start

### 1) Install Python packages

```bash
pip install -e py_ant_maze
pip install -e maze_generator
```

### 2) Work with mazes in Python

```python
from py_ant_maze import Maze

maze = Maze.from_file("path/to/maze.yaml")
print(maze.to_text(with_grid_numbers=True))
```

### 3) Convert between YAML and images (2D occupancy/edge only)

```python
from py_ant_maze import image_to_yaml_file, config_file_to_image
config_file_to_image("maze.yaml", "maze-layout.png")
```

### 4) Export geometry

```bash
# USD
maze-generator path/to/maze.yaml -o path/to/output.usda

# OBJ bundle (visual.obj, collider.obj, textures/)
maze-generator path/to/maze.yaml --format obj -o path/to/output_obj_bundle
```

### 5) Use the editor

- Deployed app: https://maze.yihao.one
- Local dev:

```bash
cd py_ant_maze
python -m build

cd ../maze_editor
npm install
npm run dev
```

Then open the Vite URL shown in the terminal (usually `http://localhost:5173`).

## Maze Families

| Family | 2D | 3D |
| --- | --- | --- |
| Occupancy Grid | `occupancy_grid` | `occupancy_grid_3d` |
| Edge Grid | `edge_grid` | `edge_grid_3d` |
| Radial Arm | `radial_arm` | `radial_arm_3d` |

## Maze Editor Demos

| Demo | Preview |
| --- | --- |
| Maze types | ![Maze types](media/maze_types.gif) |
| 2D and 3D mazes | ![2D and 3D mazes](media/2d_3d_mazes.gif) |
| Occupancy grid size | ![Occupancy grid size](media/occupancy_cell_size.gif) |
| Paint occupancy cells | ![Paint occupancy cells](media/paint_cells.gif) |
| Add elements | ![Add elements](media/add_elements.gif) |
| Add start/end | ![Add start/end](media/exp_add_start_end.gif) |
| Save YAML config | ![Save YAML config](media/save_config.gif) |
| Save PNG image | ![Save PNG image](media/save_image.gif) |
| Edge-grid type | ![Edge-grid type](media/edge_grid.gif) |
| Radial-arm type | ![Radial-arm type](media/radial_arm.gif) |
| Radial-arm polygon type | ![Radial-arm polygon type](media/radial_arm_polygon.gif) |


## Notes

- USD export writes merged visual walls at `/Maze/Walls/merged_walls` plus separate compound box colliders at `/Maze/Colliders/*`.
- OBJ export writes `visual.obj`, `collider.obj`, and copied textures into a bundle directory.

## License

MIT
