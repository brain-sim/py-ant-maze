from __future__ import annotations

from typing import TypeAlias, Union

from ...core.parsing.level_connectors import LevelConnector, LevelConnectorLocation
from ...core.structures.element_set import ElementSet, FrozenElementSet


REQUIRED_CELL_ELEMENTS = ("elevator", "escalator")
ElementSetLike: TypeAlias = Union[ElementSet, FrozenElementSet]


def ensure_required_elements(element_set: ElementSetLike, *, context: str) -> None:
    missing = [
        name
        for name in REQUIRED_CELL_ELEMENTS
        if not _has_element(element_set, name)
    ]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"{context} must include elements: {joined}")


def element_value(element_set: ElementSetLike, name: str, *, context: str) -> int:
    for element in element_set.elements():
        if element.name.lower() == name.lower():
            return element.value
    raise ValueError(f"{context} must include element: {name}")


def validate_connector_rules(
    connector: LevelConnector,
    *,
    context: str,
) -> None:
    start = connector.start
    end = connector.end
    level_diff = abs(start.level.index - end.level.index)
    if level_diff != 1:
        raise ValueError(f"{context} must connect adjacent levels")
    if connector.kind == "elevator":
        _validate_same_coordinate(start, end, context=context)
    elif connector.kind == "escalator":
        _validate_different_coordinate(start, end, context=context)
    else:
        raise ValueError(f"{context} has unknown connector type: {connector.kind}")


def _validate_same_coordinate(
    start: LevelConnectorLocation,
    end: LevelConnectorLocation,
    *,
    context: str,
) -> None:
    if start.row != end.row or start.col != end.col:
        raise ValueError(f"{context} must use the same row and col for elevator")
    if start.arm != end.arm:
        raise ValueError(f"{context} must use the same arm for elevator")


def _validate_different_coordinate(
    start: LevelConnectorLocation,
    end: LevelConnectorLocation,
    *,
    context: str,
) -> None:
    if start.row == end.row and start.col == end.col and start.arm == end.arm:
        raise ValueError(f"{context} must use different coordinates for escalator")


def _has_element(element_set: ElementSetLike, name: str) -> bool:
    target = name.lower()
    return any(element.name.lower() == target for element in element_set.elements())
