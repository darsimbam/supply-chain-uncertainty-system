"""
build_real_data.py
------------------
Downloads the UCI Online Retail II dataset and transforms it into the
master_data.csv schema used by all 6 portfolio notebooks.

Run from the repo root:
    python data/build_real_data.py

Outputs:
    data/raw/online_retail_II.xlsx        (raw download, cached)
    data/processed/master_data.csv        (ready for notebooks)
"""

import io
import zipfile
import requests
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import norm

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT      = Path(__file__).parent.parent
RAW_DIR   = ROOT / "data" / "raw"
PROC_DIR  = ROOT / "data" / "processed"
RAW_XLSX  = RAW_DIR  / "online_retail_II.xlsx"
OUT_CSV   = PROC_DIR / "master_data.csv"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROC_DIR.mkdir(parents=True, exist_ok=True)

# ── Parameters ─────────────────────────────────────────────────────────────────
DOWNLOAD_URL   = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
TOP_N_SKUS     = 50      # keep highest-volume SKUs
TOP_N_LOCS     = 4       # keep highest-volume countries
MIN_WEEKS      = 40      # drop SKU-location pairs with fewer weeks of data
HOLDING_RATE   = 0.20
MARGIN_RATE    = 0.30    # margin = price × MARGIN_RATE
EXPEDITE_MULT  = 1.50    # shortage cost = margin × EXPEDITE_MULT

# Lead-time assumptions by country (days)
LT_BY_COUNTRY = {
    "United Kingdom": {"mean": 7,  "std": 1},
    "Germany":        {"mean": 14, "std": 3},
    "France":         {"mean": 14, "std": 3},
    "Netherlands":    {"mean": 10, "std": 2},
    "default":        {"mean": 21, "std": 5},
}

# Service target by ABC class
SL_BY_ABC = {"A": 0.95, "B": 0.90, "C": 0.85}

RNG = np.random.default_rng(42)


# ── Step 1: Download ───────────────────────────────────────────────────────────
def download_raw() -> None:
    if RAW_XLSX.exists():
        print(f"Raw file already cached: {RAW_XLSX}")
        return
    print(f"Downloading UCI Online Retail II (~44 MB)...")
    resp = requests.get(DOWNLOAD_URL, timeout=120, stream=True)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    data  = b""
    for chunk in resp.iter_content(chunk_size=65536):
        data += chunk
        if total:
            pct = len(data) / total * 100
            print(f"  {pct:.0f}%", end="\r")
    print(f"  Downloaded {len(data)/1e6:.1f} MB")
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        xlsx_name = next(n for n in z.namelist() if n.endswith(".xlsx"))
        z.extract(xlsx_name, RAW_DIR)
        extracted = RAW_DIR / xlsx_name
        if extracted != RAW_XLSX:
            extracted.rename(RAW_XLSX)
    print(f"Saved: {RAW_XLSX}")


# ── Step 2: Load and clean raw data ───────────────────────────────────────────
def load_and_clean() -> pd.DataFrame:
    print("Loading Excel sheets (this takes ~30s)...")
    sheets = []
    for sheet in ["Year 2009-2010", "Year 2010-2011"]:
        try:
            s = pd.read_excel(RAW_XLSX, sheet_name=sheet, engine="openpyxl")
            sheets.append(s)
            print(f"  Loaded '{sheet}': {len(s):,} rows")
        except Exception as e:
            print(f"  Skipped '{sheet}': {e}")
    df = pd.concat(sheets, ignore_index=True)

    # Normalise column names
    df.columns = [c.strip() for c in df.columns]

    # Drop cancellations (InvoiceNo starts with C)
    df = df[~df["Invoice"].astype(str).str.startswith("C")]

    # Drop bad rows
    df = df.dropna(subset=["StockCode", "Quantity", "Price", "InvoiceDate", "Country"])
    df = df[df["Quantity"] > 0]
    df = df[df["Price"] > 0]

    # Remove non-product codes (postage, samples, bank charges, etc.)
    bad_codes = {"POST", "D", "M", "BANK CHARGES", "PADS", "DOT", "AMAZONFEE",
                 "S", "CRUK", "C2", "DCGS0076P", "gift_0001_40"}
    df = df[~df["StockCode"].astype(str).str.upper().isin(bad_codes)]
    df = df[df["StockCode"].astype(str).str.match(r"^\d{5}")]

    # Parse dates
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["InvoiceDate"])

    print(f"Clean rows: {len(df):,}")
    return df


# ── Step 3: Filter to top SKUs and locations ───────────────────────────────────
def filter_top(df: pd.DataFrame) -> pd.DataFrame:
    top_skus = (
        df.groupby("StockCode")["Quantity"].sum()
        .nlargest(TOP_N_SKUS).index.tolist()
    )
    top_locs = (
        df.groupby("Country")["Quantity"].sum()
        .nlargest(TOP_N_LOCS).index.tolist()
    )
    df = df[df["StockCode"].isin(top_skus) & df["Country"].isin(top_locs)]
    print(f"After filter: {len(df):,} rows | {df['StockCode'].nunique()} SKUs | {df['Country'].nunique()} countries")
    return df


