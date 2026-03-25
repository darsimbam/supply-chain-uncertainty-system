"""
build_real_data.py  —  Realistic FMCG Synthetic Generator
----------------------------------------------------------
No download required. Generates 60 grocery SKUs x 5 store locations x 3 years
of weekly demand with:
  - Category-authentic seasonal patterns (Christmas, summer, Easter, spring)
  - SKU-level growth / decline trends
  - Real sell-price variation per category
  - Promo event spikes (8 campaigns/year affecting category subsets)
  - Controlled WAPE spread: A/X items 10-20%, B/Y 25-45%, C/Z 45-70%
  - Natural Pareto ABC split and wide XYZ spread

Run from repo root:
    python data/build_real_data.py

Output:
    data/processed/master_data.csv
"""

import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import norm

# ── Paths ───────────────────────────────────────────────────────────────────────
ROOT     = Path(__file__).parent.parent
PROC_DIR = ROOT / "data" / "processed"
OUT_CSV  = PROC_DIR / "master_data.csv"
PROC_DIR.mkdir(parents=True, exist_ok=True)

RNG = np.random.default_rng(42)

# ── Timeline ─────────────────────────────────────────────────────────────────────
N_WEEKS    = 156                          # 3 years
START_DATE = pd.Timestamp("2022-01-03")   # Monday

# ── Stores: name -> volume scale factor ─────────────────────────────────────────
STORES = {
    "Store_North":   1.25,
    "Store_South":   1.00,
    "Store_East":    0.85,
    "Store_West":    0.68,
    "Store_Central": 1.40,
}

LT_BY_STORE = {
    "Store_North":   {"mean":  7, "std": 1},
    "Store_South":   {"mean":  7, "std": 1},
    "Store_East":    {"mean": 10, "std": 2},
    "Store_West":    {"mean": 14, "std": 3},
    "Store_Central": {"mean":  5, "std": 1},
}

# ── Financial parameters ─────────────────────────────────────────────────────────
HOLDING_RATE  = 0.20
MARGIN_RATE   = 0.30
EXPEDITE_MULT = 1.50
SL_BY_ABC     = {"A": 0.95, "B": 0.90, "C": 0.85}

# ── SKU catalogue ────────────────────────────────────────────────────────────────
# Columns: sku_id, category, base_units/wk/store, unit_price, season_profile,
#          annual_trend (fraction), demand_cv (noise level)
#
# Design intent:
#   A-class: base > 80,  cv < 0.35  →  X/Y  →  WAPE 10–25 %
#   B-class: base 25–80, cv 0.35–0.60 → Y   →  WAPE 25–45 %
#   C-class: base < 25,  cv > 0.60  →  Y/Z  →  WAPE 45–70 %

