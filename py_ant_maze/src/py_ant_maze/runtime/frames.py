from __future__ import annotations

FRAME_CONFIG = "config"
FRAME_SIMULATION_GENESIS = "simulation_genesis"
FRAME_SIMULATION_ISAAC = "simulation_isaac"
FRAME_CHOICES = (
    FRAME_CONFIG,
    FRAME_SIMULATION_GENESIS,
    FRAME_SIMULATION_ISAAC,
)


def normalize_frame(value: str) -> str:
    frame = str(value).strip().lower()
    if frame not in FRAME_CHOICES:
        raise ValueError(f"Unsupported frame={value!r}; expected one of {FRAME_CHOICES}")
    return frame


def frame_flips_y(frame: str) -> bool:
    normalized = normalize_frame(frame)
    return normalized == FRAME_SIMULATION_GENESIS


def frame_flips_x(frame: str) -> bool:
    normalized = normalize_frame(frame)
    return normalized == FRAME_SIMULATION_ISAAC


class MazeFrameTransformer:
    def __init__(self, frame: str):
        self.frame = normalize_frame(frame)

    def cell_center(
        self,
        row: int,
        col: int,
        rows: int,
        cell_size: float,
        cols: int | None = None,
    ) -> tuple[float, float]:
        x = (col + 0.5) * cell_size
        y = (row + 0.5) * cell_size
        if frame_flips_x(self.frame):
            if cols is None:
                raise ValueError("cols is required for simulation_isaac frame transforms.")
            x = float(cols) * cell_size - x
        if frame_flips_y(self.frame):
            y = float(rows) * cell_size - y
        return x, y
