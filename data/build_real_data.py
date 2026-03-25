"""
build_real_data.py
------------------
Downloads the M5 Forecasting Competition dataset (Walmart grocery / FMCG store
sales) and transforms it into the master_data.csv schema used by all 6 portfolio
notebooks.

Prerequisites
-------------
    pip install kaggle
    # Get your API token from https://www.kaggle.com/settings  (API section)
    # Save the downloaded kaggle.json to  ~/.kaggle/kaggle.json
    # On Windows: C:\\Users\\<you>\\.kaggle\\kaggle.json

Run from repo root:
    python data/build_real_data.py

Outputs:
    data/raw/m5/           (raw M5 files, cached)
    data/processed/master_data.csv
"""

import subprocess
import zipfile
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import norm

# ── Paths ───────────────────────────────────────────────────────────────────────
ROOT     = Path(__file__).parent.parent
RAW_DIR  = ROOT / "data" / "raw" / "m5"
PROC_DIR = ROOT / "data" / "processed"
OUT_CSV  = PROC_DIR / "master_data.csv"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROC_DIR.mkdir(parents=True, exist_ok=True)

# ── Parameters ──────────────────────────────────────────────────────────────────
DEPT_ID        = "FOODS_3"       # Grocery department — continuous weekly demand
TOP_N_ITEMS    = 50              # top SKUs by total units sold
STORES         = ["CA_1", "CA_2", "TX_1", "TX_2", "WI_1"]
DATE_START     = "2013-01-07"    # ~3 years of weekly data
HOLDING_RATE   = 0.20
MARGIN_RATE    = 0.30
EXPEDITE_MULT  = 1.50
SL_BY_ABC      = {"A": 0.95, "B": 0.90, "C": 0.85}

# Lead-time assumptions by store location (days)
LT_BY_STORE = {
    "CA_1": {"mean":  5, "std": 1},
    "CA_2": {"mean":  5, "std": 1},
    "TX_1": {"mean": 10, "std": 2},
    "TX_2": {"mean": 10, "std": 2},
    "WI_1": {"mean": 14, "std": 3},
}

RNG = np.random.default_rng(42)


# ── Step 1: Download ────────────────────────────────────────────────────────────
def download_m5() -> None:
    if (RAW_DIR / "calendar.csv").exists():
        print("M5 files already cached.")
        return

    print("Downloading M5 dataset via Kaggle API (~110 MB)...")
    try:
        subprocess.run(
            ["kaggle", "competitions", "download",
             "-c", "m5-forecasting-accuracy", "-p", str(RAW_DIR)],
            check=True,
        )
    except FileNotFoundError:
        raise SystemExit(
            "\nkaggle CLI not found.\n"
            "  pip install kaggle\n"
            "  Then save your API token to ~/.kaggle/kaggle.json\n"
            "  (get it from https://www.kaggle.com/settings > API > Create New Token)"
        )

    zip_path = RAW_DIR / "m5-forecasting-accuracy.zip"
    if zip_path.exists():
        print("Extracting...")
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(RAW_DIR)
        print(f"Extracted to {RAW_DIR}")


# ── Step 2: Load raw files ──────────────────────────────────────────────────────
def load_m5() -> tuple:
    print("Loading M5 files...")
    cal    = pd.read_csv(RAW_DIR / "calendar.csv",              parse_dates=["date"])
    sales  = pd.read_csv(RAW_DIR / "sales_train_evaluation.csv")
    prices = pd.read_csv(RAW_DIR / "sell_prices.csv")
    print(f"  calendar:  {len(cal):,} rows")
    print(f"  sales:     {len(sales):,} rows")
    print(f"  prices:    {len(prices):,} rows")
    return cal, sales, prices


