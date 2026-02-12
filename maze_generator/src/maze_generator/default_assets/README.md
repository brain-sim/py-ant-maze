# default_assets

Packaged assets consumed by `maze_generator.maze_materials.discovery`.

## Layout

- `textures/`: image files discovered as wall textures
- `materials/`: USD files scanned recursively for `UsdShade.Material` prims

## Naming Rule

Texture filename stem maps directly to maze element name.

Examples:
- `wall_1.jpg` -> `wall_1`
- `door.png` -> `door`

Single-material USD file mapping:
- if file is under `materials/<element>/...`, it maps to `<element>`
- otherwise it maps by file stem

Multi-material USD file maps by material prim name.

Examples:
- `materials/wall_1/wall_1.usd` (single material) -> `wall_1`
- `/Materials/wall_2` (inside multi-material USD) -> `wall_2`

## Discovery Behavior

- `discover_default_materials()` defaults to `*.jpg`
- `discover_all_default_materials()` searches `*.jpg`, `*.jpeg`, `*.png`, `*.exr`, `*.tif`, `*.tiff`
- USD discovery patterns: `*.usd`, `*.usda`, `*.usdc`, `*.usdz`
- Missing `default_assets` or `textures` directory raises `FileNotFoundError`
- Missing `materials` directory raises `FileNotFoundError`
- USD files without `UsdShade.Material` prims raise `ValueError`
- Duplicate element names within discovered textures or discovered USD materials raise `ValueError`
- If both texture and USD material exist for one element, USD material is used
- Empty combined discovery result raises `FileNotFoundError` unless `allow_empty=True`
