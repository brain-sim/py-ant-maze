from types import MappingProxyType
from typing import Callable, Dict, Iterable, List, Optional, Set, Tuple, Type, TypeAlias

from .elements import MazeElement
from ..types import ElementSpecList


ElementList: TypeAlias = List[MazeElement]
FrozenElementList: TypeAlias = Tuple[MazeElement, ...]
ElementNameMap: TypeAlias = Dict[str, MazeElement]
ElementTokenMap: TypeAlias = Dict[str, MazeElement]
ElementValueMap: TypeAlias = Dict[int, MazeElement]
ElementValueSet: TypeAlias = Set[int]
ElementDefaults: TypeAlias = Dict[str, int]
TokenWrapper: TypeAlias = Callable[[str], object]


class ElementSet:
    def __init__(self, elements: Iterable[MazeElement]) -> None:
        self._elements: ElementList = []
        self._by_name: ElementNameMap = {}
        self._by_token: ElementTokenMap = {}
        self._by_value: ElementValueMap = {}
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

    def elements(self) -> ElementList:
        return list(self._elements)

    def freeze(self) -> "FrozenElementSet":
        return FrozenElementSet(self._elements)

    def to_list(
        self,
        token_wrapper: Optional[TokenWrapper] = None,
    ) -> ElementSpecList:
        wrap = token_wrapper or (lambda token: token)
        return [
            {"name": el.name, "token": wrap(el.token), "value": el.value}
            for el in self._elements
        ]

    @classmethod
    def from_list(
        cls,
        items: ElementSpecList,
        element_cls: Type[MazeElement],
        reserved_defaults: Optional[ElementDefaults] = None,
    ) -> "ElementSet":
        if not isinstance(items, list):
            raise TypeError("elements must be a list")
        if not items:
            raise ValueError("elements list cannot be empty")

        reserved_defaults = reserved_defaults or {}
        parsed: ElementList = []
        used_values: ElementValueSet = set()
        explicit_values: ElementValueSet = set()
        reserved_values: ElementDefaults = {}

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


def _next_available_value(used: ElementValueSet) -> int:
    candidate = 0
    while candidate in used:
        candidate += 1
    return candidate


class FrozenElementSet:
    def __init__(self, elements: Iterable[MazeElement]) -> None:
        elements_tuple = tuple(elements)
        self._elements: FrozenElementList = elements_tuple
        self._by_name = MappingProxyType({el.name: el for el in elements_tuple})
        self._by_token = MappingProxyType({el.token: el for el in elements_tuple})
        self._by_value = MappingProxyType({el.value: el for el in elements_tuple})

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

    def elements(self) -> FrozenElementList:
        return self._elements

    def to_list(
        self,
        token_wrapper: Optional[TokenWrapper] = None,
    ) -> ElementSpecList:
        wrap = token_wrapper or (lambda token: token)
        return [
            {"name": el.name, "token": wrap(el.token), "value": el.value}
            for el in self._elements
        ]

    def thaw(self) -> ElementSet:
        return ElementSet(self._elements)
