"""
Adstock & Carryover Models (Phase 2)
Models the lagged effect of media spend — today's ad exposure affects
conversions for days/weeks after the exposure.

Two adstock functions:
1. Geometric: simple exponential decay (1 parameter: decay rate)
2. Weibull: flexible shape allowing delayed peak (2 parameters: shape, scale)

Plus saturation transform (Hill function) applied after adstock.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Dict, List, Tuple, Optional


def geometric_adstock(x: np.ndarray, decay: float = 0.5, max_lag: int = 8) -> np.ndarray:
    """
    Geometric adstock: each period carries over a fraction (decay) to next.
    adstock[t] = x[t] + decay * adstock[t-1]
    
    Args:
        x: spend or impression series (daily/weekly)
        decay: carryover rate (0 = no carryover, 1 = full carryover)
        max_lag: maximum number of periods to carry over
    """
    adstocked = np.zeros_like(x, dtype=float)
    adstocked[0] = x[0]
    
    for t in range(1, len(x)):
        adstocked[t] = x[t] + decay * adstocked[t - 1]
    
    return adstocked


def weibull_adstock(x: np.ndarray, shape: float = 2.0, scale: float = 1.0, max_lag: int = 12) -> np.ndarray:
    """
    Weibull adstock: allows delayed peak effect.
    Useful for channels like TV where effect builds then decays.
    
    Args:
        x: spend series
        shape: Weibull shape (>1 = delayed peak, =1 = exponential, <1 = fast decay)
        scale: Weibull scale (higher = longer effect)
    """
    # Build Weibull kernel
    lags = np.arange(max_lag) + 1e-10  # Avoid divide by zero at lag=0
    kernel = (shape / scale) * (lags / scale) ** (shape - 1) * np.exp(-(lags / scale) ** shape)
    kernel = np.nan_to_num(kernel, nan=0.0, posinf=0.0, neginf=0.0)
    kernel_sum = kernel.sum()
    kernel = kernel / kernel_sum if kernel_sum > 0 else np.ones(max_lag) / max_lag
    
    # Convolve
    adstocked = np.convolve(x, kernel, mode='full')[:len(x)]
    
    return adstocked


def hill_saturation(x: np.ndarray, half_saturation: float, slope: float = 1.0) -> np.ndarray:
    """
    Hill function saturation transform.
    y = x^slope / (half_saturation^slope + x^slope)
    
    Returns values in [0, 1] — multiply by max_effect to get actual contribution.
    """
    x_safe = np.maximum(x, 1e-10)
    return x_safe ** slope / (half_saturation ** slope + x_safe ** slope)


def adstock_transform(
    spend_series: np.ndarray,
    adstock_type: str = "geometric",
    decay: float = 0.5,
    shape: float = 2.0,
    scale: float = 1.0,
    max_lag: int = 8,
    apply_saturation: bool = True,
    half_saturation: Optional[float] = None,
    saturation_slope: float = 1.0,
) -> np.ndarray:
    """
    Full adstock + saturation pipeline.
    1. Apply adstock (geometric or weibull)
    2. Apply Hill saturation (optional)
    """
    # Step 1: Adstock
    if adstock_type == "geometric":
        adstocked = geometric_adstock(spend_series, decay, max_lag)
    elif adstock_type == "weibull":
        adstocked = weibull_adstock(spend_series, shape, scale, max_lag)
    else:
        adstocked = spend_series.copy()
    
    # Step 2: Saturation
    if apply_saturation and half_saturation:
        saturated = hill_saturation(adstocked, half_saturation, saturation_slope)
    else:
        saturated = adstocked
    
    return saturated


def fit_adstock_params(
    spend: np.ndarray,
    response: np.ndarray,
    adstock_type: str = "geometric",
) -> Dict:
    """
    Fit optimal adstock parameters by maximizing correlation
    between adstocked spend and response.
    """
    best_params = None
    best_corr = -1
    
    if adstock_type == "geometric":
        for decay in np.arange(0.1, 0.95, 0.05):
            adstocked = geometric_adstock(spend, decay)
            corr = np.corrcoef(adstocked, response)[0, 1]
            if corr > best_corr:
                best_corr = corr
                best_params = {"decay": round(float(decay), 2)}
    
    elif adstock_type == "weibull":
        for shape in np.arange(0.5, 4.0, 0.5):
            for scale in np.arange(0.5, 5.0, 0.5):
                adstocked = weibull_adstock(spend, shape, scale)
                corr = np.corrcoef(adstocked, response)[0, 1]
                if corr > best_corr:
                    best_corr = corr
                    best_params = {"shape": round(float(shape), 1), "scale": round(float(scale), 1)}
    
    return {
        "adstock_type": adstock_type,
        "params": best_params or {},
        "correlation": round(float(best_corr), 4),
    }


def compute_channel_adstock(
    df: pd.DataFrame,
    adstock_type: str = "geometric",
) -> Dict[str, Dict]:
    """
    Fit adstock parameters for each channel and return
    adstocked spend series + optimal parameters.
    """
    results = {}
    
    for channel in df["channel"].unique():
        ch_data = df[df["channel"] == channel].sort_values("month" if "month" in df.columns else "date")
        
        monthly = ch_data.groupby(ch_data.columns[ch_data.columns.str.contains("month|date")][0]).agg(
            spend=("spend", "sum"),
            revenue=("revenue", "sum"),
        ).reset_index()
        
        if len(monthly) < 4:
            continue
        
        spend = monthly["spend"].values
        revenue = monthly["revenue"].values
        
        # Fit adstock
        fit = fit_adstock_params(spend, revenue, adstock_type)
        
        # Apply with fitted params
        if adstock_type == "geometric":
            adstocked = geometric_adstock(spend, fit["params"].get("decay", 0.5))
        else:
            adstocked = weibull_adstock(
                spend,
                fit["params"].get("shape", 2.0),
                fit["params"].get("scale", 1.0)
            )
        
        # Fit half-saturation for Hill curve
        median_adstocked = float(np.median(adstocked))
        
        results[channel] = {
            **fit,
            "original_spend": spend.tolist(),
            "adstocked_spend": adstocked.tolist(),
            "revenue": revenue.tolist(),
            "half_saturation": round(median_adstocked, 0),
            "carryover_effect_pct": round(float((adstocked.sum() - spend.sum()) / spend.sum() * 100), 1),
        }
    
    return results


if __name__ == "__main__":
    from mock_data import generate_all_data
    
    data = generate_all_data()
    df = data["campaign_performance"]
    
    print("=== Geometric Adstock ===")
    results = compute_channel_adstock(df, "geometric")
    for ch, info in results.items():
        print(f"  {ch}: decay={info['params'].get('decay', '?')} "
              f"corr={info['correlation']:.3f} "
              f"carryover={info['carryover_effect_pct']:+.1f}%")
    
    print("\n=== Weibull Adstock ===")
    results_w = compute_channel_adstock(df, "weibull")
    for ch, info in results_w.items():
        print(f"  {ch}: shape={info['params'].get('shape', '?')} "
              f"scale={info['params'].get('scale', '?')} "
              f"corr={info['correlation']:.3f}")
