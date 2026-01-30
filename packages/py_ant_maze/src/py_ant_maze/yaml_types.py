from typing import List


class LiteralStr(str):
    """Marker type for YAML literal block strings."""


class QuotedStr(str):
    """Marker type for YAML quoted strings (forces single quotes)."""


def literal_block(lines: List[str]) -> LiteralStr:
    return LiteralStr("\n".join(lines) + "\n")
