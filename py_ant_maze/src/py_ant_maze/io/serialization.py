from typing import Any

import yaml

from .yaml_types import LiteralStr, QuotedStr
from ..core.types import Spec


class _MazeDumper(yaml.SafeDumper):
    """YAML dumper that renders layout strings using literal blocks."""


def _literal_block_representer(dumper: yaml.Dumper, data: LiteralStr) -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data), style="|")


def _quoted_str_representer(dumper: yaml.Dumper, data: QuotedStr) -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data), style="'")


_MazeDumper.add_representer(LiteralStr, _literal_block_representer)
_MazeDumper.add_representer(QuotedStr, _quoted_str_representer)


def dump_yaml(mapping: Spec) -> str:
    _wrap_config_tokens(mapping)
    layout_mapping = mapping.get("layout")
    if isinstance(layout_mapping, dict):
        _wrap_multiline_strings(layout_mapping)
    return yaml.dump(mapping, Dumper=_MazeDumper, sort_keys=False, default_flow_style=False)


def _wrap_config_tokens(mapping: Spec) -> None:
    config = mapping.get("config")
    if not isinstance(config, dict):
        return
    for key in ("cell_elements", "wall_elements", "elements"):
        items = config.get(key)
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict) and "token" in item:
                item["token"] = QuotedStr(str(item["token"]))


def _wrap_multiline_strings(value: Any) -> Any:
    if isinstance(value, str) and "\n" in value:
        if not value.endswith("\n"):
            value += "\n"
        return LiteralStr(value)
    if isinstance(value, list):
        for i, item in enumerate(value):
            value[i] = _wrap_multiline_strings(item)
        return value
    if isinstance(value, dict):
        for key, item in value.items():
            value[key] = _wrap_multiline_strings(item)
        return value
    return value