# ── Step 3: Filter, melt, aggregate ────────────────────────────────────────────
def filter_and_reshape(cal: pd.DataFrame, sales: pd.DataFrame,
                       prices: pd.DataFrame) -> pd.DataFrame:
    # Filter to target department + selected stores
    mask = (sales["dept_id"] == DEPT_ID) & (sales["store_id"].isin(STORES))
    foods = sales[mask].copy()

    # Identify day-columns then select top-N items by total units
    d_cols = [c for c in foods.columns if c.startswith("d_")]
    top_items = (
        foods.groupby("item_id")[d_cols].sum().sum(axis=1)
        .nlargest(TOP_N_ITEMS).index
    )
    foods = foods[foods["item_id"].isin(top_items)]
    print(f"Filtered: {foods['item_id'].nunique()} items x {foods['store_id'].nunique()} stores")

    # Melt wide -> long (only selected items — much smaller)
    id_cols = ["item_id", "store_id"]
    long = foods[id_cols + d_cols].melt(
        id_vars=id_cols, var_name="d", value_name="daily_sales"
    )

    # Join calendar to get date + week number + event flags
    cal_sub = cal[["d", "date", "wm_yr_wk", "event_type_1", "event_type_2"]].copy()
    long = long.merge(cal_sub, on="d")
    long = long[long["date"] >= DATE_START]

    # Monday-anchored week floor
    long["week"] = long["date"] - pd.to_timedelta(long["date"].dt.dayofweek, unit="D")

    # Flag weeks that contain a calendar event (promo) or are in Nov/Dec (holiday)
    long["has_event"]   = long["event_type_1"].notna() | long["event_type_2"].notna()
    long["is_holiday"]  = long["date"].dt.month.isin([11, 12])

    # Aggregate daily -> weekly
    weekly = (
        long.groupby(["item_id", "store_id", "week", "wm_yr_wk"])
        .agg(
            actual_demand=("daily_sales",  "sum"),
            promo_flag   =("has_event",    "max"),
            holiday_flag =("is_holiday",   "max"),
        )
        .reset_index()
    )
    weekly["promo_flag"]   = weekly["promo_flag"].astype(int)
    weekly["holiday_flag"] = weekly["holiday_flag"].astype(int)

    # Join sell prices (wm_yr_wk links weeks to prices)
    prices_sub = prices[
        prices["store_id"].isin(STORES) & prices["item_id"].isin(top_items)
    ].copy()
    weekly = weekly.merge(
        prices_sub[["store_id", "item_id", "wm_yr_wk", "sell_price"]],
        on=["store_id", "item_id", "wm_yr_wk"],
        how="left",
    )

    # Forward/back fill price per SKU-location, fallback to item mean
    weekly = weekly.sort_values(["item_id", "store_id", "week"])
    weekly["sell_price"] = (
        weekly.groupby(["item_id", "store_id"])["sell_price"]
        .transform(lambda s: s.ffill().bfill())
    )
    weekly["sell_price"] = weekly["sell_price"].fillna(
        weekly.groupby("item_id")["sell_price"].transform("mean")
    )

    # Build full date spine to ensure no gaps
    all_weeks = pd.date_range(weekly["week"].min(), weekly["week"].max(), freq="7D")
    spine = pd.DataFrame(
        [(i, s, w) for i in top_items for s in STORES for w in all_weeks],
        columns=["item_id", "store_id", "week"],
    )
    weekly = spine.merge(
        weekly.drop(columns="wm_yr_wk"), on=["item_id", "store_id", "week"], how="left"
    )
    weekly["actual_demand"] = weekly["actual_demand"].fillna(0).astype(int)
    weekly["promo_flag"]    = weekly["promo_flag"].fillna(0).astype(int)
    weekly["holiday_flag"]  = weekly["holiday_flag"].fillna(0).astype(int)
    weekly["sell_price"]    = (
        weekly.groupby(["item_id", "store_id"])["sell_price"]
        .transform(lambda s: s.ffill().bfill())
    )

    print(f"Weekly grid: {len(weekly):,} rows | {weekly['item_id'].nunique()} items | {weekly['store_id'].nunique()} stores | {weekly['week'].nunique()} weeks")
    return weekly


# ── Step 4: Derive forecast (exponential smoothing + realistic noise) ───────────
def add_forecast(weekly: pd.DataFrame, alpha: float = 0.25) -> pd.DataFrame:
    forecasts = []
    for (item, store), grp in weekly.groupby(["item_id", "store_id"]):
        grp = grp.sort_values("week")
        d   = grp["actual_demand"].values.astype(float)
        f   = np.zeros_like(d)
        f[0] = d[0]
        for i in range(1, len(d)):
            f[i] = alpha * d[i - 1] + (1 - alpha) * f[i - 1]
        # Systematic bias + noise — drives WAPE variance across SKUs
        bias  = RNG.uniform(-0.12, 0.12)
        sigma = max(d.std(), 0.1) * 0.18
        noise = RNG.normal(0, sigma, size=len(d))
        f     = np.clip(f * (1 + bias) + noise, 0, None).round(0)
        forecasts.append(pd.Series(f, index=grp.index))

    weekly["forecast"] = pd.concat(forecasts).sort_index()
    return weekly


