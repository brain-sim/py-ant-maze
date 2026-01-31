from __future__ import annotations

from abc import ABC, abstractmethod

from .types import ConfigSpec, LayoutSpec


class ConfigBase(ABC):
    @classmethod
    @abstractmethod
    def from_spec(cls, spec: ConfigSpec) -> "ConfigBase":
        raise NotImplementedError

    @abstractmethod
    def to_spec(self) -> ConfigSpec:
        raise NotImplementedError


class LayoutBase(ABC):
    @classmethod
    @abstractmethod
    def from_spec(cls, spec: LayoutSpec, config: ConfigBase) -> "LayoutBase":
        raise NotImplementedError

    @abstractmethod
    def to_spec(self, config: ConfigBase, with_grid_numbers: bool) -> LayoutSpec:
        raise NotImplementedError
