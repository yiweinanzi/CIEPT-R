from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class TransportProblem:
    cost: np.ndarray
    source_mass: np.ndarray
    target_capacity: np.ndarray
    mass_budget: float
    epsilon: float
    max_iters: int = 200
    tolerance: float = 1e-9


@dataclass(frozen=True)
class TransportResult:
    plan: np.ndarray
    transported_mass: float
    rejected_mass: float
    source_leftover: np.ndarray
    target_usage: np.ndarray
    target_slack: np.ndarray
    iterations: int
