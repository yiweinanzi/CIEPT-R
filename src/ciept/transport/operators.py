from __future__ import annotations

import torch


def _as_scalar_tensor(value: torch.Tensor | float, device: torch.device, dtype: torch.dtype) -> torch.Tensor:
    if isinstance(value, torch.Tensor):
        if value.numel() != 1:
            raise ValueError("Mass budget tensor must be scalar")
        return value.to(device=device, dtype=dtype).reshape(())
    return torch.tensor(float(value), device=device, dtype=dtype)


def _project_rows(plan: torch.Tensor, source_mass: torch.Tensor, eps: float) -> torch.Tensor:
    row_sums = plan.sum(dim=1)
    scale = torch.minimum(torch.ones_like(row_sums), source_mass / row_sums.clamp_min(eps))
    return plan * scale.unsqueeze(1)


def _project_cols(plan: torch.Tensor, target_capacity: torch.Tensor, eps: float) -> torch.Tensor:
    col_sums = plan.sum(dim=0)
    scale = torch.minimum(torch.ones_like(col_sums), target_capacity / col_sums.clamp_min(eps))
    return plan * scale.unsqueeze(0)


def torch_partial_transport(
    cost: torch.Tensor,
    source_mass: torch.Tensor,
    target_capacity: torch.Tensor,
    mass_budget: torch.Tensor | float,
    epsilon: float,
    max_iters: int = 200,
    tolerance: float = 1e-9,
) -> torch.Tensor:
    if cost.ndim != 2:
        raise ValueError("Cost matrix must be rank-2")
    if source_mass.ndim != 1 or target_capacity.ndim != 1:
        raise ValueError("source_mass and target_capacity must be rank-1")
    if cost.shape != (source_mass.shape[0], target_capacity.shape[0]):
        raise ValueError("Cost matrix shape must match source and target masses")
    if torch.any(source_mass < 0):
        raise ValueError("Source masses must be non-negative")
    if torch.any(target_capacity < 0):
        raise ValueError("Target capacities must be non-negative")
    if epsilon <= 0:
        raise ValueError("Epsilon must be positive")

    budget = _as_scalar_tensor(mass_budget, device=cost.device, dtype=cost.dtype)
    if budget.item() <= 0:
        raise ValueError("Mass budget must be positive")

    desired_mass = torch.minimum(
        budget,
        torch.minimum(source_mass.sum(), target_capacity.sum()),
    )
    if desired_mass.item() <= 0:
        raise ValueError("No positive transported mass is possible")

    kernel = torch.exp(-cost / epsilon)
    kernel_sum = kernel.sum()
    if not torch.isfinite(kernel_sum) or kernel_sum.item() <= 0:
        raise ValueError("Kernel initialization failed")

    plan = kernel / kernel_sum * desired_mass
    for _ in range(max_iters):
        previous = plan.clone()
        plan = _project_rows(plan, source_mass, tolerance)
        plan = _project_cols(plan, target_capacity, tolerance)

        total_mass = plan.sum()
        if total_mass.item() > desired_mass.item() + tolerance:
            plan = plan * (desired_mass / total_mass)
        elif 0.0 < total_mass.item() < desired_mass.item() - tolerance:
            plan = plan * (desired_mass / total_mass)
            plan = _project_rows(plan, source_mass, tolerance)
            plan = _project_cols(plan, target_capacity, tolerance)

        if not torch.isfinite(plan).all():
            raise ValueError("Transport plan contains NaN or Inf")

        delta = torch.max(torch.abs(plan - previous)).item()
        if delta <= tolerance:
            break

    return plan
