from __future__ import annotations

import argparse
from pathlib import Path

from ciept.data.stress_pipeline import generate_conflict_stress_dataset


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate conflict stress perturbation artifacts")
    parser.add_argument("--input-jsonl", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--strengths", nargs="*", type=float, default=[0.1, 0.3, 0.5])
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = generate_conflict_stress_dataset(
        input_jsonl=Path(args.input_jsonl),
        output_dir=Path(args.output_dir),
        strengths=list(args.strengths),
    )
    print(str(Path(args.output_dir) / "protocol_summary.json"))
    print(f"generated_records={summary['generated_records']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
