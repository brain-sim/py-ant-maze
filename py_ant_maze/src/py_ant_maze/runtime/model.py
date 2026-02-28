from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

IntGrid = Sequence[Sequence[int]]


@dataclass(frozen=True)
class MazeCells:
    values: IntGrid
    rows: int
    cols: int


@dataclass(frozen=True)
class MazeSemantics:
    cell_values_by_name: dict[str, frozenset[int]]
    wall_values_by_name: dict[str, frozenset[int]]

    def values_for_cell_names(self, names: Iterable[str]) -> frozenset[int]:
        return self._values_for_names(self.cell_values_by_name, names)

    def values_for_wall_names(self, names: Iterable[str]) -> frozenset[int]:
        return self._values_for_names(self.wall_values_by_name, names)

    @staticmethod
    def _values_for_names(by_name: Mapping[str, frozenset[int]], names: Iterable[str]) -> frozenset[int]:
        values: set[int] = set()
        for name in names:
            values.update(by_name.get(str(name).strip().lower(), ()))
        return frozenset(values)
