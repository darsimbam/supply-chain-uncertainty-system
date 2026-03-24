"""
forecasting.py — Baseline forecasting models and error diagnostics.
"""

import numpy as np
import pandas as pd


# --- Error metrics ---

def rmse(actual: np.ndarray, forecast: np.ndarray) -> float:
    return np.sqrt(np.mean((actual - forecast) ** 2))


def mae(actual: np.ndarray, forecast: np.ndarray) -> float:
    return np.mean(np.abs(actual - forecast))


def bias(actual: np.ndarray, forecast: np.ndarray) -> float:
    """Mean forecast error. Positive = under-forecast, negative = over-forecast."""
    return np.mean(actual - forecast)


def wape(actual: np.ndarray, forecast: np.ndarray) -> float:
    """Weighted Absolute Percentage Error."""
    return np.sum(np.abs(actual - forecast)) / np.sum(actual)


def mape(actual: np.ndarray, forecast: np.ndarray) -> float:
    mask = actual != 0
    return np.mean(np.abs((actual[mask] - forecast[mask]) / actual[mask]))


def error_summary(actual: np.ndarray, forecast: np.ndarray) -> dict:
    return {
        "RMSE": rmse(actual, forecast),
        "MAE": mae(actual, forecast),
        "Bias": bias(actual, forecast),
        "WAPE": wape(actual, forecast),
        "MAPE": mape(actual, forecast),
    }


# --- Baseline forecast models ---

def naive_forecast(series: pd.Series) -> pd.Series:
    """Forecast = last observed value (lag-1)."""
    return series.shift(1)


def moving_average(series: pd.Series, window: int = 4) -> pd.Series:
    return series.rolling(window=window).mean()


def exponential_smoothing(series: pd.Series, alpha: float = 0.3) -> pd.Series:
    result = [series.iloc[0]]
    for val in series.iloc[1:]:
        result.append(alpha * val + (1 - alpha) * result[-1])
    return pd.Series(result, index=series.index)
