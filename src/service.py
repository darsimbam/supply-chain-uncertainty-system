"""
service.py — Fill rate and cycle service level estimation.
"""

import numpy as np
from scipy.stats import norm


def cycle_service_level(safety_stock: float, sigma_lead_time_demand: float) -> float:
    """
    Probability of no stockout in a replenishment cycle.
    CSL = Phi(SS / sigma_LTD)
    """
    if sigma_lead_time_demand == 0:
        return 1.0
    z = safety_stock / sigma_lead_time_demand
    return norm.cdf(z)


def fill_rate_type2(
    safety_stock: float,
    sigma_lead_time_demand: float,
    order_quantity: float,
) -> float:
    """
    Type-2 service level (fill rate): fraction of demand met from stock.

    fill_rate = 1 - E(stockout units per cycle) / order_quantity
    """
    if order_quantity == 0 or sigma_lead_time_demand == 0:
        return 1.0
    z = safety_stock / sigma_lead_time_demand
    loss = norm.pdf(z) - z * (1 - norm.cdf(z))  # standard loss function
    expected_shortage = sigma_lead_time_demand * loss
    return 1 - expected_shortage / order_quantity


def simulate_fill_rate(
    demand_samples: np.ndarray,
    reorder_point: float,
    order_quantity: float,
    lead_time_samples: np.ndarray,
    n_simulations: int = 10_000,
) -> float:
    """
    Monte Carlo fill rate estimate.
    Returns fraction of demand units filled from stock across simulations.
    """
    total_demand = 0
    total_filled = 0
    rng = np.random.default_rng(42)

    for _ in range(n_simulations):
        d = rng.choice(demand_samples)
        lt = rng.choice(lead_time_samples)
        ltd = d * lt
        on_hand = reorder_point + order_quantity - ltd
        filled = min(max(on_hand, 0), d)
        total_demand += d
        total_filled += filled

    return total_filled / total_demand if total_demand > 0 else 1.0
