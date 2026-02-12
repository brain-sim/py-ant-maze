"""CLI entry point for maze-generator."""

from __future__ import annotations

import argparse
from pathlib import Path

from . import maze_to_usd


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="maze-generator",
        description="Generate a USD file from a py-ant-maze YAML configuration.",
    )
    parser.add_argument("input", help="Path to a maze YAML file")
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output USD file path (default: <input>.usda)",
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge walls with the same element name into one mesh",
    )
    args = parser.parse_args()

    output = args.output or _default_output_path(args.input)
    written_path = maze_to_usd(args.input, output, merge=args.merge)
    print(f"Wrote {written_path}")


def _default_output_path(input_path: str) -> str:
    path = Path(input_path)
    if path.suffix:
        return str(path.with_suffix(".usda"))
    return f"{input_path}.usda"


if __name__ == "__main__":
    main()
