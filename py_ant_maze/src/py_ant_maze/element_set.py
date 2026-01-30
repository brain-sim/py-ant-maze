from typing import Dict, List, Optional, Set, Iterable, Type

from .elements import MazeElement
from .yaml_types import QuotedStr


class ElementSet:
    def __init__(self, elements: Iterable[MazeElement]) -> None:
        self._elements: List[MazeElement] = []
        self._by_name: Dict[str, MazeElement] = {}
        self._by_token: Dict[str, MazeElement] = {}
        self._by_value: Dict[int, MazeElement] = {}
        for element in elements:
            self.add(element)

    def add(self, element: MazeElement) -> None:
        if element.name in self._by_name:
            raise ValueError(f"duplicate element name: {element.name}")
        if element.token in self._by_token:
            raise ValueError(f"duplicate element token: {element.token}")
        if element.value in self._by_value:
            raise ValueError(f"duplicate element value: {element.value}")

        self._elements.append(element)
        self._by_name[element.name] = element
        self._by_token[element.token] = element
        self._by_value[element.value] = element

    def element(self, name: str) -> MazeElement:
        try:
            return self._by_name[name]
        except KeyError as exc:
            raise KeyError(f"unknown element name: {name}") from exc

    def element_for_token(self, token: str) -> MazeElement:
        try:
            return self._by_token[token]
        except KeyError as exc:
            raise KeyError(f"unknown element token: {token}") from exc

    def element_for_value(self, value: int) -> MazeElement:
        try:
            return self._by_value[value]
        except KeyError as exc:
            raise KeyError(f"unknown element value: {value}") from exc

    def elements(self) -> List[MazeElement]:
        return list(self._elements)

    def to_list(self) -> List[Dict[str, object]]:
        return [
            {"name": el.name, "token": QuotedStr(el.token), "value": el.value} for el in self._elements
        ]

    @classmethod
    def from_list(
        cls,
        items: List[Dict[str, object]],
        element_cls: Type[MazeElement],
        reserved_defaults: Optional[Dict[str, int]] = None,
    ) -> "ElementSet":
        if not isinstance(items, list):
            raise TypeError("elements must be a list")
        if not items:
            raise ValueError("elements list cannot be empty")

        reserved_defaults = reserved_defaults or {}
        parsed: List[MazeElement] = []
        used_values: Set[int] = set()
        explicit_values: Set[int] = set()
        reserved_values: Dict[str, int] = {}

        for item in items:
            if not isinstance(item, dict):
                raise TypeError("each element must be a mapping")
            name = item.get("name")
            value = item.get("value")
            if not name:
                raise ValueError("each element must include name")
            if value is None:
                lower = str(name).lower()
                if lower in reserved_defaults:
                    reserved_values[lower] = reserved_defaults[lower]
            else:
                if not isinstance(value, int):
                    raise TypeError("element value must be an integer")
                if value in explicit_values:
                    raise ValueError(f"duplicate element value: {value}")
                explicit_values.add(value)

        for item in items:
            name = item.get("name")
            token = item.get("token")
            value = item.get("value")
            if not name or token is None:
                raise ValueError("each element must include name and token")

            lower = str(name).lower()
            if value is None:
                if lower in reserved_values:
                    value = reserved_values[lower]
                    if value in explicit_values:
                        raise ValueError(f"reserved value already used: {value}")
                else:
                    blocked = used_values.union(explicit_values).union(reserved_values.values())
                    value = _next_available_value(blocked)

            if value in used_values:
                raise ValueError(f"duplicate element value: {value}")

            element = element_cls(name=name, token=token, value=value)
            used_values.add(value)
            parsed.append(element)

        return cls(parsed)


def _next_available_value(used: Set[int]) -> int:
    candidate = 0
    while candidate in used:
        candidate += 1
    return candidate
