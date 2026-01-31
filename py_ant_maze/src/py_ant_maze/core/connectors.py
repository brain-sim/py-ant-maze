from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

from .multi_level import LevelDefinition, resolve_level


@dataclass(frozen=True)
class ConnectorLocation:
    level: LevelDefinition
    row: int
    col: int
    arm: Optional[int] = None


@dataclass(frozen=True)
class Connector:
    kind: str
    start: ConnectorLocation
    end: ConnectorLocation


def parse_connectors(
    connectors_spec: Any,
    *,
    levels: Sequence[LevelDefinition],
    context: str,
    allow_arm: bool = False,
    require_arm: bool = False,
) -> List[Connector]:
    if connectors_spec is None:
        return []
    if not isinstance(connectors_spec, list):
        raise TypeError(f"{context} must be a list")

    connectors: List[Connector] = []
    for index, entry in enumerate(connectors_spec):
        entry_context = f"{context}[{index}]"
        if not isinstance(entry, dict):
            raise TypeError(f"{entry_context} must be a mapping")
        kind = entry.get("type") or entry.get("kind")
        if kind not in {"elevator", "escalator"}:
            raise ValueError(f"{entry_context}.type must be 'elevator' or 'escalator'")
        start_spec = entry.get("from")
        end_spec = entry.get("to")
        if start_spec is None:
            raise ValueError(f"{entry_context}.from is required")
        if end_spec is None:
            raise ValueError(f"{entry_context}.to is required")

        start = _parse_location(
            start_spec,
            levels=levels,
            context=f"{entry_context}.from",
            allow_arm=allow_arm,
            require_arm=require_arm,
        )
        end = _parse_location(
            end_spec,
            levels=levels,
            context=f"{entry_context}.to",
            allow_arm=allow_arm,
            require_arm=require_arm,
        )
        connectors.append(Connector(kind=kind, start=start, end=end))
    return connectors


def connectors_to_spec(connectors: Sequence[Connector]) -> List[Dict[str, Any]]:
    return [
        {
            "type": connector.kind,
            "from": location_to_spec(connector.start),
            "to": location_to_spec(connector.end),
        }
        for connector in connectors
    ]


def location_to_spec(location: ConnectorLocation) -> Dict[str, Any]:
    spec: Dict[str, Any] = {
        "level": location.level.name,
        "row": location.row,
        "col": location.col,
    }
    if location.arm is not None:
        spec["arm"] = location.arm
    return spec


def _parse_location(
    spec: Any,
    *,
    levels: Sequence[LevelDefinition],
    context: str,
    allow_arm: bool,
    require_arm: bool,
) -> ConnectorLocation:
    if not isinstance(spec, dict):
        raise TypeError(f"{context} must be a mapping")
    if "level" not in spec:
        raise ValueError(f"{context}.level is required")

    level = resolve_level(levels, spec.get("level"), context=context)
    row = _parse_non_negative_int(spec.get("row"), f"{context}.row")
    col = _parse_non_negative_int(spec.get("col"), f"{context}.col")

    arm_value = spec.get("arm")
    if arm_value is None:
        if require_arm:
            raise ValueError(f"{context}.arm is required")
        arm = None
    else:
        if not allow_arm:
            raise ValueError(f"{context}.arm is not allowed")
        arm = _parse_non_negative_int(arm_value, f"{context}.arm")

    return ConnectorLocation(level=level, row=row, col=col, arm=arm)


def _parse_non_negative_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field} must be an integer")
    if value < 0:
        raise ValueError(f"{field} must be >= 0")
    return value