SKU_CATALOG = [
    # ── A-class (high volume, low noise) ──────────────────────────────────────
    ("SKU_A01", "DAIRY",     180, 1.25, "mild_xmas",  0.02, 0.18),
    ("SKU_A02", "DAIRY",     155, 1.40, "mild_xmas",  0.01, 0.20),
    ("SKU_A03", "DAIRY",     130, 2.10, "mild_xmas",  0.01, 0.22),
    ("SKU_A04", "DAIRY",     110, 1.85, "flat",       0.00, 0.15),
    ("SKU_A05", "BAKERY",    200, 1.10, "mild_xmas",  0.00, 0.12),
    ("SKU_A06", "BAKERY",    170, 0.90, "mild_xmas",  0.01, 0.14),
    ("SKU_A07", "BAKERY",    140, 1.50, "mild_xmas",  0.01, 0.18),
    ("SKU_A08", "BEVERAGES", 160, 0.85, "summer",     0.03, 0.25),
    ("SKU_A09", "BEVERAGES", 130, 1.20, "summer",     0.02, 0.28),
    ("SKU_A10", "BEVERAGES", 120, 1.05, "flat",       0.01, 0.20),
    ("SKU_A11", "SNACKS",    115, 1.80, "mild_xmas",  0.02, 0.25),
    ("SKU_A12", "SNACKS",    100, 2.20, "mild_xmas",  0.02, 0.28),
    ("SKU_A13", "HOUSEHOLD",  95, 3.50, "flat",       0.00, 0.14),
    ("SKU_A14", "HOUSEHOLD",  90, 2.80, "flat",       0.00, 0.16),
    ("SKU_A15", "FROZEN",     85, 2.50, "mild_xmas",  0.02, 0.22),
    # ── B-class (medium volume, moderate noise) ────────────────────────────────
    ("SKU_B01", "BEVERAGES",  70, 1.60, "summer",     0.04, 0.38),
    ("SKU_B02", "BEVERAGES",  65, 2.10, "summer",     0.03, 0.42),
    ("SKU_B03", "SNACKS",     60, 2.50, "xmas",       0.02, 0.44),
    ("SKU_B04", "SNACKS",     58, 1.90, "xmas",       0.02, 0.46),
    ("SKU_B05", "DAIRY",      55, 2.80, "mild_xmas",  0.01, 0.38),
    ("SKU_B06", "FROZEN",     52, 3.20, "mild_xmas",  0.02, 0.40),
    ("SKU_B07", "FROZEN",     48, 2.90, "mild_xmas",  0.03, 0.42),
    ("SKU_B08", "BAKERY",     45, 1.80, "xmas",       0.01, 0.45),
    ("SKU_B09", "PERSONAL",   42, 3.50, "flat",       0.01, 0.38),
    ("SKU_B10", "PERSONAL",   40, 4.20, "flat",       0.01, 0.40),
    ("SKU_B11", "HOUSEHOLD",  38, 4.80, "flat",       0.00, 0.36),
    ("SKU_B12", "HOUSEHOLD",  35, 3.90, "spring",     0.01, 0.42),
    ("SKU_B13", "BEVERAGES",  33, 2.40, "summer",     0.05, 0.50),
    ("SKU_B14", "SNACKS",     30, 3.10, "xmas",       0.03, 0.52),
    ("SKU_B15", "PERSONAL",   28, 5.50, "flat",       0.02, 0.46),
    ("SKU_B16", "FROZEN",     27, 3.80, "mild_xmas",  0.01, 0.48),
    ("SKU_B17", "DAIRY",      26, 3.20, "mild_xmas",  0.01, 0.52),
    ("SKU_B18", "BAKERY",     25, 2.10, "xmas",       0.01, 0.55),
    ("SKU_B19", "HOUSEHOLD",  26, 5.20, "spring",     0.00, 0.50),
    ("SKU_B20", "SNACKS",     27, 2.80, "xmas",       0.04, 0.55),
    # ── C-class (low volume, high noise / intermittent) ────────────────────────
    ("SKU_C01", "PERSONAL",   18, 7.50, "flat",       0.02, 0.75),
    ("SKU_C02", "PERSONAL",   15, 8.20, "flat",       0.02, 0.82),
    ("SKU_C03", "FROZEN",     14, 5.80, "xmas",       0.03, 0.85),
    ("SKU_C04", "BEVERAGES",  13, 4.50, "summer",     0.05, 0.82),
    ("SKU_C05", "SNACKS",     12, 6.20, "xmas",       0.04, 0.90),
    ("SKU_C06", "HOUSEHOLD",  11, 9.80, "flat",       0.01, 0.92),
    ("SKU_C07", "PERSONAL",   10, 12.0, "flat",       0.02, 0.95),
    ("SKU_C08", "FROZEN",      9, 7.20, "xmas",       0.03, 0.98),
    ("SKU_C09", "BAKERY",      8, 3.80, "spring",     0.01, 0.90),
    ("SKU_C10", "BEVERAGES",   8, 5.50, "summer",     0.06, 0.95),
    ("SKU_C11", "DAIRY",       7, 4.90, "mild_xmas",  0.01, 1.02),
    ("SKU_C12", "SNACKS",      7, 8.50, "xmas",       0.05, 1.08),
    ("SKU_C13", "HOUSEHOLD",   6, 11.0, "flat",       0.00, 1.12),
    ("SKU_C14", "PERSONAL",    6, 15.0, "flat",       0.02, 1.18),
    ("SKU_C15", "FROZEN",      5, 6.80, "xmas",       0.04, 1.20),
    ("SKU_C16", "BEVERAGES",   5, 7.20, "summer",     0.06, 1.15),
    ("SKU_C17", "SNACKS",      4, 9.50, "xmas",       0.05, 1.22),
    ("SKU_C18", "BAKERY",      4, 4.20, "spring",     0.02, 1.12),
    ("SKU_C19", "PERSONAL",    3, 18.0, "flat",       0.03, 1.28),
    ("SKU_C20", "HOUSEHOLD",   3, 14.0, "flat",       0.01, 1.35),
    ("SKU_C21", "FROZEN",      4, 8.90, "xmas",       0.04, 1.20),
    ("SKU_C22", "DAIRY",       5, 5.50, "mild_xmas",  0.02, 1.10),
    ("SKU_C23", "BEVERAGES",   4, 6.10, "summer",     0.07, 1.18),
    ("SKU_C24", "SNACKS",      3, 11.0, "xmas",       0.05, 1.25),
    ("SKU_C25", "PERSONAL",    2, 22.0, "flat",       0.03, 1.40),
]

