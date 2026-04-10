"""Hierarchical Forecasting (Phase 3) - Region × Channel × Campaign level prediction."""
import numpy as np
import pandas as pd
from typing import Dict

def hierarchical_forecast(df, periods=12, levels=None):
    """Forecast at multiple hierarchy levels with reconciliation."""
    if levels is None:
        levels = ["total", "channel", "region", "channel_region"]
    
    time_col = "month" if "month" in df.columns else "date"
    ch_col = "channel" if "channel" in df.columns else "ch"
    reg_col = "region" if "region" in df.columns else "reg"
    
    results = {}
    
    # Level 1: Total
    if "total" in levels:
        monthly = df.groupby(time_col)["revenue" if "revenue" in df.columns else "rev"].sum().values
        results["total"] = _simple_forecast(monthly, periods, "Total")
    
    # Level 2: By channel
    if "channel" in levels:
        results["by_channel"] = {}
        for ch in df[ch_col].unique():
            ch_data = df[df[ch_col] == ch].groupby(time_col)["revenue" if "revenue" in df.columns else "rev"].sum().values
            if len(ch_data) >= 3:
                results["by_channel"][ch] = _simple_forecast(ch_data, periods, ch)
    
    # Level 3: By region
    if "region" in levels:
        results["by_region"] = {}
        for reg in df[reg_col].unique():
            reg_data = df[df[reg_col] == reg].groupby(time_col)["revenue" if "revenue" in df.columns else "rev"].sum().values
            if len(reg_data) >= 3:
                results["by_region"][reg] = _simple_forecast(reg_data, periods, reg)
    
    # Level 4: Channel × Region
    if "channel_region" in levels:
        results["by_channel_region"] = {}
        for ch in df[ch_col].unique():
            for reg in df[reg_col].unique():
                cr_data = df[(df[ch_col]==ch)&(df[reg_col]==reg)].groupby(time_col)["revenue" if "revenue" in df.columns else "rev"].sum().values
                if len(cr_data) >= 3:
                    results["by_channel_region"][f"{ch}|{reg}"] = _simple_forecast(cr_data, periods, f"{ch}|{reg}")
    
    # Reconciliation: ensure channel forecasts sum to total
    if "total" in results and "by_channel" in results:
        total_fc = results["total"]["forecast_total"]
        channel_sum = sum(r["forecast_total"] for r in results["by_channel"].values())
        if channel_sum > 0:
            scale = total_fc / channel_sum
            for ch in results["by_channel"]:
                results["by_channel"][ch]["forecast_total"] = round(results["by_channel"][ch]["forecast_total"] * scale, 0)
                results["by_channel"][ch]["reconciliation_factor"] = round(scale, 3)
    
    return results

def _simple_forecast(values, periods, label):
    """Trend + seasonality forecast for a single series."""
    n = len(values)
    x = np.arange(n)
    # Linear trend
    if n >= 2:
        slope, intercept = np.polyfit(x, values, 1)
    else:
        slope, intercept = 0, values[0] if len(values) > 0 else 0
    
    # Seasonal factors
    fitted = slope * x + intercept
    seasonal = values / np.maximum(fitted, 1)
    
    # Forecast
    forecast = []
    for i in range(periods):
        trend_val = slope * (n + i) + intercept
        sf = seasonal[i % n] if i < n else seasonal[i % min(n, 12)]
        pred = max(0, trend_val * sf)
        forecast.append(round(pred, 0))
    
    return {
        "label": label,
        "historical": values.tolist(),
        "forecast": forecast,
        "forecast_total": round(sum(forecast), 0),
        "historical_total": round(float(values.sum()), 0),
        "yoy_pct": round((sum(forecast) - values.sum()) / max(values.sum(), 1) * 100, 1),
        "trend_slope": round(float(slope), 2),
    }

