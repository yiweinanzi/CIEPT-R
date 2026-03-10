from __future__ import annotations

import numpy as np

from ciept.transport.types import TransportProblem, TransportResult


def check_capacity_constraints(
    result: TransportResult,
    problem: TransportProblem,
    tolerance: float = 1e-6,
) -> bool:
    row_ok = np.all(result.plan.sum(axis=1) <= problem.source_mass + tolerance)
    col_ok = np.all(result.plan.sum(axis=0) <= problem.target_capacity + tolerance)
    mass_ok = result.transported_mass <= problem.mass_budget + tolerance
    return bool(row_ok and col_ok and mass_ok)


def check_reject_semantics(
    result: TransportResult,
    problem: TransportProblem,
    tolerance: float = 1e-6,
) -> bool:
    expected_reject = float(problem.source_mass.sum() - result.transported_mass)
    reject_ok = abs(result.rejected_mass - expected_reject) <= tolerance
    leftover_ok = abs(result.source_leftover.sum() - result.rejected_mass) <= tolerance
    return bool(reject_ok and leftover_ok and result.rejected_mass >= -tolerance)
