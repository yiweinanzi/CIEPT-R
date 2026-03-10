from __future__ import annotations

import argparse
from pathlib import Path

from ciept.delivery.export import build_delivery_bundle


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a delivery bundle for the repository")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--project-root", default=".")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    build_delivery_bundle(
        project_root=Path(args.project_root).resolve(),
        output_dir=Path(args.output_dir).resolve(),
    )
    print(str(Path(args.output_dir).resolve()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
