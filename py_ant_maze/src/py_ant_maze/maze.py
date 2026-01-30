from typing import Any, Dict

import yaml

from .yaml_types import LiteralStr, QuotedStr
from .registry import get_types


class _MazeDumper(yaml.SafeDumper):
    """YAML dumper that renders layout strings using literal blocks."""


def _literal_block_representer(dumper: yaml.Dumper, data: LiteralStr) -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data), style="|")


def _quoted_str_representer(dumper: yaml.Dumper, data: QuotedStr) -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data), style="'")


_MazeDumper.add_representer(LiteralStr, _literal_block_representer)
_MazeDumper.add_representer(QuotedStr, _quoted_str_representer)

class Maze:
    def __init__(self, maze_type: str, config: object, layout: object) -> None:
        self.maze_type = maze_type
        self.config = config
        self.layout = layout

    @classmethod
    def from_text(cls, text: str) -> "Maze":
        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            raise TypeError("maze YAML must be a mapping")
        return cls._from_mapping(data)

    @classmethod
    def from_file(cls, path: str) -> "Maze":
        with open(path, "r", encoding="utf-8") as handle:
            return cls.from_text(handle.read())

    def to_text(self, with_grid_numbers: bool = False) -> str:
        mapping = self.to_mapping(with_grid_numbers=with_grid_numbers)
        return yaml.dump(mapping, Dumper=_MazeDumper, sort_keys=False, default_flow_style=False)

    def to_file(self, path: str, with_grid_numbers: bool = False) -> None:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(self.to_text(with_grid_numbers=with_grid_numbers))

    def to_mapping(self, with_grid_numbers: bool = False) -> Dict[str, Any]:
        config_mapping = self.config.to_mapping()
        layout_mapping = self.layout.to_mapping(self.config, with_grid_numbers)
        return {
            "maze_type": self.maze_type,
            "config": config_mapping,
            "layout": layout_mapping,
        }

    @classmethod
    def _from_mapping(cls, maze_spec: Dict[str, Any]) -> "Maze":
        maze_type = maze_spec.get("maze_type")
        if not maze_type:
            raise ValueError("maze_type is required")
        config_mapping = maze_spec.get("config", {})
        layout_mapping = maze_spec.get("layout")
        if layout_mapping is None:
            raise ValueError("layout is required")

        config_cls, layout_cls = get_types(maze_type)
        config = config_cls.from_mapping(config_mapping)
        layout = layout_cls.from_mapping(layout_mapping, config)
        return cls(maze_type, config, layout)
