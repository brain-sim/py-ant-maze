"""Color resolution using the same rules as the web maze renderer."""

from __future__ import annotations

import colorsys

from .models import Layer, RGB, RenderPalette


class WebColorResolver:
    def __init__(self, palette: RenderPalette | None = None) -> None:
        self.palette = palette or RenderPalette()

    def resolve(self, name: str, layer: Layer = "cell") -> RGB:
        layer_map = self.palette.wall if layer in {"wall", "corner"} else self.palette.cell
        if name in layer_map:
            return layer_map[name]
        if name in self.palette.legacy:
            return self.palette.legacy[name]

        hash_value = _js_hash(name)
        hue = (abs(hash_value) * 137.508) % 360.0
        saturation = 60.0 if layer == "wall" else 70.0
        lightness = 45.0 if layer == "wall" else 50.0
        return _hsl_to_rgb(hue, saturation, lightness)


def _js_hash(value: str) -> int:
    hash_value = 0
    for character in value:
        hash_value = (ord(character) + ((hash_value << 5) - hash_value)) & 0xFFFFFFFF
    if hash_value >= 0x80000000:
        hash_value -= 0x100000000
    return hash_value


def _hsl_to_rgb(hue: float, saturation: float, lightness: float) -> RGB:
    h = hue / 360.0
    l = lightness / 100.0
    s = saturation / 100.0
    red, green, blue = colorsys.hls_to_rgb(h, l, s)
    return (
        int(round(red * 255.0)),
        int(round(green * 255.0)),
        int(round(blue * 255.0)),
    )
