"""
utils.py — Shared helper functions used across all projects.
"""

import pandas as pd
import numpy as np


def load_sample_data(path: str) -> pd.DataFrame:
    """Load a CSV or Excel file into a DataFrame."""
    if path.endswith(".xlsx"):
        return pd.read_excel(path)
    return pd.read_csv(path)


def abc_classify(df: pd.DataFrame, value_col: str, sku_col: str = "sku") -> pd.DataFrame:
    """
    Classify SKUs into ABC segments by cumulative value contribution.
    A = top 80%, B = next 15%, C = bottom 5%.
    """
    df = df.copy()
    df = df.sort_values(value_col, ascending=False)
    df["cumulative_pct"] = df[value_col].cumsum() / df[value_col].sum()
    df["abc_class"] = "C"
    df.loc[df["cumulative_pct"] <= 0.95, "abc_class"] = "B"
    df.loc[df["cumulative_pct"] <= 0.80, "abc_class"] = "A"
    return df


def xyz_classify(df: pd.DataFrame, cv_col: str) -> pd.DataFrame:
    """
    Classify SKUs by demand variability (coefficient of variation).
    X = CV <= 0.5, Y = 0.5 < CV <= 1.0, Z = CV > 1.0
    """
    df = df.copy()
    df["xyz_class"] = "Z"
    df.loc[df[cv_col] <= 1.0, "xyz_class"] = "Y"
    df.loc[df[cv_col] <= 0.5, "xyz_class"] = "X"
    return df
