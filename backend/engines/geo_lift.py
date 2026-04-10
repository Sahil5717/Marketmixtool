"""Geo-Lift / Incrementality Testing Framework (Phase 3)
Designs matched-market experiments to measure true causal impact of marketing spend."""
import numpy as np
import pandas as pd
from typing import Dict, List

def design_geo_test(df, channel, test_regions=None, control_regions=None, test_duration_weeks=8):
    """Design a geo-lift experiment: select test/control markets, estimate required sample size."""
    regions = df["region"].unique() if "region" in df.columns else df.get("reg", pd.Series([])).unique()
    if len(regions) < 2:
        return {"error": "Need at least 2 regions for geo-lift testing"}
    
    # Compute regional metrics for matching
    reg_data = df.groupby("region" if "region" in df.columns else "reg").agg(
        spend=("spend", "sum"), revenue=("revenue", "sum"),
        conversions=("conversions", "sum") if "conversions" in df.columns else ("conv", "sum"),
    ).reset_index()
    reg_col = "region" if "region" in reg_data.columns else "reg"
    reg_data["roi"] = (reg_data["revenue"] - reg_data["spend"]) / reg_data["spend"].clip(lower=1)
    reg_data["rev_per_period"] = reg_data["revenue"] / max(df["month" if "month" in df.columns else "date"].nunique(), 1)
    
    # Match regions by similarity (revenue volume)
    reg_data = reg_data.sort_values("revenue")
    n = len(reg_data)
    
    if test_regions is None:
        test_regions = [reg_data.iloc[n//2][reg_col]] if n > 2 else [reg_data.iloc[0][reg_col]]
    if control_regions is None:
        control_regions = [r for r in reg_data[reg_col].values if r not in test_regions][:len(test_regions)]
    
    # Calculate expected lift and required sample size
    ch_data = df[df["channel" if "channel" in df.columns else "ch"] == channel]
    ch_spend = ch_data["spend"].sum()
    ch_rev = ch_data["revenue"].sum()
    expected_lift_pct = min(30, max(5, (ch_rev / max(ch_spend, 1) - 1) * 10))
    
    test_rev = reg_data[reg_data[reg_col].isin(test_regions)]["rev_per_period"].sum()
    # MDE (minimum detectable effect) power calculation approximation
    baseline_weekly = test_rev / 4  # monthly to weekly
    mde = expected_lift_pct / 100
    z_alpha = 1.96; z_beta = 0.84  # 80% power, 95% confidence
    variance = baseline_weekly * 0.15  # assume 15% CV
    sample_weeks = max(4, int(np.ceil(2 * (z_alpha + z_beta)**2 * variance**2 / (baseline_weekly * mde)**2)))
    
    return {
        "channel": channel,
        "test_regions": test_regions, "control_regions": control_regions,
        "test_duration_weeks": max(test_duration_weeks, sample_weeks),
        "expected_lift_pct": round(expected_lift_pct, 1),
        "minimum_detectable_effect": round(mde * 100, 1),
        "statistical_power": 0.80, "confidence_level": 0.95,
        "estimated_test_cost": round(ch_spend / len(regions) * len(test_regions) / 12 * test_duration_weeks / 4, 0),
        "regional_metrics": reg_data.to_dict(orient="records"),
        "recommendation": f"Run {test_duration_weeks}-week holdout test in {', '.join(test_regions)} vs {', '.join(control_regions)}. "
                         f"Expected to detect {expected_lift_pct:.0f}% lift with 80% power.",
    }

def analyze_geo_results(test_revenue, control_revenue, pre_test_ratio=1.0):
    """Analyze results of a completed geo-lift test."""
    expected_control = control_revenue * pre_test_ratio
    incremental = test_revenue - expected_control
    lift_pct = (incremental / expected_control * 100) if expected_control > 0 else 0
    # Simple significance test
    se = np.sqrt(test_revenue + control_revenue) * 0.1
    z_stat = incremental / max(se, 1)
    p_value = 2 * (1 - min(0.9999, 0.5 + 0.5 * np.tanh(z_stat / 1.4)))
    
    return {
        "test_revenue": round(test_revenue, 0), "control_revenue": round(control_revenue, 0),
        "incremental_revenue": round(incremental, 0), "lift_pct": round(lift_pct, 1),
        "z_statistic": round(z_stat, 2), "p_value": round(p_value, 4),
        "significant": p_value < 0.05,
        "confidence": "High" if p_value < 0.01 else "Medium" if p_value < 0.05 else "Low",
    }

def design_all_tests(df, curves, top_n=5):
    """Design incrementality tests for top channels by spend."""
    ch_spend = df.groupby("channel" if "channel" in df.columns else "ch")["spend"].sum().sort_values(ascending=False)
    tests = []
    for ch in ch_spend.head(top_n).index:
        test = design_geo_test(df, ch)
        if "error" not in test:
            tests.append(test)
    return {"tests": tests, "n_channels_testable": len(tests)}

