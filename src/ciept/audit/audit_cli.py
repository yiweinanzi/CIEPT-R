from __future__ import annotations

import argparse
from pathlib import Path

from ciept.audit.adjudication import init_adjudication_queue
from ciept.audit.audit_dataset import build_audit_dataset
from ciept.audit.vlm_io import export_vlm_requests, merge_vlm_predictions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit dataset protocol CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser_ = subparsers.add_parser("build")
    build_parser_.add_argument("--stress-jsonl", required=True)
    build_parser_.add_argument("--output-dir", required=True)

    merge_parser = subparsers.add_parser("merge-vlm")
    merge_parser.add_argument("--audit-examples", required=True)
    merge_parser.add_argument("--predictions", required=True)
    merge_parser.add_argument("--manifest", required=True)
    merge_parser.add_argument("--output", required=True)

    adjudication_parser = subparsers.add_parser("init-adjudication")
    adjudication_parser.add_argument("--annotated-examples", required=True)
    adjudication_parser.add_argument("--output", required=True)

    requests_parser = subparsers.add_parser("export-vlm")
    requests_parser.add_argument("--audit-examples", required=True)
    requests_parser.add_argument("--output", required=True)
    requests_parser.add_argument("--prompt-version", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.command == "build":
        build_audit_dataset(Path(args.stress_jsonl), Path(args.output_dir))
        print(str(Path(args.output_dir) / "manifest.json"))
        return 0

    if args.command == "export-vlm":
        export_vlm_requests(Path(args.audit_examples), Path(args.output), args.prompt_version)
        print(str(Path(args.output)))
        return 0

    if args.command == "merge-vlm":
        merge_vlm_predictions(
            Path(args.audit_examples),
            Path(args.predictions),
            Path(args.manifest),
            Path(args.output),
        )
        print(str(Path(args.output)))
        return 0

    if args.command == "init-adjudication":
        init_adjudication_queue(Path(args.annotated_examples), Path(args.output))
        print(str(Path(args.output)))
        return 0

    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