# ── Promo calendar: (week_of_year, affected_categories, uplift_fraction) ─────────
# 8 campaigns per year; weeks are ISO week numbers
PROMO_EVENTS = [
    ( 4, {"SNACKS", "BEVERAGES"},                 0.30),   # January deals
    (14, {"DAIRY", "BAKERY", "SNACKS"},            0.25),   # Easter
    (17, {"HOUSEHOLD", "PERSONAL"},                0.20),   # Spring clean
    (22, {"BEVERAGES", "FROZEN"},                  0.28),   # Pre-summer
    (30, {"BEVERAGES", "SNACKS"},                  0.35),   # Summer peak
    (40, {"HOUSEHOLD", "PERSONAL"},                0.22),   # Back-to-school
    (48, {"SNACKS", "BEVERAGES", "FROZEN"},        0.40),   # Black Friday
    (50, {"DAIRY", "BAKERY", "FROZEN", "SNACKS"},  0.50),   # Christmas
]


# ── Seasonal index ───────────────────────────────────────────────────────────────
def seasonal_index(week_of_year: np.ndarray, profile: str) -> np.ndarray:
    """Return a multiplicative seasonal factor for each week."""
    w = week_of_year.astype(float)
    s = np.ones(len(w))

    if profile == "flat":
        return s

    if profile in ("mild_xmas", "xmas"):
        xmas_mult = 0.15 if profile == "mild_xmas" else 0.35
        # Smooth build from week 44, peak at week 51
        build  = np.clip((w - 44) / 8, 0, 1)
        s     += xmas_mult * build
        # Post-holiday dip weeks 1-3
        s     += np.where(w <= 3, -0.20, 0.0)

    if profile == "summer":
        # Gaussian bell centred at week 28 (July)
        s += 0.28 * np.exp(-0.5 * ((w - 28) / 7) ** 2)

    if profile == "spring":
        # Easter/spring clean peak around week 15
        s += 0.22 * np.exp(-0.5 * ((w - 15) / 4) ** 2)

    return np.clip(s, 0.30, 2.20)


