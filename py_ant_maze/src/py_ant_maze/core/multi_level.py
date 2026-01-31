from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Sequence, Tuple, Union

from .types import LayoutSpec, LayoutInput


LevelIdentifier = Union[str, int]


@dataclass(frozen=True)
class LevelDefinition:
    name: str
    index: int


@dataclass(frozen=True)
class LevelLayoutSpec:
    definition: LevelDefinition
    layout_spec: LayoutInput


def parse_level_layouts(levels_spec: Any, *, context: str) -> List[LevelLayoutSpec]:
    if not isinstance(levels_spec, list):
        raise TypeError(f"{context} must be a list")
    if len(levels_spec) < 2:
        raise ValueError(f"{context} must include at least two levels")

    seen_names = set()
    parsed: List[LevelLayoutSpec] = []
    for index, entry in enumerate(levels_spec):
        if not isinstance(entry, dict):
            raise TypeError(f"{context}[{index}] must be a mapping")
        level_id = entry.get("id")
        level_name = str(level_id) if level_id is not None else f"level_{index}"
        if level_name in seen_names:
            raise ValueError(f"{context}[{index}] has a duplicate id: {level_name}")

        if "layout" in entry:
            layout_spec = entry["layout"]
        else:
            layout_spec = {key: value for key, value in entry.items() if key != "id"}

        if layout_spec is None:
            raise ValueError(f"{context}[{index}].layout is required")
        if isinstance(layout_spec, dict) and not layout_spec:
            raise ValueError(f"{context}[{index}].layout cannot be empty")

        parsed.append(
            LevelLayoutSpec(
                definition=LevelDefinition(name=level_name, index=index),
                layout_spec=layout_spec,
            )
        )
        seen_names.add(level_name)
    return parsed


def resolve_level(
    levels: Sequence[LevelDefinition],
    identifier: LevelIdentifier,
    *,
    context: str,
) -> LevelDefinition:
    if isinstance(identifier, int):
        if identifier < 0 or identifier >= len(levels):
            raise ValueError(f"{context}.level index out of range")
        return levels[identifier]
    if isinstance(identifier, str):
        for level in levels:
            if level.name == identifier:
                return level
        raise ValueError(f"{context}.level unknown identifier: {identifier}")
    raise TypeError(f"{context}.level must be a string or integer")


def connectors_mapping(spec: LayoutSpec, *, context: str) -> Dict[str, Any]:
    connectors = spec.get("connectors", {})
    if connectors is None:
        connectors = {}
    if not isinstance(connectors, dict):
        raise TypeError(f"{context}.connectors must be a mapping")
    return connectors
