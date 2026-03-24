"""
generate_sample_data.py
-----------------------
Generates a synthetic supply chain dataset shared across all 6 projects.

Run from the repo root:
    python data/sample/generate_sample_data.py

Outputs:
    data/sample/master_data.csv
"""

import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(42)
OUT = Path(__file__).parent / "master_data.csv"

# --- Configuration ---

N_SKUS = 50
N_WEEKS = 104  # 2 years
LOCATIONS = ["WH_NORTH", "WH_SOUTH"]

SKUS = [f"SKU_{str(i).zfill(3)}" for i in range(1, N_SKUS + 1)]

# Segment mix: 20% A, 30% B, 50% C
ABC = (
    ["A"] * 10
    + ["B"] * 15
    + ["C"] * 25
)

# Demand profiles per ABC class
DEMAND_PARAMS = {
    "A": {"mean": 500, "std": 80},
    "B": {"mean": 150, "std": 60},
    "C": {"mean": 30,  "std": 25},
}

# Variability class drives XYZ and forecast noise
CV_RANGES = {
    "A": (0.10, 0.30),
    "B": (0.30, 0.70),
    "C": (0.50, 1.50),
}

# Lead time params (days)
LT_PARAMS = {
    "A": {"mean": 14, "std": 2},
    "B": {"mean": 21, "std": 4},
    "C": {"mean": 28, "std": 7},
}

# Financial params
UNIT_COST_RANGE = {
    "A": (80, 300),
    "B": (20, 80),
    "C": (5, 20),
}
MARGIN_RATE = 0.30       # margin as fraction of unit cost
HOLDING_COST_RATE = 0.20 # annual
SHORTAGE_COST_MULT = 1.5 # shortage cost = margin * multiplier


def assign_xyz(cv: float) -> str:
    if cv <= 0.5:
        return "X"
    elif cv <= 1.0:
        return "Y"
    return "Z"


def make_demand(abc: str, n_weeks: int, cv_range: tuple) -> np.ndarray:
    params = DEMAND_PARAMS[abc]
    cv = RNG.uniform(*cv_range)
    std = params["mean"] * cv
    demand = RNG.normal(loc=params["mean"], scale=std, size=n_weeks)
    demand = np.clip(demand, 0, None).round(0)
    return demand, cv


def make_forecast(demand: np.ndarray, noise_scale: float = 0.15) -> np.ndarray:
    """Naive forecast + bias + noise."""
    bias_factor = RNG.uniform(-0.10, 0.10)
    noise = RNG.normal(0, demand.std() * noise_scale, size=len(demand))
    forecast = demand * (1 + bias_factor) + noise
    forecast = np.clip(forecast, 0, None).round(0)
    return forecast


def main():
    weeks = pd.date_range("2023-01-02", periods=N_WEEKS, freq="W-MON")
    rows = []

    for sku, abc in zip(SKUS, ABC):
        cv_range = CV_RANGES[abc]
        lt_params = LT_PARAMS[abc]

        demand, cv = make_demand(abc, N_WEEKS, cv_range)
        forecast = make_forecast(demand)
        xyz = assign_xyz(cv)

        unit_cost = round(RNG.uniform(*UNIT_COST_RANGE[abc]), 2)
        unit_margin = round(unit_cost * MARGIN_RATE, 2)
        lead_time_mean = lt_params["mean"]
        lead_time_std = lt_params["std"]

        for loc in LOCATIONS:
            # Slight location multiplier
            loc_factor = 1.0 if loc == "WH_NORTH" else RNG.uniform(0.6, 0.9)
            loc_demand = (demand * loc_factor).round(0)
            loc_forecast = (forecast * loc_factor).round(0)

            # Safety stock and ROP (simplified for data generation)
            sigma_d = loc_demand.std()
            z = 1.645  # 95% CSL
            ss = round(z * np.sqrt(lead_time_mean * sigma_d**2 + loc_demand.mean()**2 * lead_time_std**2), 0)
            rop = round(loc_demand.mean() * lead_time_mean / 7 + ss, 0)  # lead time in weeks

            for i, week in enumerate(weeks):
                # Promo: random 5% of weeks
                promo = int(RNG.random() < 0.05)
                holiday = int(week.month == 12 and week.day >= 20)

                # On-hand: simplified random position
                on_hand = round(RNG.uniform(ss * 0.5, ss * 3), 0)
                on_order = round(RNG.uniform(0, loc_demand.mean() * 2), 0)
                stockout = int(on_hand < loc_demand[i])

                rows.append({
                    "sku": sku,
                    "location": loc,
                    "date": week.date(),
                    "actual_demand": loc_demand[i],
                    "forecast": loc_forecast[i],
                    "abc_class": abc,
                    "xyz_class": xyz,
                    "cv": round(cv, 3),
                    "promo_flag": promo,
                    "holiday_flag": holiday,
                    "lead_time_mean": lead_time_mean,
                    "lead_time_std": lead_time_std,
                    "unit_cost": unit_cost,
                    "unit_margin": unit_margin,
                    "holding_cost_rate": HOLDING_COST_RATE,
                    "shortage_cost_per_unit": round(unit_margin * SHORTAGE_COST_MULT, 2),
                    "service_target": 0.95 if abc == "A" else (0.90 if abc == "B" else 0.85),
                    "safety_stock": ss,
                    "reorder_point": rop,
                    "on_hand": on_hand,
                    "on_order": on_order,
                    "stockout_flag": stockout,
                    "product_family": f"FAM_{abc}",
                })

    df = pd.DataFrame(rows)
    df.to_csv(OUT, index=False)
    print(f"Saved {len(df):,} rows -> {OUT}")
    print(df.groupby(["abc_class", "xyz_class"]).size().rename("rows"))


if __name__ == "__main__":
    main()
