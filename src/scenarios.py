"""
scenarios.py — ROI scenario comparison for uncertainty-reduction levers.
"""

import pandas as pd
from dataclasses import dataclass, field
from typing import List


@dataclass
class Scenario:
    name: str
    forecast_error_reduction: float = 0.0   # fraction, e.g. 0.10 = 10% less error
    lead_time_reduction: float = 0.0        # fraction reduction
    review_period_reduction: float = 0.0    # fraction reduction
    implementation_cost: float = 0.0        # one-time CHF
    annual_holding_saving: float = 0.0      # CHF/year
    annual_shortage_saving: float = 0.0     # CHF/year

    @property
    def annual_saving(self) -> float:
        return self.annual_holding_saving + self.annual_shortage_saving

    @property
    def roi(self) -> float:
        if self.implementation_cost == 0:
            return float("inf")
        return self.annual_saving / self.implementation_cost

    @property
    def payback_years(self) -> float:
        if self.annual_saving == 0:
            return float("inf")
        return self.implementation_cost / self.annual_saving


def compare_scenarios(scenarios: List[Scenario]) -> pd.DataFrame:
    records = []
    for s in scenarios:
        records.append({
            "Scenario": s.name,
            "Annual Saving (CHF)": round(s.annual_saving, 0),
            "Implementation Cost (CHF)": round(s.implementation_cost, 0),
            "ROI": round(s.roi, 2),
            "Payback (years)": round(s.payback_years, 2),
        })
    df = pd.DataFrame(records).sort_values("ROI", ascending=False)
    return df
