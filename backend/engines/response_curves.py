"""
Response Curve Engine
Fits diminishing returns curves to historical spend-vs-outcome data.
Phase 1: Power-law curves (y = a * x^b)
Phase 2: Hill curves (y = a * x^b / (K^b + x^b))

These curves are the foundation for the optimizer - they tell us the
marginal return of the next dollar in each channel.
"""

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit, minimize_scalar
from typing import Dict, Tuple, List


def power_law(x: np.ndarray, a: float, b: float) -> np.ndarray:
    """Power-law: y = a * x^b where 0 < b < 1 gives diminishing returns."""
    return a * np.power(np.maximum(x, 1e-6), b)


def hill_curve(x: np.ndarray, a: float, b: float, K: float) -> np.ndarray:
    """Hill/logistic saturation: y = a * x^b / (K^b + x^b)"""
    xb = np.power(np.maximum(x, 1e-6), b)
    Kb = np.power(K, b)
    return a * xb / (Kb + xb)


def marginal_return_power_law(x: float, a: float, b: float) -> float:
    """Derivative of power-law: dy/dx = a * b * x^(b-1)"""
    if x <= 0:
        return float("inf")
    return a * b * np.power(x, b - 1)


def marginal_return_hill(x: float, a: float, b: float, K: float) -> float:
    """Derivative of Hill curve."""
    if x <= 0:
        return float("inf")
    Kb = K ** b
    xb = x ** b
    return a * b * (x ** (b - 1)) * Kb / ((Kb + xb) ** 2)


def fit_response_curves(
    campaign_df: pd.DataFrame,
    model_type: str = "power_law"
) -> Dict[str, Dict]:
    """
    Fit response curves for each channel using monthly spend vs. revenue data.
    Returns fitted parameters and diagnostics per channel.
    """
    results = {}
    
    for channel in campaign_df["channel"].unique():
        ch_data = campaign_df[campaign_df["channel"] == channel]
        
        # Aggregate monthly spend and revenue across campaigns/regions
        monthly = ch_data.groupby("month").agg(
            spend=("spend", "sum"),
            revenue=("revenue", "sum"),
            conversions=("conversions", "sum"),
        ).reset_index().sort_values("month")
        
        x = monthly["spend"].values
        y = monthly["revenue"].values
        
        if len(x) < 3 or x.sum() == 0:
            continue
        
        try:
            if model_type == "power_law":
                # Fit y = a * x^b
                popt, pcov = curve_fit(
                    power_law, x, y,
                    p0=[1.0, 0.5],
                    bounds=([0, 0.01], [np.inf, 0.99]),
                    maxfev=5000
                )
                a, b = popt
                y_pred = power_law(x, a, b)
                
                # Calculate saturation point (where marginal ROI = 1)
                # dy/dx = 1 → a * b * x^(b-1) = 1 → x = (a*b)^(1/(1-b))
                if b < 1:
                    saturation_spend = np.power(a * b, 1 / (1 - b))
                else:
                    saturation_spend = x.max() * 2
                
                # Current marginal ROI
                current_spend = x.mean()
                current_marginal_roi = marginal_return_power_law(current_spend, a, b)
                
                results[channel] = {
                    "model": "power_law",
                    "params": {"a": float(a), "b": float(b)},
                    "saturation_spend": float(saturation_spend),
                    "current_avg_spend": float(current_spend),
                    "current_marginal_roi": float(current_marginal_roi),
                    "headroom_pct": float(max(0, (saturation_spend - current_spend) / saturation_spend * 100)),
                    "r_squared": float(_r_squared(y, y_pred)),
                    "monthly_data": {"spend": x.tolist(), "revenue": y.tolist()},
                    "curve_points": _generate_curve_points(a, b, x, "power_law"),
                }
            
            elif model_type == "hill":
                # Fit Hill curve
                K_init = np.median(x)
                popt, pcov = curve_fit(
                    hill_curve, x, y,
                    p0=[y.max() * 2, 0.7, K_init],
                    bounds=([0, 0.1, 1], [y.max() * 10, 3.0, x.max() * 5]),
                    maxfev=10000
                )
                a, b, K = popt
                y_pred = hill_curve(x, a, b, K)
                
                current_spend = x.mean()
                current_marginal_roi = marginal_return_hill(current_spend, a, b, K)
                
                # Saturation is at inflection point of Hill curve
                saturation_spend = K * ((b - 1) / (b + 1)) ** (1 / b) if b > 1 else K
                
                results[channel] = {
                    "model": "hill",
                    "params": {"a": float(a), "b": float(b), "K": float(K)},
                    "saturation_spend": float(saturation_spend),
                    "current_avg_spend": float(current_spend),
                    "current_marginal_roi": float(current_marginal_roi),
                    "headroom_pct": float(max(0, (saturation_spend - current_spend) / saturation_spend * 100)),
                    "r_squared": float(_r_squared(y, y_pred)),
                    "monthly_data": {"spend": x.tolist(), "revenue": y.tolist()},
                    "curve_points": _generate_curve_points(a, b, x, "hill", K),
                }
        
        except (RuntimeError, ValueError) as e:
            # Fallback to simple linear if curve fitting fails
            slope = np.polyfit(x, y, 1)[0]
            results[channel] = {
                "model": "linear_fallback",
                "params": {"slope": float(slope)},
                "saturation_spend": float(x.max() * 3),
                "current_avg_spend": float(x.mean()),
                "current_marginal_roi": float(slope),
                "headroom_pct": 100.0,
                "r_squared": float(np.corrcoef(x, y)[0, 1] ** 2) if len(x) > 1 else 0,
                "monthly_data": {"spend": x.tolist(), "revenue": y.tolist()},
                "curve_points": {"spend": [0, float(x.max() * 1.5)], "revenue": [0, float(slope * x.max() * 1.5)]},
                "fit_error": str(e),
            }
    
    return results


