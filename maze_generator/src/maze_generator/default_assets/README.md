# default_assets

Packaged assets consumed by `maze_generator.maze_materials.discovery`.

## Layout

- `textures/`: image files discovered as wall textures

## Naming Rule

Texture filename stem maps directly to maze element name.

Examples:
- `wall_1.jpg` -> `wall_1`
- `door.png` -> `door`

## Discovery Behavior

- `discover_default_materials()` defaults to `*.jpg`
- `discover_all_default_materials()` searches `*.jpg`, `*.jpeg`, `*.png`, `*.exr`, `*.tif`, `*.tiff`
- Missing `default_assets` or `textures` directory raises `FileNotFoundError`
- Empty match set raises `FileNotFoundError` unless `allow_empty=True`
