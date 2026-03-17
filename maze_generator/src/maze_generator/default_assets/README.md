# default_assets

Packaged material library used by `maze_generator.maze_materials.discovery`.

## Directory Layout

```text
default_assets/
├── textures/                    # 2D textures (used for OBJ map_Kd or USD preview texture)
└── materials/                   # USD files containing UsdShade.Material prims
```

## Mapping Rules

### Textures

Texture filename stem maps directly to element name.

Examples:

- `textures/wall_1.jpg` -> element `wall_1`
- `textures/door.png` -> element `door`
- `textures/wall_1_stretch.jpg` -> preferred override for maze element `wall_1`

### USD materials

If a USD file contains exactly one `UsdShade.Material`:

- under `materials/<element>/...` -> map to `<element>`
- otherwise -> map by file stem

If a USD file contains multiple `UsdShade.Material` prims:

- each material maps by its prim name (`/Materials/Concrete` -> `Concrete`)

## Discovery APIs

- `discover_default_materials()`:
  - texture pattern default: `*.jpg`
  - USD patterns: `*.usd`, `*.usda`, `*.usdc`, `*.usdz`
- `discover_all_default_materials()`:
  - texture patterns: `*.jpg`, `*.jpeg`, `*.png`, `*.exr`, `*.tif`, `*.tiff`
  - USD patterns: same as above

## Resolution Priority in Export

If both texture and USD material exist for the same element:

- USD export prefers the discovered USD material.
- OBJ export uses textures only (USD material references are ignored for OBJ).

If both `<element>` and `<element>_stretch` assets exist:

- lookup for maze element `<element>` prefers `<element>_stretch`

## Adding New Assets

1. Add texture(s) in `textures/` named after target element(s).
2. Add USD material file(s) in `materials/` if needed.
3. Ensure element names are unique within each discovered set.
4. Verify discovery:

```python
from maze_generator import discover_all_default_materials

source = discover_all_default_materials()
print(source.textures.keys())
print(source.usd_materials.keys())
```
