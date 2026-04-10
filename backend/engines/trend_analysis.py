"""
Trend & Variance Analysis Engine (Phase 1)
- Period-over-period comparison (MoM, QoQ, YoY)
- Moving averages (3-month, 6-month)
- Anomaly detection (z-score based)
- Variance decomposition by channel/campaign
- Statistical significance flags
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple


def period_over_period(
    df: pd.DataFrame,
    metric: str = "revenue",
    period: str = "month",
) -> pd.DataFrame:
    """
    Calculate period-over-period change for a given metric.
    Returns: DataFrame with current, prior, absolute change, % change, direction.
    """
    if period == "month":
        grouped = df.groupby("month").agg(**{metric: (metric, "sum")}).reset_index()
        grouped = grouped.sort_values("month")
    elif period == "quarter":
        df = df.copy()
        df["quarter"] = df["month"].apply(lambda x: f"Q{(int(x.split('-')[1])-1)//3+1}")
        grouped = df.groupby("quarter").agg(**{metric: (metric, "sum")}).reset_index()
    else:
        grouped = df.groupby("month").agg(**{metric: (metric, "sum")}).reset_index().sort_values("month")

    grouped["prior"] = grouped[metric].shift(1)
    grouped["change"] = grouped[metric] - grouped["prior"]
    grouped["change_pct"] = grouped["change"] / grouped["prior"].clip(lower=1) * 100
    grouped["direction"] = grouped["change"].apply(
        lambda x: "up" if x > 0 else ("down" if x < 0 else "flat")
    )
    # 3-period moving average
    grouped["ma3"] = grouped[metric].rolling(window=3, min_periods=1).mean()

    return grouped


def channel_variance_decomposition(
    df: pd.DataFrame,
    metric: str = "revenue",
) -> pd.DataFrame:
    """
    Decompose total variance by channel.
    Shows which channels are driving overall performance changes.
    """
    # Split into first half vs second half
    months = sorted(df["month"].unique())
    mid = len(months) // 2
    h1_months = months[:mid]
    h2_months = months[mid:]

    h1 = df[df["month"].isin(h1_months)]
    h2 = df[df["month"].isin(h2_months)]

    h1_ch = h1.groupby("channel").agg(**{metric: (metric, "sum")}).reset_index()
    h2_ch = h2.groupby("channel").agg(**{metric: (metric, "sum")}).reset_index()

    merged = h1_ch.merge(h2_ch, on="channel", suffixes=("_h1", "_h2"), how="outer").fillna(0)
    merged["change"] = merged[f"{metric}_h2"] - merged[f"{metric}_h1"]
    merged["change_pct"] = merged["change"] / merged[f"{metric}_h1"].clip(lower=1) * 100

    total_change = merged["change"].sum()
    merged["contribution_pct"] = merged["change"] / total_change * 100 if total_change != 0 else 0

    return merged.sort_values("change", ascending=False)


def detect_anomalies(
    df: pd.DataFrame,
    metric: str = "revenue",
    z_threshold: float = 2.0,
) -> List[Dict]:
    """
    Detect anomalous periods using z-score method.
    Returns list of anomalies with period, value, z-score, and direction.
    """
    grouped = df.groupby("month").agg(**{metric: (metric, "sum")}).reset_index().sort_values("month")
    
    values = grouped[metric].values
    mean = np.mean(values)
    std = np.std(values)
    
    if std == 0:
        return []
    
    anomalies = []
    for _, row in grouped.iterrows():
        z = (row[metric] - mean) / std
        if abs(z) > z_threshold:
            anomalies.append({
                "period": row["month"],
                "value": round(row[metric], 2),
                "mean": round(mean, 2),
                "z_score": round(z, 2),
                "direction": "spike" if z > 0 else "dip",
                "severity": "high" if abs(z) > 3 else "medium",
                "deviation_pct": round((row[metric] - mean) / mean * 100, 1),
            })
    
    return anomalies


def channel_anomalies(
    df: pd.DataFrame,
    metric: str = "revenue",
    z_threshold: float = 1.8,
) -> List[Dict]:
    """Detect anomalies at the channel-month level."""
    anomalies = []
    
    for channel in df["channel"].unique():
        ch_data = df[df["channel"] == channel]
        monthly = ch_data.groupby("month").agg(**{metric: (metric, "sum")}).reset_index()
        values = monthly[metric].values
        
        if len(values) < 3:
            continue
            
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:
            continue
        
        for _, row in monthly.iterrows():
            z = (row[metric] - mean) / std
            if abs(z) > z_threshold:
                anomalies.append({
                    "channel": channel,
                    "period": row["month"],
                    "value": round(row[metric], 2),
                    "mean": round(mean, 2),
                    "z_score": round(z, 2),
                    "direction": "spike" if z > 0 else "dip",
                })
    
    return sorted(anomalies, key=lambda x: abs(x["z_score"]), reverse=True)


def compute_moving_averages(
    df: pd.DataFrame,
    metric: str = "revenue",
    windows: List[int] = [3, 6],
) -> pd.DataFrame:
    """Compute moving averages at specified windows."""
    monthly = df.groupby("month").agg(**{metric: (metric, "sum")}).reset_index().sort_values("month")
    
    for w in windows:
        monthly[f"ma_{w}"] = monthly[metric].rolling(window=w, min_periods=1).mean()
    
    # Trend direction based on 3-month MA slope
    ma3 = monthly[f"ma_{windows[0]}"].values
    if len(ma3) >= 3:
        recent_slope = (ma3[-1] - ma3[-3]) / 2
        monthly["trend_direction"] = "up" if recent_slope > 0 else "down"
        monthly["trend_strength"] = abs(recent_slope) / np.mean(ma3) * 100
    
    return monthly


def roi_variance_analysis(df: pd.DataFrame) -> Dict:
    """
    Analyze ROI variance across channels and time.
    Identifies most/least consistent performers.
    """
    channel_monthly = df.groupby(["channel", "month"]).agg(
        spend=("spend", "sum"),
        revenue=("revenue", "sum"),
    ).reset_index()
    
    channel_monthly["roi"] = (channel_monthly["revenue"] - channel_monthly["spend"]) / channel_monthly["spend"]
    
    results = {}
    for channel in channel_monthly["channel"].unique():
        ch_rois = channel_monthly[channel_monthly["channel"] == channel]["roi"].values
        results[channel] = {
            "mean_roi": float(np.mean(ch_rois)),
            "std_roi": float(np.std(ch_rois)),
            "cv": float(np.std(ch_rois) / np.mean(ch_rois)) if np.mean(ch_rois) != 0 else 0,
            "min_roi": float(np.min(ch_rois)),
            "max_roi": float(np.max(ch_rois)),
            "consistency": "high" if np.std(ch_rois) / max(np.mean(ch_rois), 0.01) < 0.15 else (
                "medium" if np.std(ch_rois) / max(np.mean(ch_rois), 0.01) < 0.3 else "low"
            ),
        }
    
    return results


def run_full_trend_analysis(df: pd.DataFrame) -> Dict:
    """Run all trend & variance analyses and return combined results."""
    return {
        "revenue_trend": period_over_period(df, "revenue").to_dict(orient="records"),
        "spend_trend": period_over_period(df, "spend").to_dict(orient="records"),
        "conversion_trend": period_over_period(df, "conversions").to_dict(orient="records"),
        "revenue_anomalies": detect_anomalies(df, "revenue"),
        "spend_anomalies": detect_anomalies(df, "spend"),
        "channel_anomalies": channel_anomalies(df, "revenue"),
        "variance_decomposition": channel_variance_decomposition(df, "revenue").to_dict(orient="records"),
        "roi_variance": roi_variance_analysis(df),
        "moving_averages": compute_moving_averages(df, "revenue").to_dict(orient="records"),
    }


if __name__ == "__main__":
    from mock_data import generate_all_data
    
    data = generate_all_data()
    df = data["campaign_performance"]
    
    results = run_full_trend_analysis(df)
    
    print("=== Period-over-Period Revenue ===")
    for r in results["revenue_trend"]:
        if r.get("prior"):
            print(f"  {r['month']}: ${r['revenue']:,.0f} ({r['change_pct']:+.1f}%) MA3: ${r['ma3']:,.0f}")
    
    print(f"\n=== Anomalies ({len(results['revenue_anomalies'])}) ===")
    for a in results["revenue_anomalies"]:
        print(f"  {a['period']}: {a['direction']} z={a['z_score']:.1f} ({a['deviation_pct']:+.1f}%)")
    
    print(f"\n=== Channel Anomalies ({len(results['channel_anomalies'])}) ===")
    for a in results["channel_anomalies"][:5]:
        print(f"  {a['channel']} {a['period']}: {a['direction']} z={a['z_score']:.1f}")
    
    print("\n=== ROI Consistency ===")
    for ch, info in results["roi_variance"].items():
        print(f"  {ch}: mean={info['mean_roi']:.2f}x CV={info['cv']:.2f} [{info['consistency']}]")
    
    print("\n=== Variance Decomposition ===")
    for r in results["variance_decomposition"]:
        print(f"  {r['channel']}: {r['change']:+,.0f} ({r['contribution_pct']:+.1f}% of total change)")
