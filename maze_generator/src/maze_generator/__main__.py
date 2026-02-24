"""CLI entry point for maze-generator."""

from __future__ import annotations

import argparse
from pathlib import Path

from . import ExportOptions, maze_to_obj, maze_to_usd

_USD_SUFFIXES = {".usd", ".usda", ".usdc", ".usdz"}
_OBJ_NAME_HINTS = ("_obj", "_obj_bundle")


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
        help=(
            "Output format. If omitted, inferred from --output suffix "
            "(.obj => obj, .usd/.usda/.usdc/.usdz => usd) or *_obj name hint, "
            "otherwise defaults to usd."
        ),
    )
    parser.add_argument(
        "--frame",
        choices=("simulation", "config"),
        default="simulation",
        help=(
            "Output coordinate frame. 'simulation' flips map Y from config-image indexing; "
            "'config' preserves original layout indexing."
        ),
    )
    args = parser.parse_args()

    output_format = _resolve_format(args.format, args.output)
    output = _resolve_output_path(args.input, args.output, output_format)
    export_options = ExportOptions(target_frame=args.frame)

    if output_format == "usd":
        written_path = maze_to_usd(args.input, output, export_options=export_options)
    else:
        written_path = maze_to_obj(args.input, output, export_options=export_options)

    print(f"Wrote {written_path}")


def _resolve_format(format_arg: str | None, output_arg: str | None) -> str:
    if format_arg is not None:
        return format_arg
    if output_arg is not None:
        output_path = Path(output_arg)
        suffix = output_path.suffix.lower()
        if suffix == ".obj":
            return "obj"
        if suffix in _USD_SUFFIXES:
            return "usd"
        if not suffix and output_path.name.lower().endswith(_OBJ_NAME_HINTS):
            return "obj"
    return "usd"


def _resolve_output_path(input_path: str, output_arg: str | None, output_format: str) -> str:
    if output_arg is None:
        return _default_output_path(input_path, output_format)
    return _normalize_output_path(output_arg, output_format)


def _normalize_output_path(output_path: str, output_format: str) -> str:
    if output_format != "usd":
        return output_path

    output = Path(output_path)
    suffix = output.suffix.lower()
    if suffix in _USD_SUFFIXES:
        return output_path
    if suffix:
        return str(output.with_suffix(".usda"))
    return f"{output_path}.usda"


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
