from .element_set import ElementSet
from .types import Grid, GridLines, LayoutInput, TokenRow, TokenGrid

_LARGE_GRID_THRESHOLD = 100
_LARGE_GRID_INTERVAL = 10
_GRID_PAD_CHAR = "_"


def parse_grid(layout: LayoutInput, elements: ElementSet) -> Grid:
    lines = _layout_to_lines(layout)
    cleaned = [line.rstrip() for line in lines if str(line).strip()]
    if not cleaned:
        raise ValueError("layout is empty")

    has_row_separators = any("|" in line for line in cleaned)
    rows: TokenGrid = []

    for line in cleaned:
        if has_row_separators:
            if "|" not in line:
                if _looks_like_header(line):
                    continue
                raise ValueError("layout row is missing a row separator")
            content = line.split("|", 1)[1]
        else:
            content = line

        tokens = _tokens_from_line(content)
        rows.append(tokens)

    if not rows:
        raise ValueError("layout is empty")

    width = len(rows[0])
    if width == 0:
        raise ValueError("layout must have at least one column")

    grid: Grid = []
    for row in rows:
        if len(row) != width:
            raise ValueError("all rows must have the same length")
        grid_row = []
        for token in row:
            try:
                element = elements.element_for_token(token)
            except KeyError as exc:
                raise ValueError(f"unknown layout token: {token}") from exc
            grid_row.append(element.value)
        grid.append(grid_row)

    return grid


def format_grid(
    grid: Grid,
    elements: ElementSet,
    with_grid_numbers: bool = False,
) -> GridLines:
    token_by_value = {el.value: el.token for el in elements.elements()}
    rows = [[token_by_value[cell] for cell in row] for row in grid]
    height = len(rows)
    width = len(rows[0]) if rows else 0

    if not with_grid_numbers:
        return ["".join(row) for row in rows]

    index_width = len(str(max(width - 1, height - 1, 0)))
    cell_width = max(1, index_width)
    interval = _LARGE_GRID_INTERVAL if max(width, height) > _LARGE_GRID_THRESHOLD else 1

    header_cells = []
    for col in range(width):
        if col % interval == 0:
            header_cells.append(f"{col:>{cell_width}}")
        else:
            header_cells.append(_GRID_PAD_CHAR * cell_width)
    header_prefix = _GRID_PAD_CHAR * (index_width + 2) + " "
    header = header_prefix + " ".join(header_cells)

    lines = [header]
    for row_index, row in enumerate(rows):
        row_label = (
            f"{row_index:>{index_width}}"
            if row_index % interval == 0
            else _GRID_PAD_CHAR * index_width
        )
        row_cells = [f"{token:>{cell_width}}" for token in row]
        line = f"{row_label} | " + " ".join(row_cells)
        lines.append(line)
    return lines


def _layout_to_lines(layout: LayoutInput) -> GridLines:
    if isinstance(layout, str):
        return layout.splitlines()
    if isinstance(layout, list):
        if all(isinstance(item, str) for item in layout):
            return layout
        if all(isinstance(item, (list, tuple)) for item in layout):
            lines = []
            for row in layout:
                tokens = []
                for cell in row:
                    if not isinstance(cell, str) or len(cell) != 1:
                        raise ValueError("layout rows must contain single-character strings")
                    tokens.append(cell)
                lines.append(" ".join(tokens))
            return lines
    raise TypeError("layout must be a string or list of strings")


def _tokens_from_line(line: str) -> TokenRow:
    condensed = "".join(ch for ch in line if not ch.isspace())
    if not condensed:
        raise ValueError("layout row is empty")
    return list(condensed)


def _looks_like_header(line: str) -> bool:
    tokens = line.strip().split()
    if not tokens:
        return True
    return all(token.isdigit() or _is_pad_token(token) for token in tokens)


def _is_pad_token(token: str) -> bool:
    return token and all(ch == _GRID_PAD_CHAR for ch in token)