# ── Step 4: Aggregate to weekly demand per SKU-location ───────────────────────
def aggregate_weekly(df: pd.DataFrame) -> pd.DataFrame:
    # Use Monday-anchored week start (floor to Monday)
    df["week"] = df["InvoiceDate"] - pd.to_timedelta(df["InvoiceDate"].dt.dayofweek, unit="D")
    df["week"] = df["week"].dt.normalize()

    agg = (
        df.groupby(["StockCode", "Country", "week"])
        .agg(
            actual_demand=("Quantity",  "sum"),
            avg_price    =("Price",     "mean"),
            n_invoices   =("Invoice",   "nunique"),
        )
        .reset_index()
    )

    # Build full date spine (Monday steps)
    all_weeks = pd.date_range(agg["week"].min(), agg["week"].max(), freq="7D")
    skus = agg["StockCode"].unique()
    locs = agg["Country"].unique()

    spine = pd.DataFrame(
        [(s, l, w) for s in skus for l in locs for w in all_weeks],
        columns=["StockCode", "Country", "week"],
    )

    weekly = spine.merge(agg, on=["StockCode", "Country", "week"], how="left")
    weekly["actual_demand"] = weekly["actual_demand"].fillna(0)
    weekly["n_invoices"]    = weekly["n_invoices"].fillna(0)

    # Forward-fill price per SKU (use global SKU mean as fallback)
    sku_mean_price = agg.groupby("StockCode")["avg_price"].mean()
    weekly["avg_price"] = (
        weekly.groupby("StockCode")["avg_price"]
        .transform(lambda s: s.ffill().bfill())
    )
    weekly["avg_price"] = weekly["avg_price"].fillna(
        weekly["StockCode"].map(sku_mean_price)
    )

    # Drop pairs with fewer than MIN_WEEKS of observed data
    obs_counts = (
        agg.groupby(["StockCode", "Country"])["actual_demand"]
        .count()
        .reset_index(name="obs")
    )
    weekly = weekly.merge(obs_counts, on=["StockCode", "Country"])
    weekly = weekly[weekly["obs"] >= MIN_WEEKS].drop(columns="obs")

    print(f"Weekly grid: {len(weekly):,} rows | {weekly['StockCode'].nunique()} SKUs | {weekly['Country'].nunique()} countries")
    return weekly


# ── Step 5: Derive forecast ────────────────────────────────────────────────────
def add_forecast(weekly: pd.DataFrame, alpha: float = 0.25) -> pd.DataFrame:
    """Exponential smoothing per SKU-location + systematic bias for realism."""
    forecasts = []
    for (sku, loc), grp in weekly.groupby(["StockCode", "Country"]):
        grp = grp.sort_values("week")
        d   = grp["actual_demand"].values.astype(float)
        f   = np.zeros_like(d)
        f[0] = d[0]
        for i in range(1, len(d)):
            f[i] = alpha * d[i-1] + (1 - alpha) * f[i-1]
        # Add realistic bias noise
        bias  = RNG.uniform(-0.08, 0.08)
        noise = RNG.normal(0, d.std() * 0.12, size=len(d))
        f     = np.clip(f * (1 + bias) + noise, 0, None).round(0)
        forecasts.append(pd.Series(f, index=grp.index))

    weekly["forecast"] = pd.concat(forecasts).sort_index()
    return weekly


