from __future__ import annotations

from collections.abc import Iterable

from .model import MazeSemantics


class MazeSemanticsBuilder:
    def build(self, config: object) -> MazeSemantics:
        return MazeSemantics(
            cell_values_by_name=self._index_by_name(config.cell_elements.elements()),
            wall_values_by_name=self._index_by_name(config.wall_elements.elements()),
            cell_values_by_token=self._index_by_token(config.cell_elements.elements()),
            wall_values_by_token=self._index_by_token(config.wall_elements.elements()),
        )

    @staticmethod
    def _index_by_name(elements: Iterable[object]) -> dict[str, frozenset[int]]:
        values_by_name: dict[str, set[int]] = {}
        for element in elements:
            name = str(element.name).strip().lower()
            values_by_name.setdefault(name, set()).add(int(element.value))
        return {name: frozenset(values) for name, values in values_by_name.items()}

    @staticmethod
    def _index_by_token(elements: Iterable[object]) -> dict[str, frozenset[int]]:
        values_by_token: dict[str, set[int]] = {}
        for element in elements:
            value = int(element.value)
            token = str(element.token)
            values_by_token.setdefault(token, set()).add(value)
            values_by_token.setdefault(token.lower(), set()).add(value)
        return {token: frozenset(values) for token, values in values_by_token.items()}
