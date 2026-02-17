"""CLI entry point for maze-generator."""

from __future__ import annotations

import argparse
from pathlib import Path

from . import maze_to_obj, maze_to_usd

_USD_SUFFIXES = {".usd", ".usda", ".usdc", ".usdz"}


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="maze-generator",
        description="Generate maze geometry files (USD or OBJ) from a py-ant-maze YAML configuration.",
    )
    parser.add_argument("input", help="Path to a maze YAML file")
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output path (default: <input>.usda for USD, <input>_obj directory for OBJ)",
    )
    parser.add_argument(
        "--format",
        choices=("usd", "obj"),
        default=None,
        help="Output format. If omitted, inferred from --output suffix, otherwise defaults to usd.",
    )
    args = parser.parse_args()

    output_format = _resolve_format(args.format, args.output)
    output = args.output or _default_output_path(args.input, output_format)

    if output_format == "usd":
        written_path = maze_to_usd(args.input, output)
    else:
        written_path = maze_to_obj(args.input, output)

    print(f"Wrote {written_path}")


def _resolve_format(format_arg: str | None, output_arg: str | None) -> str:
    if format_arg is not None:
        return format_arg
    if output_arg is not None:
        suffix = Path(output_arg).suffix.lower()
        if suffix == ".obj":
            return "obj"
        if suffix in _USD_SUFFIXES:
            return "usd"
    return "usd"


def _default_output_path(input_path: str, output_format: str) -> str:
    path = Path(input_path)
    if output_format == "usd":
        if path.suffix:
            return str(path.with_suffix(".usda"))
        return f"{input_path}.usda"

    if path.suffix:
        return f"{path.with_suffix('')}_obj"
    return f"{input_path}_obj"


if __name__ == "__main__":
    main()