# ── Step 6: Derive financial and policy fields ────────────────────────────────
def derive_fields(weekly: pd.DataFrame) -> pd.DataFrame:
    """ABC/XYZ, lead times, costs, SS, ROP, inventory position."""

    # ── ABC classification ─────────────────────────────────────
    sku_vol = (
        weekly.groupby("StockCode")["actual_demand"].sum()
        .sort_values(ascending=False)
    )
    cum_pct = sku_vol.cumsum() / sku_vol.sum()
    abc_map = {}
    for sku in sku_vol.index:
        p = cum_pct[sku]
        abc_map[sku] = "A" if p <= 0.80 else ("B" if p <= 0.95 else "C")

    # ── XYZ classification ─────────────────────────────────────
    sku_cv = weekly.groupby("StockCode")["actual_demand"].agg(
        lambda x: x.std() / x.mean() if x.mean() > 0 else 0
    )
    xyz_map = {}
    for sku, cv in sku_cv.items():
        xyz_map[sku] = "X" if cv <= 0.5 else ("Y" if cv <= 1.0 else "Z")

    weekly["abc_class"]     = weekly["StockCode"].map(abc_map)
    weekly["xyz_class"]     = weekly["StockCode"].map(xyz_map)
    weekly["cv"]            = weekly["StockCode"].map(sku_cv).round(3)
    weekly["product_family"]= "FAM_" + weekly["abc_class"]

    # ── Rename core fields ─────────────────────────────────────
    weekly = weekly.rename(columns={
        "StockCode": "sku",
        "Country":   "location",
        "week":      "date",
    })
    weekly["date"] = weekly["date"].dt.date

    # ── Financial fields ───────────────────────────────────────
    unit_price = (
        weekly.groupby("sku")["avg_price"].mean().rename("avg_price_sku")
    )
    weekly["unit_cost"]   = weekly["sku"].map(unit_price).round(2)
    weekly["unit_margin"] = (weekly["unit_cost"] * MARGIN_RATE).round(2)
    weekly["holding_cost_rate"]    = HOLDING_RATE
    weekly["shortage_cost_per_unit"]= (weekly["unit_margin"] * EXPEDITE_MULT).round(2)

    # ── Service target ─────────────────────────────────────────
    weekly["service_target"] = weekly["abc_class"].map(SL_BY_ABC)

    # ── Lead-time ──────────────────────────────────────────────
    def get_lt(loc, key):
        p = LT_BY_COUNTRY.get(loc, LT_BY_COUNTRY["default"])
        return p[key]

    weekly["lead_time_mean"] = weekly["location"].apply(lambda l: get_lt(l, "mean"))
    weekly["lead_time_std"]  = weekly["location"].apply(lambda l: get_lt(l, "std"))

    # ── Promo / holiday flags ──────────────────────────────────
    weekly["date_dt"]      = pd.to_datetime(weekly["date"])
    weekly["promo_flag"]   = (weekly["n_invoices"].fillna(0) > weekly.groupby("sku")["n_invoices"].transform("mean") * 1.5).astype(int)
    weekly["holiday_flag"] = ((weekly["date_dt"].dt.month == 12) & (weekly["date_dt"].dt.day >= 20)).astype(int)
    weekly = weekly.drop(columns=["date_dt"])

    # ── Safety stock and ROP (compute per SKU-location, merge back) ──
    ss_rop_rows = []
    for (sku, loc), grp in weekly.groupby(["sku", "location"]):
        d      = grp["actual_demand"].values
        avg_d  = d.mean()
        std_d  = d.std() if len(d) > 1 else 0
        sl     = grp["service_target"].iloc[0]
        lt     = grp["lead_time_mean"].iloc[0] / 7
        lt_std = grp["lead_time_std"].iloc[0]  / 7
        z      = norm.ppf(sl)
        ss     = max(z * np.sqrt(lt * std_d**2 + avg_d**2 * lt_std**2), 0)
        rop    = avg_d * lt + ss
        ss_rop_rows.append({"sku": sku, "location": loc,
                             "safety_stock": round(ss, 0),
                             "reorder_point": round(rop, 0)})

    ss_rop_df = pd.DataFrame(ss_rop_rows)
    weekly    = weekly.merge(ss_rop_df, on=["sku", "location"])

    # ── Inventory position (simulate around safety stock) ──────
    ss_vals   = weekly["safety_stock"].clip(lower=1).values
    weekly["on_hand"]      = np.round(RNG.uniform(ss_vals * 0.8, ss_vals * 2.5), 0)
    safe_cost = weekly["unit_cost"].fillna(1.0).clip(lower=0.01, upper=500).values
    weekly["on_order"]     = np.round(RNG.uniform(0, safe_cost * 50), 0)
    weekly["stockout_flag"]= (weekly["on_hand"] < weekly["actual_demand"]).astype(int)

    return weekly


# ── Step 7: Final schema alignment ────────────────────────────────────────────
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


def main():
    print("=== UCI Online Retail II -> Portfolio Master Data ===\n")
    download_raw()

    df      = load_and_clean()
    df      = filter_top(df)
    weekly  = aggregate_weekly(df)
    weekly  = add_forecast(weekly)
    weekly  = derive_fields(weekly)

    # Keep only schema columns that exist
    cols = [c for c in SCHEMA_COLS if c in weekly.columns]
    out  = weekly[cols].sort_values(["sku", "location", "date"]).reset_index(drop=True)

    out.to_csv(OUT_CSV, index=False)

    print(f"\nSaved: {OUT_CSV}")
    print(f"Rows:  {len(out):,}")
    print(f"SKUs:  {out['sku'].nunique()}")
    print(f"Locs:  {out['location'].nunique()}")
    print(f"Weeks: {out['date'].nunique()}")
    print(f"Date range: {out['date'].min()} to {out['date'].max()}")
    print()
    print("ABC/XYZ breakdown:")
    print(out.drop_duplicates(["sku","location"]).groupby(["abc_class","xyz_class"]).size().rename("sku_locs").to_string())


if __name__ == "__main__":
    main()