def _r_squared(y_actual: np.ndarray, y_predicted: np.ndarray) -> float:
    ss_res = np.sum((y_actual - y_predicted) ** 2)
    ss_tot = np.sum((y_actual - np.mean(y_actual)) ** 2)
    if ss_tot == 0:
        return 0
    return 1 - ss_res / ss_tot


def _generate_curve_points(
    a: float, b: float, x_data: np.ndarray,
    model_type: str, K: float = None,
    n_points: int = 50
) -> Dict:
    """Generate smooth curve points for visualization."""
    x_range = np.linspace(0, x_data.max() * 1.5, n_points)
    
    if model_type == "power_law":
        y_range = power_law(x_range, a, b)
    elif model_type == "hill":
        y_range = hill_curve(x_range, a, b, K)
    else:
        y_range = a * x_range
    
    return {
        "spend": x_range.tolist(),
        "revenue": y_range.tolist(),
    }


def get_marginal_roi_table(
    curves: Dict[str, Dict],
    spend_levels: List[float] = None
) -> pd.DataFrame:
    """
    Generate a table showing marginal ROI at various spend levels for each channel.
    This is the key input for the optimizer.
    """
    if spend_levels is None:
        spend_levels = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]  # multipliers of current spend
    
    rows = []
    for channel, curve in curves.items():
        current = curve["current_avg_spend"]
        
        for mult in spend_levels:
            spend = current * mult
            
            if curve["model"] == "power_law":
                a, b = curve["params"]["a"], curve["params"]["b"]
                total_return = power_law(np.array([spend]), a, b)[0]
                marginal = marginal_return_power_law(spend, a, b)
            elif curve["model"] == "hill":
                a, b, K = curve["params"]["a"], curve["params"]["b"], curve["params"]["K"]
                total_return = hill_curve(np.array([spend]), a, b, K)[0]
                marginal = marginal_return_hill(spend, a, b, K)
            else:
                slope = curve["params"]["slope"]
                total_return = slope * spend
                marginal = slope
            
            rows.append({
                "channel": channel,
                "spend_multiplier": mult,
                "monthly_spend": spend,
                "expected_revenue": total_return,
                "marginal_roi": marginal,
                "avg_roi": total_return / spend if spend > 0 else 0,
            })
    
    return pd.DataFrame(rows)


if __name__ == "__main__":
    from mock_data import generate_all_data
    
    data = generate_all_data()
    campaigns = data["campaign_performance"]
    
    print("\n=== Fitting Power-Law Response Curves ===")
    curves = fit_response_curves(campaigns, model_type="power_law")
    
    for channel, info in curves.items():
        print(f"\n{channel}:")
        print(f"  Model: y = {info['params']['a']:.2f} * x^{info['params']['b']:.3f}")
        print(f"  R²: {info['r_squared']:.3f}")
        print(f"  Current avg spend: ${info['current_avg_spend']:,.0f}")
        print(f"  Saturation spend: ${info['saturation_spend']:,.0f}")
        print(f"  Headroom: {info['headroom_pct']:.1f}%")
        print(f"  Current marginal ROI: {info['current_marginal_roi']:.2f}")
    
    print("\n=== Marginal ROI Table ===")
    table = get_marginal_roi_table(curves)
    print(table.to_string(index=False))
