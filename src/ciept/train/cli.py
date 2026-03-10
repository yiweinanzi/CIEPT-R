from __future__ import annotations

import argparse

from ciept.train.engine import build_toy_batch, eval_step, train_step
from ciept.transport.reranker import CapacityCalibratedPartialTransportReranker


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Toy training/evaluation entrypoint for CIEPT-R")
    parser.add_argument("--mode", choices=["train", "eval"], required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    reranker = CapacityCalibratedPartialTransportReranker()
    batch = build_toy_batch()

    if args.mode == "train":
        outputs = train_step(reranker, batch, tau=0.5, lambda_intervention=0.5)
        print(f"ranking_loss={outputs['ranking_loss'].item():.6f}")
        print(f"intervention_loss={outputs['intervention_loss'].item():.6f}")
        print(f"total_loss={outputs['total_loss'].item():.6f}")
        return 0

    if args.mode == "eval":
        metrics = eval_step(reranker, batch)
        print(f"recall_at_1={metrics['recall_at_1']:.6f}")
        print(f"mrr={metrics['mrr']:.6f}")
        return 0

    raise ValueError(f"Unsupported mode: {args.mode}")


if __name__ == "__main__":
    raise SystemExit(main())