# ── Demand generator ─────────────────────────────────────────────────────────────
def generate_demand(base: float, unit_price: float, season_profile: str,
                    annual_trend: float, cv: float,
                    store_scale: float, store: str,
                    category: str) -> tuple:
    """
    Generate N_WEEKS of weekly demand + promo flag for one SKU-store pair.
    Uses a Gamma distribution so demand is always non-negative.
    """
    weeks = pd.date_range(START_DATE, periods=N_WEEKS, freq="7D")
    iso_w = weeks.isocalendar().week.values.astype(float)

    # Trend: compound growth per week
    trend = (1 + annual_trend) ** (np.arange(N_WEEKS) / 52.0)

    # Seasonal
    season = seasonal_index(iso_w, season_profile)

    # Base expected demand
    mu = base * store_scale * trend * season

    # Promo uplift
    promo = np.zeros(N_WEEKS, dtype=int)
    for (promo_week, cats, uplift) in PROMO_EVENTS:
        if category in cats:
            # Apply to that ISO week across all 3 years
            hit = np.isin(iso_w, [promo_week])
            mu   = np.where(hit, mu * (1 + uplift), mu)
            promo = np.where(hit, 1, promo)

    # Store-specific jitter (±5 %) to break perfect correlation across stores
    mu *= RNG.uniform(0.95, 1.05, size=N_WEEKS)

    # Sample from Gamma (shape = 1/cv², scale = mu/shape)
    shape = max(1 / cv ** 2, 0.1)
    demand = RNG.gamma(shape=shape, scale=np.maximum(mu, 0.01) / shape)
    demand = np.round(np.clip(demand, 0, None), 0).astype(int)

    # Holiday flag: Nov-Dec (months 11-12) + first 2 weeks of Jan
    holiday = ((weeks.month >= 11) | (weeks.isocalendar().week <= 2)).astype(int).values

    return weeks, demand, promo, holiday


# ── Forecast (exponential smoothing + SKU-class bias) ────────────────────────────
def ses_forecast(demand: np.ndarray, sku_id: str, alpha: float = 0.25) -> np.ndarray:
    """
    SES with a systematic bias drawn per SKU so different SKUs have
    different forecast error profiles, producing wide WAPE spread.
    """
    d = demand.astype(float)
    f = np.zeros_like(d)
    f[0] = d[0]
    for i in range(1, len(d)):
        f[i] = alpha * d[i - 1] + (1 - alpha) * f[i - 1]

    # A-SKUs get tight noise, C-SKUs get loose noise (drives WAPE spread)
    if sku_id.startswith("SKU_A"):
        bias_range, noise_scale = (-0.06, 0.06), 0.10
    elif sku_id.startswith("SKU_B"):
        bias_range, noise_scale = (-0.12, 0.12), 0.20
    else:
        bias_range, noise_scale = (-0.20, 0.20), 0.35

    bias  = RNG.uniform(*bias_range)
    sigma = max(d.std(), 0.5) * noise_scale
    noise = RNG.normal(0, sigma, size=len(d))
    f     = np.clip(f * (1 + bias) + noise, 0, None).round(0)
    return f


# ── ABC / XYZ classification ─────────────────────────────────────────────────────
def classify(df: pd.DataFrame) -> pd.DataFrame:
    # ABC by cumulative revenue share (SKU level across all stores)
    sku_rev = (
        df.assign(rev=df["actual_demand"] * df["unit_cost"])
        .groupby("sku")["rev"].sum()
        .sort_values(ascending=False)
    )
    cum = sku_rev.cumsum() / sku_rev.sum()
    abc = cum.map(lambda p: "A" if p <= 0.80 else ("B" if p <= 0.95 else "C"))

    # XYZ by coefficient of variation (SKU level)
    cv_map = df.groupby("sku")["actual_demand"].agg(
        lambda x: x.std() / x.mean() if x.mean() > 0 else 0
    )
    xyz = cv_map.map(lambda c: "X" if c <= 0.50 else ("Y" if c <= 1.00 else "Z"))

    df["abc_class"] = df["sku"].map(abc)
    df["xyz_class"] = df["sku"].map(xyz)
    df["cv"]        = df["sku"].map(cv_map).round(3)
    return df


