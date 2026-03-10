from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ciept.transport.toy_solver import solve_partial_transport
from ciept.transport.types import TransportProblem


def test_solver_respects_mass_budget_and_constraints():
    problem = TransportProblem(
        cost=np.array([[0.1, 1.0], [0.2, 0.3]], dtype=float),
        source_mass=np.array([0.6, 0.5], dtype=float),
        target_capacity=np.array([0.4, 0.5], dtype=float),
        mass_budget=0.7,
        epsilon=0.1,
        max_iters=200,
        tolerance=1e-9,
    )

    result = solve_partial_transport(problem)

    assert result.plan.shape == (2, 2)
    assert np.all(result.plan.sum(axis=1) <= problem.source_mass + 1e-6)
    assert np.all(result.plan.sum(axis=0) <= problem.target_capacity + 1e-6)
    assert result.transported_mass <= problem.mass_budget + 1e-6
    assert abs(result.rejected_mass - (problem.source_mass.sum() - result.transported_mass)) < 1e-6


def test_solver_rejects_invalid_problem_shapes():
    problem = TransportProblem(
        cost=np.array([[0.1, 0.2]], dtype=float),
        source_mass=np.array([0.5, 0.5], dtype=float),
        target_capacity=np.array([0.6, 0.4], dtype=float),
        mass_budget=0.8,
        epsilon=0.1,
        max_iters=10,
        tolerance=1e-6,
    )

    with pytest.raises(ValueError, match="shape"):
        solve_partial_transport(problem)
