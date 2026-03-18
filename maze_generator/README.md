# maze_generator

Geometry export package for `py_ant_maze` mazes.

Converts maze layouts into:

- USD scene with merged visual meshes + compound colliders.
- OBJ bundle with visual/collider meshes + copied textures.

## Current Scope

Supported input maze types:

- `occupancy_grid`
- `edge_grid`

`radial_arm` and `*_3d` parsing exists in `py_ant_maze`, but geometry export in this package is currently implemented for the two 2D grid families above.

## Install

```bash
cd maze_generator
pip install -e .
```

Runtime dependencies:

- `py-ant-maze`
- `usd-core>=24.0`
- `trimesh>=4.0.0`
- `manifold3d>=2.5.0`

## Export Pipeline (Code Path)

1. Parse/load maze (`py_ant_maze.Maze` or YAML path).
2. Extract wall boxes (`maze_geometry/extractor.py`).
3. Apply export frame (`ExportOptions.target_frame`).
4. Resolve materials (`maze_materials/source.py`, `discovery.py`, `color.py`).
5. Write output:
   - USD: `maze_usd/writer.py` + `wall_writers.py`
   - OBJ: `maze_obj/writer.py`

## Package Structure

```text
src/maze_generator/
├── __main__.py                  # CLI
├── __init__.py                  # Public Python API
├── export_options.py            # Frame conversion options
├── maze_geometry/               # Maze -> wall boxes
├── maze_boolean/                # Boolean union + convex segmentation
├── maze_materials/              # Material source/discovery/color logic
├── maze_usd/                    # USD stage, material library, wall writers
├── maze_obj/                    # OBJ/MTL bundle writer
└── default_assets/              # Packaged textures + USD materials
```

## CLI

```bash
maze-generator input.yaml -o output.usda
maze-generator input.yaml --format obj -o output_bundle
maze-generator input.yaml --frame config -o output_config_frame.usda
python -m maze_generator input.yaml --format obj
```

Arguments:

- `-o, --output`:
  - USD: file path
  - OBJ: output directory
- `--format {usd,obj}`:
  - inferred from output suffix when omitted
  - `.obj` or `_obj`/`_obj_bundle` name hint => OBJ
  - `.usd/.usda/.usdc/.usdz` => USD
  - fallback default => USD
- `--frame {simulation_genesis,simulation_isaac,config}`:
  - `simulation_genesis` (default): Y-flipped map orientation
  - `simulation_isaac`: X-flipped map orientation
  - `config`: authored indexing/orientation

Default output path when `--output` is omitted:

- USD: `<input>.usda`
- OBJ: `<input>_obj`

## Python API

```python
from maze_generator import (
    ExportOptions,
    MaterialSource,
    UsdMaterialRef,
    maze_to_obj,
    maze_to_usd,
    discover_default_materials,
)

# USD output
maze_to_usd("maze.yaml", "maze.usda")

# OBJ bundle output
maze_to_obj("maze.yaml", "maze_obj_bundle")

# Keep config frame (no Y flip)
maze_to_usd(
    "maze.yaml",
    "maze_config_frame.usda",
    export_options=ExportOptions(target_frame="config"),
)

# Per-element texture override
source = MaterialSource(textures={"wall_1": "/abs/path/wall_1.jpg"})
maze_to_obj("maze.yaml", "maze_obj_bundle_textured", material_source=source)

# External USD material reference
source = MaterialSource(
    usd_materials={
        "wall_2": UsdMaterialRef(
            file="/abs/path/materials.usda",
            path="/Materials/Concrete",
        )
    }
)
maze_to_usd("maze.yaml", "maze_external.usda", material_source=source)

# Use packaged assets
source = discover_default_materials()
```

## Output Layout

### USD

- `/Maze/Walls/merged_walls`: merged visual mesh.
- Material subsets under merged mesh per `element_name`.
- `/Maze/Colliders/collider_*`: non-overlapping compound collider boxes (`UsdPhysics.CollisionAPI`).
- `/Maze/Materials/*`: generated/referenced material prims.

### OBJ bundle

- `visual.obj` + `visual.mtl`
- `collider.obj` + `collider.mtl`
- `textures/` with copied texture files referenced by `visual.mtl`

## Material Resolution Priority

For each wall element name:

- Extended identifier rule:
  - side overrides are optional
  - base lookup: `<element>_stretch` is checked before `<element>`
  - side-face lookup: `<element>_<face>_stretch`, `<element>_stretch_<face>`, `<element>_<face>`, `<element>_stretch`, `<element>`
  - examples:
    - maze element `wall_1` will prefer assets named `wall_1_stretch.*` over `wall_1.*`
    - left faces for maze element `wall_1` will prefer `wall_1_left_stretch.*`, then `wall_1_stretch_left.*`, then `wall_1_left.*`, then base assets
- USD export:
  1. `MaterialSource.usd_materials[element]`
  2. `MaterialSource.textures[element]`
  3. procedural preview material (from `material_map` or generated palette)
- OBJ export:
  1. `MaterialSource.textures[element]` -> `map_Kd`
  2. fallback color `Kd` from `material_map`/generated palette

## Default Assets

Packaged defaults live under `src/maze_generator/default_assets/`.  
See [`default_assets/README.md`](src/maze_generator/default_assets/README.md) for naming and discovery rules.
