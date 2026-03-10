from __future__ import annotations

import numpy as np

from ciept.transport.types import TransportProblem, TransportResult


def _validate_problem(problem: TransportProblem) -> None:
    if problem.cost.ndim != 2:
        raise ValueError("Cost matrix shape must be two-dimensional")

    expected_shape = (problem.source_mass.shape[0], problem.target_capacity.shape[0])
    if problem.cost.shape != expected_shape:
        raise ValueError("Cost matrix shape must match source and target masses")

    if np.any(problem.source_mass < 0.0):
        raise ValueError("Source masses must be non-negative")
    if np.any(problem.target_capacity < 0.0):
        raise ValueError("Target capacities must be non-negative")
    if problem.mass_budget <= 0.0:
        raise ValueError("Mass budget must be positive")
    if problem.epsilon <= 0.0:
        raise ValueError("Epsilon must be positive")


def _project_rows(plan: np.ndarray, source_mass: np.ndarray, eps: float) -> np.ndarray:
    row_sums = plan.sum(axis=1)
    scale = np.minimum(1.0, source_mass / np.maximum(row_sums, eps))
    return plan * scale[:, None]


def _project_cols(plan: np.ndarray, target_capacity: np.ndarray, eps: float) -> np.ndarray:
    col_sums = plan.sum(axis=0)
    scale = np.minimum(1.0, target_capacity / np.maximum(col_sums, eps))
    return plan * scale[None, :]


def solve_partial_transport(problem: TransportProblem) -> TransportResult:
    _validate_problem(problem)

    desired_mass = min(
        float(problem.mass_budget),
        float(problem.source_mass.sum()),
        float(problem.target_capacity.sum()),
    )
    if desired_mass <= 0.0:
        raise ValueError("Problem does not allow any positive transported mass")

    kernel = np.exp(-problem.cost / problem.epsilon)
    kernel_sum = float(kernel.sum())
    if not np.isfinite(kernel_sum) or kernel_sum <= 0.0:
        raise ValueError("Kernel initialization failed")

    plan = kernel / kernel_sum * desired_mass
    iterations = 0

    for iteration in range(1, problem.max_iters + 1):
        previous = plan.copy()
        plan = _project_rows(plan, problem.source_mass, problem.tolerance)
        plan = _project_cols(plan, problem.target_capacity, problem.tolerance)

        total_mass = float(plan.sum())
        if total_mass > desired_mass + problem.tolerance:
            plan *= desired_mass / total_mass
        elif 0.0 < total_mass < desired_mass - problem.tolerance:
            plan *= desired_mass / total_mass
            plan = _project_rows(plan, problem.source_mass, problem.tolerance)
            plan = _project_cols(plan, problem.target_capacity, problem.tolerance)

        if not np.all(np.isfinite(plan)):
            raise ValueError("Transport plan contains NaN or Inf")

        delta = float(np.max(np.abs(plan - previous)))
        iterations = iteration
        if delta <= problem.tolerance:
            break

    source_usage = plan.sum(axis=1)
    target_usage = plan.sum(axis=0)
    transported_mass = float(plan.sum())
    rejected_mass = float(problem.source_mass.sum() - transported_mass)

    return TransportResult(
        plan=plan,
        transported_mass=transported_mass,
        rejected_mass=rejected_mass,
        source_leftover=np.maximum(problem.source_mass - source_usage, 0.0),
        target_usage=target_usage,
        target_slack=np.maximum(problem.target_capacity - target_usage, 0.0),
        iterations=iterations,
    )
