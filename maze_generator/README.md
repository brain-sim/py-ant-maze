# maze_generator

Generate USD/OBJ maze assets from `py_ant_maze` YAML files.

## Install

```bash
pip install -e .
```

Required runtime dependencies:
- `py-ant-maze`
- `usd-core>=24.0`
- `trimesh>=4.0.0`
- `manifold3d>=2.5.0`

## Export Behavior

USD output is fixed to:
- one merged visual mesh at `/Maze/Walls/merged_walls` with per-element material subsets
- one separate collider branch at `/Maze/Colliders/*` with box-compound colliders (`UsdPhysics.CollisionAPI`)

OBJ output is fixed to a bundle directory containing:
- `visual.obj` + `visual.mtl` (merged visual meshes/materials)
- `collider.obj` + `collider.mtl` (box-compound colliders)
- `textures/` (copied texture assets for visual materials)

## CLI

```bash
maze-generator input.yaml -o output.usda
maze-generator input.yaml --format obj -o output_bundle
maze-generator input.yaml --frame config -o output_config_frame.usda
python -m maze_generator input.yaml --format obj
```

- `-o, --output`: output path
  - USD: output USD file path
  - OBJ: output bundle directory path
- `--format {usd,obj}`: output format
  - if omitted, inferred from `--output` suffix (`.obj` => obj, `.usd/.usda/.usdc/.usdz` => usd)
  - extensionless names ending with `_obj` or `_obj_bundle` are treated as obj output
  - if still ambiguous, defaults to `usd`
- when output format resolves to usd and `--output` has no USD suffix, `.usda` is appended automatically
- `--frame {simulation,config}`: output coordinate frame
  - `simulation` (default): flips map Y from config-image indexing for sim-friendly orientation
  - `config`: preserves raw layout indexing as-authored in YAML

Default output paths:
- USD: `<input>.usda`
- OBJ: `<input>_obj` directory

## Python API

```python
from maze_generator import (
    ExportOptions,
    MaterialSource,
    UsdMaterialRef,
    discover_all_default_materials,
    discover_default_materials,
    maze_to_obj,
    maze_to_usd,
)

# USD output (merged visual + separate colliders)
maze_to_usd("maze.yaml", "maze.usda")

# OBJ bundle output (visual.obj + collider.obj + textures/)
maze_to_obj("maze.yaml", "maze_obj_bundle")

# Export in config frame (no X/Y flip)
maze_to_usd(
    "maze.yaml",
    "maze_config_frame.usda",
    export_options=ExportOptions(target_frame="config"),
)

# Texture mapping by element name
source = MaterialSource(textures={"wall_1": "/abs/path/wall_1.jpg"})
maze_to_obj("maze.yaml", "maze_obj_bundle_textured", material_source=source)
maze_to_usd("maze.yaml", "maze_textured.usda", material_source=source)

# External USD material mapping by element name (USD output)
source = MaterialSource(
    usd_materials={
        "wall_2": UsdMaterialRef(
            file="/abs/path/materials.usda",
            path="/Materials/Concrete",
        )
    }
)
maze_to_usd("maze.yaml", "maze_external.usda", material_source=source)

# Discover packaged textures and materials
source = discover_default_materials()
source = discover_all_default_materials()
```

## Material Resolution

For each wall element name:

If the same element name exists in both `usd_materials` and `textures`, both are allowed.

USD output:
1. `MaterialSource.usd_materials[element_name]`
2. `MaterialSource.textures[element_name]`
3. procedural preview material (`material_map` override or generated color)

OBJ visual output:
1. `MaterialSource.textures[element_name]` -> `map_Kd` in `visual.mtl`
2. fallback diffuse color (`Kd`) from `material_map`/generated color

## Failure Behavior

The package is fail-fast by design:
- missing maze file -> `FileNotFoundError`
- invalid maze spec/layout -> `ValueError` / `TypeError`
- missing texture/USD material path -> `FileNotFoundError`
- invalid discovered USD material file (no material prims) -> `ValueError`
- missing `manifold3d` for merged wall generation -> `ImportError`
- failed boolean union result -> `RuntimeError`

## Package Layout

- `maze_generator/__init__.py`: public API
- `maze_generator/__main__.py`: CLI entrypoint
- `maze_generator/maze_geometry/`: extraction and wall box models
- `maze_generator/maze_materials/`: material models and discovery
- `maze_generator/maze_boolean/`: boolean union integration
- `maze_generator/maze_usd/`: USD stage/material/wall writing pipeline
- `maze_generator/maze_obj/`: OBJ bundle writing pipeline
