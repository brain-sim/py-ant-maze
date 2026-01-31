import yaml

from .core.base import ConfigBase, LayoutBase
from .core.registry import get_types
from .core.types import MazeSpec, MazeType
from .io.serialization import dump_yaml


class Maze:
    def __init__(self, maze_type: MazeType, config: ConfigBase, layout: LayoutBase) -> None:
        self.maze_type = maze_type
        self.config = config
        self.layout = layout

    @classmethod
    def from_text(cls, text: str) -> "Maze":
        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            raise TypeError("maze YAML must be a dict")
        return cls._from_spec(data)

    @classmethod
    def from_file(cls, path: str) -> "Maze":
        with open(path, "r", encoding="utf-8") as handle:
            return cls.from_text(handle.read())

    def to_text(self, with_grid_numbers: bool = False) -> str:
        maze_spec = self.to_spec(with_grid_numbers=with_grid_numbers)
        return dump_yaml(maze_spec)

    def to_file(self, path: str, with_grid_numbers: bool = False) -> None:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(self.to_text(with_grid_numbers=with_grid_numbers))

    def to_spec(self, with_grid_numbers: bool = False) -> MazeSpec:
        config_spec = self.config.to_spec()
        layout_spec = self.layout.to_spec(self.config, with_grid_numbers)
        return {
            "maze_type": self.maze_type,
            "config": config_spec,
            "layout": layout_spec,
        }

    @classmethod
    def _from_spec(cls, maze_spec: MazeSpec) -> "Maze":
        maze_type = maze_spec.get("maze_type")
        if not maze_type:
            raise ValueError("maze_type is required")
        config_spec = maze_spec.get("config", {})
        layout_spec = maze_spec.get("layout")
        if layout_spec is None:
            raise ValueError("layout is required")

        config_cls, layout_cls = get_types(maze_type)
        config = config_cls.from_spec(config_spec)
        layout = layout_cls.from_spec(layout_spec, config)
        return cls(maze_type, config, layout)
