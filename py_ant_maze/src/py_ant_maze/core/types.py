from typing import Any, Dict, List, TypeAlias

Spec: TypeAlias = Dict[str, Any]
MazeSpec: TypeAlias = Dict[str, Any]
ConfigSpec: TypeAlias = Dict[str, Any]
LayoutSpec: TypeAlias = Dict[str, Any]

MazeType: TypeAlias = str

Token: TypeAlias = str
GridValue: TypeAlias = int
GridRow: TypeAlias = List[GridValue]
Grid: TypeAlias = List[GridRow]
TokenRow: TypeAlias = List[Token]
TokenGrid: TypeAlias = List[TokenRow]
GridLines: TypeAlias = List[str]

ElementSpec: TypeAlias = Dict[str, Any]
ElementSpecList: TypeAlias = List[ElementSpec]

LayoutInput: TypeAlias = Any
