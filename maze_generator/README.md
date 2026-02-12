# maze_generator

Generate USD mazes from `py_ant_maze` YAML files.

## Install

```bash
pip install -e .
```

Required runtime dependencies:
- `py-ant-maze`
- `usd-core>=24.0`
- `trimesh>=4.0.0`
- `manifold3d>=2.5.0`

## CLI

```bash
maze-generator input.yaml -o output.usda
maze-generator input.yaml --merge
python -m maze_generator input.yaml -o output.usda
```

- `-o, --output`: output USD path (default: `<input>.usda`)
- `--merge`: boolean-union wall boxes and emit one mesh at `/Maze/Walls/merged_walls`

Default behavior:
- auto-discovers textures from `maze_generator/default_assets/textures` and USD materials from `maze_generator/default_assets/materials` (`allow_empty=True`)
- raises explicit exceptions on invalid input or missing required dependencies

## Python API

```python
from maze_generator import (
    MaterialSource,
    UsdMaterialRef,
    discover_all_default_materials,
    discover_default_materials,
    maze_to_usd,
)

# Procedural materials only
maze_to_usd("maze.yaml", "maze.usda")

# Boolean union merge into one mesh
maze_to_usd("maze.yaml", "maze_merged.usda", merge=True)

# Texture mapping by element name
source = MaterialSource(textures={"wall_1": "/abs/path/wall_1.jpg"})
maze_to_usd("maze.yaml", "maze_textured.usda", material_source=source)

# External USD material mapping by element name
source = MaterialSource(
    usd_materials={
        "wall_2": UsdMaterialRef(
            file="/abs/path/materials.usda",
            path="/Materials/Concrete",
        )
    }
)
maze_to_usd("maze.yaml", "maze_external.usda", material_source=source)

# Discover packaged textures
source = discover_default_materials()
source = discover_all_default_materials()

# Discover with custom USD file patterns
source = discover_default_materials(usd_patterns=["*.usda"])
```

## Material Resolution Order

For each element name:
1. `MaterialSource.usd_materials[element_name]`
2. `MaterialSource.textures[element_name]`
3. procedural preview material (`material_map` override or generated color)

When `merge=True`, one mesh is emitted with per-element `UsdGeom.Subset` face groups for material binding.

## USD Material Discovery

- Discovery scans files recursively under `default_assets/materials` with patterns `*.usd`, `*.usda`, `*.usdc`, `*.usdz`.
- Single-material USD file:
  - if nested under `default_assets/materials/<element>/...`, maps to `<element>`
  - otherwise maps by file stem
  - Example: `default_assets/materials/wall_1/wall_1.usd` maps to element `wall_1`.
- Multi-material USD file: each `UsdShade.Material` prim maps by prim name.
  - Example: `/Materials/wall_2` maps to element `wall_2`.
- If both texture and USD material are discovered for the same element, the USD material is used.
- USD files without any `UsdShade.Material` prims raise `ValueError`.

## Failure Behavior

The package is fail-fast by design:
- missing maze file -> `FileNotFoundError`
- invalid maze spec/layout -> `ValueError` / `TypeError`
- missing texture/USD material path -> `FileNotFoundError`
- invalid discovered USD material file (no material prims) -> `ValueError`
- missing `manifold3d` for merge -> `ImportError`
- failed boolean union result -> `RuntimeError`

## Package Layout

- `maze_generator/__init__.py`: public API
- `maze_generator/__main__.py`: CLI entrypoint
- `maze_generator/maze_geometry/`: extraction and wall box models
- `maze_generator/maze_materials/`: material models, discovery, shader node helpers
- `maze_generator/maze_boolean/`: boolean union integration
- `maze_generator/maze_usd/`: USD stage/material/wall writing pipeline

Top-level compatibility wrapper modules are intentionally removed.