# ── Safety stock + reorder point ─────────────────────────────────────────────────
def add_ss_rop(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (sku, loc), grp in df.groupby(["sku", "location"]):
        d      = grp["actual_demand"].values.astype(float)
        avg_d  = d.mean()
        std_d  = d.std() if len(d) > 1 else 0
        sl     = grp["service_target"].iloc[0]
        lt     = grp["lead_time_mean"].iloc[0] / 7    # days -> weeks
        lt_std = grp["lead_time_std"].iloc[0]  / 7
        z      = norm.ppf(sl)
        ss     = max(z * np.sqrt(lt * std_d ** 2 + avg_d ** 2 * lt_std ** 2), 0)
        rop    = avg_d * lt + ss
        rows.append({"sku": sku, "location": loc,
                     "safety_stock": round(ss, 0), "reorder_point": round(rop, 0)})
    return df.merge(pd.DataFrame(rows), on=["sku", "location"])


# ── Main ─────────────────────────────────────────────────────────────────────────
def main() -> None:
    print("=== FMCG Synthetic Generator: 60 SKUs x 5 Stores x 3 Years ===\n")

    records = []
    for (sku_id, category, base, price, season, trend, cv) in SKU_CATALOG:
        for store, scale in STORES.items():
            weeks, demand, promo, holiday = generate_demand(
                base, price, season, trend, cv, scale, store, category
            )
            forecast = ses_forecast(demand, sku_id)
            lt = LT_BY_STORE[store]
            for i, w in enumerate(weeks):
                records.append({
                    "sku":          sku_id,
                    "location":     store,
                    "date":         w.date(),
                    "actual_demand": int(demand[i]),
                    "forecast":      int(forecast[i]),
                    "unit_cost":     round(price, 2),
                    "product_family": category,
                    "promo_flag":    int(promo[i]),
                    "holiday_flag":  int(holiday[i]),
                    "lead_time_mean": lt["mean"],
                    "lead_time_std":  lt["std"],
                    "holding_cost_rate": HOLDING_RATE,
                })

    df = pd.DataFrame(records)
    print(f"Generated: {len(df):,} rows")

    # Financial margins
    df["unit_margin"]             = (df["unit_cost"] * MARGIN_RATE).round(2)
    df["shortage_cost_per_unit"]  = (df["unit_margin"] * EXPEDITE_MULT).round(2)

    # ABC/XYZ
    df = classify(df)
    df["service_target"] = df["abc_class"].map(SL_BY_ABC)

    # SS / ROP
    df = add_ss_rop(df)

    # Simulated inventory position
    ss_vals   = df["safety_stock"].clip(lower=1).values
    df["on_hand"]       = np.round(RNG.uniform(ss_vals * 0.8, ss_vals * 2.5), 0)
    safe_cost = df["unit_cost"].clip(lower=0.01, upper=500).values
    df["on_order"]      = np.round(RNG.uniform(0, safe_cost * 50), 0)
    df["stockout_flag"] = (df["on_hand"] < df["actual_demand"]).astype(int)

    # Final column order
    cols = [
        "sku", "location", "date",
        "actual_demand", "forecast",
        "abc_class", "xyz_class", "cv",
        "promo_flag", "holiday_flag",
        "lead_time_mean", "lead_time_std",
        "unit_cost", "unit_margin",
        "holding_cost_rate", "shortage_cost_per_unit",
        "service_target",
        "safety_stock", "reorder_point",
        "on_hand", "on_order", "stockout_flag",
        "product_family",
    ]
    out = df[cols].sort_values(["sku", "location", "date"]).reset_index(drop=True)
    out.to_csv(OUT_CSV, index=False)

    # ── Summary ──────────────────────────────────────────────────────────────────
    print(f"\nSaved:      {OUT_CSV}")
    print(f"Rows:       {len(out):,}")
    print(f"SKUs:       {out['sku'].nunique()}")
    print(f"Locations:  {out['location'].nunique()}")
    print(f"Weeks:      {out['date'].nunique()}")
    print(f"Date range: {out['date'].min()} -> {out['date'].max()}")

    print("\nABC/XYZ breakdown (SKU-location pairs):")
    print(
        out.drop_duplicates(["sku", "location"])
        .groupby(["abc_class", "xyz_class"])
        .size()
        .rename("pairs")
        .to_string()
    )

    print("\nWAPE by ABC class:")
    out_w = out.copy()
    out_w["ae"]  = (out_w["actual_demand"] - out_w["forecast"]).abs()
    out_w["act"] = out_w["actual_demand"]
    wape = (
        out_w.groupby("abc_class")
        .apply(lambda g: g["ae"].sum() / (g["act"].sum() + 1e-9) * 100)
        .rename("WAPE_%")
        .round(1)
    )
    print(wape.to_string())

    print("\nDone.")


if __name__ == "__main__":
    main()
