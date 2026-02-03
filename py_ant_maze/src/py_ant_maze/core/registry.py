from __future__ import annotations

from typing import Dict

from .handlers import MazeTypeHandler
from .types import MazeType


_REGISTRY: Dict[MazeType, MazeTypeHandler] = {}
_ALIASES: Dict[MazeType, MazeType] = {}


def register_handler(handler: MazeTypeHandler) -> None:
    if handler.maze_type in _REGISTRY:
        raise ValueError(f"maze_type already registered: {handler.maze_type}")
    _REGISTRY[handler.maze_type] = handler

    for alias in handler.aliases:
        if alias in _REGISTRY or alias in _ALIASES:
            raise ValueError(f"maze_type alias already registered: {alias}")
        _ALIASES[alias] = handler.maze_type


def get_handler(maze_type: MazeType) -> MazeTypeHandler:
    if not _REGISTRY:
        register_default_handlers()
    canonical = _ALIASES.get(maze_type, maze_type)
    try:
        return _REGISTRY[canonical]
    except KeyError as exc:
        raise KeyError(f"unknown maze_type: {maze_type}") from exc


def register_default_handlers() -> None:
    if _REGISTRY:
        return
    from ..mazes import HANDLERS

    for handler in HANDLERS:
        register_handler(handler)
