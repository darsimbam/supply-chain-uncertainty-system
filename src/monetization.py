"""
monetization.py — Shortage and excess cost calculations.
"""


def shortage_cost(
    units_short: float,
    unit_margin: float,
    expedite_cost_per_unit: float = 0.0,
) -> float:
    """
    Expected cost of a shortage event.
    shortage_cost = units_short * (unit_margin + expedite_cost)
    """
    return units_short * (unit_margin + expedite_cost_per_unit)


def excess_cost(
    excess_units: float,
    unit_cost: float,
    holding_cost_rate: float,
    periods: float = 1.0,
    markdown_rate: float = 0.0,
) -> float:
    """
    Cost of holding excess inventory.
    excess_cost = excess_units * unit_cost * holding_cost_rate * periods
                + markdown_loss
    """
    holding = excess_units * unit_cost * holding_cost_rate * periods
    markdown = excess_units * unit_cost * markdown_rate
    return holding + markdown


def expected_loss(
    stockout_prob: float,
    units_short: float,
    unit_margin: float,
    excess_prob: float,
    excess_units: float,
    unit_cost: float,
    holding_cost_rate: float,
) -> dict:
    """
    Combined expected financial risk from shortage and excess.
    """
    exp_shortage = stockout_prob * shortage_cost(units_short, unit_margin)
    exp_excess = excess_prob * excess_cost(excess_units, unit_cost, holding_cost_rate)
    return {
        "expected_shortage_cost": exp_shortage,
        "expected_excess_cost": exp_excess,
        "total_expected_loss": exp_shortage + exp_excess,
    }
