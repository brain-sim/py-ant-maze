from typing import List, TypeAlias


class LiteralStr(str):
    """Marker type for YAML literal block strings."""


class QuotedStr(str):
    """Marker type for YAML quoted strings (forces single quotes)."""


Lines: TypeAlias = List[str]


def literal_block(lines: Lines) -> LiteralStr:
    return LiteralStr("\n".join(lines) + "\n")
