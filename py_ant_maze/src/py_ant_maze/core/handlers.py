from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Tuple

from .types import ConfigSpec, LayoutSpec, MazeSpec


class MazeTypeHandler(ABC):
    maze_type: str
    aliases: Tuple[str, ...] = ()

    @abstractmethod
    def parse_config(self, spec: ConfigSpec) -> Any:
        raise NotImplementedError

    @abstractmethod
    def parse_layout(self, spec: LayoutSpec, config: Any) -> Any:
        raise NotImplementedError

    def validate(self, config: Any, layout: Any) -> None:
        return None

    def freeze(self, config: Any, layout: Any) -> Tuple[Any, Any]:
        return config, layout

    def thaw(self, config: Any, layout: Any) -> Tuple[Any, Any]:
        return config, layout

    @abstractmethod
    def config_to_spec(self, config: Any) -> ConfigSpec:
        raise NotImplementedError

    @abstractmethod
    def layout_to_spec(self, layout: Any, config: Any, with_grid_numbers: bool) -> LayoutSpec:
        raise NotImplementedError

    def to_spec(self, config: Any, layout: Any, with_grid_numbers: bool) -> MazeSpec:
        return {
            "maze_type": self.maze_type,
            "config": self.config_to_spec(config),
            "layout": self.layout_to_spec(layout, config, with_grid_numbers),
        }
