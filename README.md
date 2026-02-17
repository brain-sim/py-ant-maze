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

Run the web editor:

```bash
cd py_ant_maze
python -m build

cd ../maze_editor
npm install
npm run dev
```

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
