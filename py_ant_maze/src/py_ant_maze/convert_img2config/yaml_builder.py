"""YAML rendering for reconstructed 2D mazes."""

from __future__ import annotations

from typing import Dict, List

import yaml

from .models import MazeReconstruction


class _LiteralString(str):
    pass


def _literal_string_presenter(dumper: yaml.SafeDumper, data: _LiteralString):
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data), style="|")


yaml.SafeDumper.add_representer(_LiteralString, _literal_string_presenter)


def to_yaml_text(reconstruction: MazeReconstruction) -> str:
    if reconstruction.maze_type == "occupancy_grid":
        return _occupancy_yaml(reconstruction)
    if reconstruction.maze_type == "edge_grid":
        return _edge_yaml(reconstruction)
    raise ValueError(f"Unsupported reconstructed maze type: {reconstruction.maze_type}")


def _occupancy_yaml(reconstruction: MazeReconstruction) -> str:
    if reconstruction.occupancy_grid is None:
        raise ValueError("occupancy_grid data is required")
    grid_block = _to_grid_block(reconstruction.occupancy_grid, {0: ".", 1: "#"})
    spec = {
        "maze_type": "occupancy_grid",
        "config": {
            "cell_elements": [{"name": "open", "token": ".", "value": 0}],
            "wall_elements": [{"name": "wall", "token": "#", "value": 1}],
        },
        "layout": {"grid": _LiteralString(grid_block)},
    }
    return yaml.safe_dump(spec, sort_keys=False)


def _edge_yaml(reconstruction: MazeReconstruction) -> str:
    if reconstruction.cells is None:
        raise ValueError("cells data is required")
    if reconstruction.vertical_walls is None:
        raise ValueError("vertical_walls data is required")
    if reconstruction.horizontal_walls is None:
        raise ValueError("horizontal_walls data is required")

    has_blocked_cells = any(value == 1 for row in reconstruction.cells for value in row)
    cell_elements = [{"name": "open", "token": ".", "value": 0}]
    if has_blocked_cells:
        cell_elements.append({"name": "blocked", "token": "x", "value": 1})

    cells_block = _to_grid_block(reconstruction.cells, {0: ".", 1: "x"})
    vertical_block = _to_grid_block(reconstruction.vertical_walls, {0: "-", 1: "#"})
    horizontal_block = _to_grid_block(reconstruction.horizontal_walls, {0: "-", 1: "#"})

    spec = {
        "maze_type": "edge_grid",
        "config": {
            "cell_elements": cell_elements,
            "wall_elements": [
                {"name": "empty", "token": "-", "value": 0},
                {"name": "wall", "token": "#", "value": 1},
            ],
        },
        "layout": {
            "cells": _LiteralString(cells_block),
            "walls": {
                "vertical": _LiteralString(vertical_block),
                "horizontal": _LiteralString(horizontal_block),
            },
        },
    }
    return yaml.safe_dump(spec, sort_keys=False)


def _to_grid_block(grid: List[List[int]], token_map: Dict[int, str]) -> str:
    rows: List[str] = []
    for row in grid:
        tokens: List[str] = []
        for value in row:
            if value not in token_map:
                raise ValueError(f"Unsupported grid value: {value}")
            tokens.append(token_map[value])
        rows.append(" ".join(tokens))
    return "\n".join(rows)
