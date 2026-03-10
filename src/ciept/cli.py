import argparse

from ciept.config import load_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CIEPT-R bootstrap CLI")
    parser.add_argument("--config", required=True, help="Path to YAML config file")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = load_config(args.config)
    project = config.get("project", {})
    paths = config.get("paths", {})

    print(f"Project: {project.get('name', 'unknown')}")
    print(f"Seed: {project.get('seed', 'unknown')}")
    print(f"Root: {paths.get('root', '.')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
