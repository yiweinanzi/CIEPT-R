from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ExperimentContext:
    experiment_name: str
    run_id: str
    results_root: Path


@dataclass(frozen=True)
class ExperimentResult:
    experiment_name: str
    run_id: str
    metrics: dict[str, float]
    artifacts: dict[str, str] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
