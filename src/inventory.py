"""
inventory.py — Safety stock and reorder point calculations.
"""

import numpy as np
from scipy.stats import norm


# --- Safety stock ---

def safety_stock_normal(
    sigma_demand: float,
    lead_time: float,
    sigma_lead_time: float,
    avg_demand: float,
    service_level: float,
) -> float:
    """
    Safety stock for normally distributed demand and lead time.

    Parameters
    ----------
    sigma_demand      : std dev of periodic demand
    lead_time         : average lead time (periods)
    sigma_lead_time   : std dev of lead time
    avg_demand        : average periodic demand
    service_level     : target CSL (e.g. 0.95)

    Returns
    -------
    Safety stock in units.
    """
    z = norm.ppf(service_level)
    ss = z * np.sqrt(lead_time * sigma_demand**2 + avg_demand**2 * sigma_lead_time**2)
    return ss


def safety_stock_simple(sigma_demand: float, lead_time: float, service_level: float) -> float:
    """Simplified safety stock assuming constant lead time."""
    z = norm.ppf(service_level)
    return z * sigma_demand * np.sqrt(lead_time)


# --- Reorder point ---

def reorder_point(avg_demand: float, lead_time: float, safety_stock: float) -> float:
    """
    ROP = expected lead-time demand + safety stock.
    """
    return avg_demand * lead_time + safety_stock


# --- Days on hand ---

def days_on_hand(on_hand: float, avg_daily_demand: float) -> float:
    if avg_daily_demand == 0:
        return float("inf")
    return on_hand / avg_daily_demand


# --- EOQ ---

def eoq(annual_demand: float, ordering_cost: float, holding_cost_per_unit: float) -> float:
    """Economic Order Quantity."""
    return np.sqrt(2 * annual_demand * ordering_cost / holding_cost_per_unit)
