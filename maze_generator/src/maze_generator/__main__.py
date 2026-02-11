"""CLI entry point for maze-generator.

Usage:
    maze-generator input.yaml -o output.usda [--merge]
    python -m maze_generator input.yaml -o output.usda [--merge]
"""

from __future__ import annotations

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="maze-generator",
        description="Generate a USD file from a py-ant-maze YAML configuration.",
    )
    parser.add_argument("input", help="Path to a maze YAML file")
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output USD file path (default: <input>.usda)",
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge walls with the same element name into one mesh",
    )

    args = parser.parse_args()

    # Determine output path
    output = args.output
    if output is None:
        base = args.input.rsplit(".", 1)[0] if "." in args.input else args.input
        output = f"{base}.usda"

    try:
        from . import maze_to_usd
        maze_to_usd(args.input, output, merge=args.merge)
        print(f"Wrote {output}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
