# py-ant-maze

Monorepo for maze authoring, serialization, and USD generation.

## Packages

| Package | Purpose |
| --- | --- |
| [`py_ant_maze`](py_ant_maze) | Maze model + YAML parsing/validation/editing APIs + 2D image-to-YAML inversion + 2D config-to-image rendering |
| [`maze_generator`](maze_generator) | Convert maze YAML to USD with materials/textures |
| [`maze_editor`](maze_editor) | Browser editor (React + Pyodide) for interactive maze editing |

## Quick Setup

Install the Python packages in editable mode:

```bash
pip install -e py_ant_maze
pip install -e maze_generator
```

Run the USD generator CLI:

```bash
maze-generator path/to/maze.yaml -o path/to/output.usda
maze-generator path/to/maze.yaml --format obj -o path/to/output_bundle
maze-generator path/to/maze-layout.png --from-image -o path/to/inferred.yaml

# render image directly from YAML/config (2D occupancy/edge)
python -c "from py_ant_maze import config_file_to_image; config_file_to_image('path/to/maze.yaml', 'path/to/maze-layout.png')"
```

Use the web editor:

- Deployed app: open https://maze.yihao.one
- Local development:

```bash
cd py_ant_maze
python -m build

cd ../maze_editor
npm install
npm run dev
```

Then open the Vite URL shown in the terminal (usually `http://localhost:5173`).

## Maze Editor Demos

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

## Maze Families

| Family | 2D | 3D |
| --- | --- | --- |
| Occupancy Grid | `occupancy_grid` | `occupancy_grid_3d` |
| Edge Grid | `edge_grid` | `edge_grid_3d` |
| Radial Arm | `radial_arm` | `radial_arm_3d` |

## Notes

- `maze_generator` uses strict failure behavior (no silent fallback for invalid inputs or missing required dependencies).
- USD export always writes merged visual walls plus separate box-compound colliders (`/Maze/Colliders`).
- OBJ export writes a bundle directory containing `visual.obj`, `collider.obj`, and copied `textures/`.
- `py_ant_maze.convert_config2img` intentionally mirrors maze editor rendering logic in Python. It is a copied implementation; `maze_editor` code remains separate.

## License

MIT
