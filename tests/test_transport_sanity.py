from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.transport.sanity import check_capacity_constraints, check_reject_semantics
from ciept.transport.toy_solver import solve_partial_transport
from ciept.transport.types import TransportProblem


def test_target_capacity_binding_saturates_small_capacity_target():
    problem = TransportProblem(
        cost=np.array([[0.01, 0.5], [0.02, 0.6]], dtype=float),
        source_mass=np.array([0.4, 0.4], dtype=float),
        target_capacity=np.array([0.2, 0.6], dtype=float),
        mass_budget=0.8,
        epsilon=0.05,
        max_iters=300,
        tolerance=1e-9,
    )

    result = solve_partial_transport(problem)

    assert check_capacity_constraints(result, problem)
    assert abs(result.target_usage[0] - 0.2) < 1e-4
    assert result.target_usage[1] > 0.5


def test_reject_over_bad_match_prefers_low_cost_alignment():
    problem = TransportProblem(
        cost=np.array([[0.01, 0.05], [4.0, 5.0]], dtype=float),
        source_mass=np.array([0.4, 0.6], dtype=float),
        target_capacity=np.array([0.5, 0.5], dtype=float),
        mass_budget=0.5,
        epsilon=0.1,
        max_iters=300,
        tolerance=1e-9,
    )

    result = solve_partial_transport(problem)

    assert check_reject_semantics(result, problem)
    assert result.plan[0].sum() > result.plan[1].sum()
    assert result.rejected_mass > 0.49
