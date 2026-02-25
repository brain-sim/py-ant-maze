from __future__ import annotations

FRAME_SIMULATION = "simulation"
FRAME_CONFIG = "config"
FRAME_CHOICES = (FRAME_SIMULATION, FRAME_CONFIG)


def normalize_frame(value: str) -> str:
    frame = str(value).strip().lower()
    if frame not in FRAME_CHOICES:
        raise ValueError(f"Unsupported frame={value!r}; expected one of {FRAME_CHOICES}")
    return frame


class MazeFrameTransformer:
    def __init__(self, frame: str):
        self.frame = normalize_frame(frame)

    def cell_center(self, row: int, col: int, rows: int, cell_size: float) -> tuple[float, float]:
        x = (col + 0.5) * cell_size
        y = (row + 0.5) * cell_size
        if self.frame == FRAME_SIMULATION:
            return x, float(rows) * cell_size - y
        return x, y