# ── Step 5: Derive all policy and financial fields ──────────────────────────────
def derive_fields(weekly: pd.DataFrame) -> pd.DataFrame:

    # ── ABC: cumulative revenue share by item (across all stores) ──
    item_rev = (
        weekly.assign(revenue=weekly["actual_demand"] * weekly["sell_price"].fillna(1))
        .groupby("item_id")["revenue"].sum()
        .sort_values(ascending=False)
    )
    cum_pct = item_rev.cumsum() / item_rev.sum()
    abc_map = {
        item: ("A" if cum_pct[item] <= 0.80 else ("B" if cum_pct[item] <= 0.95 else "C"))
        for item in item_rev.index
    }

    # ── XYZ: coefficient of variation per item ──
    item_cv = weekly.groupby("item_id")["actual_demand"].agg(
        lambda x: (x.std() / x.mean()) if x.mean() > 0 else 0
    )
    xyz_map = {
        item: ("X" if cv <= 0.5 else ("Y" if cv <= 1.0 else "Z"))
        for item, cv in item_cv.items()
    }

    weekly["abc_class"]      = weekly["item_id"].map(abc_map)
    weekly["xyz_class"]      = weekly["item_id"].map(xyz_map)
    weekly["cv"]             = weekly["item_id"].map(item_cv).round(3)
    # product_family: e.g. FOODS_3 -> strip last segment so items group nicely
    weekly["product_family"] = weekly["item_id"].str.rsplit("_", n=1).str[0]

    # ── Rename core fields ──
    weekly = weekly.rename(columns={
        "item_id":    "sku",
        "store_id":   "location",
        "week":       "date",
        "sell_price": "unit_cost",
    })
    weekly["date"] = weekly["date"].dt.date

    # ── Financial ──
    weekly["unit_cost"]              = weekly["unit_cost"].round(2)
    weekly["unit_margin"]            = (weekly["unit_cost"] * MARGIN_RATE).round(2)
    weekly["holding_cost_rate"]      = HOLDING_RATE
    weekly["shortage_cost_per_unit"] = (weekly["unit_margin"] * EXPEDITE_MULT).round(2)
    weekly["service_target"]         = weekly["abc_class"].map(SL_BY_ABC)

    # ── Lead times ──
    weekly["lead_time_mean"] = weekly["location"].map(
        lambda l: LT_BY_STORE.get(l, {"mean": 7})["mean"]
    )
    weekly["lead_time_std"]  = weekly["location"].map(
        lambda l: LT_BY_STORE.get(l, {"std": 2})["std"]
    )

    # ── Safety stock + reorder point ──
    ss_rop_rows = []
    for (sku, loc), grp in weekly.groupby(["sku", "location"]):
        d      = grp["actual_demand"].values.astype(float)
        avg_d  = d.mean()
        std_d  = d.std() if len(d) > 1 else 0
        sl     = grp["service_target"].iloc[0]
        lt     = grp["lead_time_mean"].iloc[0] / 7      # convert days -> weeks
        lt_std = grp["lead_time_std"].iloc[0]  / 7
        z      = norm.ppf(sl)
        ss     = max(z * np.sqrt(lt * std_d ** 2 + avg_d ** 2 * lt_std ** 2), 0)
        rop    = avg_d * lt + ss
        ss_rop_rows.append({"sku": sku, "location": loc,
                             "safety_stock":  round(ss, 0),
                             "reorder_point": round(rop, 0)})

    ss_rop_df = pd.DataFrame(ss_rop_rows)
    weekly    = weekly.merge(ss_rop_df, on=["sku", "location"])

    # ── Simulated inventory position (centred around safety stock) ──
    ss_vals   = weekly["safety_stock"].clip(lower=1).values
    weekly["on_hand"]       = np.round(RNG.uniform(ss_vals * 0.8, ss_vals * 2.5), 0)
    safe_cost = weekly["unit_cost"].fillna(1.0).clip(lower=0.01, upper=500).values
    weekly["on_order"]      = np.round(RNG.uniform(0, safe_cost * 50), 0)
    weekly["stockout_flag"] = (weekly["on_hand"] < weekly["actual_demand"]).astype(int)

    return weekly


# ── Schema ──────────────────────────────────────────────────────────────────────
SCHEMA_COLS = [
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


# ── Main ────────────────────────────────────────────────────────────────────────
def main() -> None:
    print("=== M5 Walmart Grocery (FOODS_3) -> Portfolio Master Data ===\n")
    download_m5()

    cal, sales, prices = load_m5()
    weekly = filter_and_reshape(cal, sales, prices)
    weekly = add_forecast(weekly)
    weekly = derive_fields(weekly)

    cols = [c for c in SCHEMA_COLS if c in weekly.columns]
    out  = weekly[cols].sort_values(["sku", "location", "date"]).reset_index(drop=True)

    out.to_csv(OUT_CSV, index=False)

    print(f"\nSaved:      {OUT_CSV}")
    print(f"Rows:       {len(out):,}")
    print(f"SKUs:       {out['sku'].nunique()}")
    print(f"Locations:  {out['location'].nunique()}")
    print(f"Weeks:      {out['date'].nunique()}")
    print(f"Date range: {out['date'].min()} -> {out['date'].max()}")
    print()
    print("ABC/XYZ breakdown (SKU-location pairs):")
    print(
        out.drop_duplicates(["sku", "location"])
        .groupby(["abc_class", "xyz_class"])
        .size()
        .rename("count")
        .to_string()
    )
    print()
    print("WAPE by SKU sample (first 10):")
    wape_rows = []
    for (sku, loc), grp in list(out.groupby(["sku", "location"]))[:10]:
        act = grp["actual_demand"].values.astype(float)
        fct = grp["forecast"].values.astype(float)
        wape = np.abs(act - fct).sum() / (act.sum() + 1e-9) * 100
        wape_rows.append({"sku": sku, "location": loc, "WAPE_%": round(wape, 1)})
    print(pd.DataFrame(wape_rows).to_string(index=False))


if __name__ == "__main__":
    main()
