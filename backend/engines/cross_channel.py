"""
Cross-Channel Leakage Engine (Phase 2)
Analyzes revenue leaking between online and offline channels:
- Timing leakage: seasonal spend vs conversion pattern mismatch
- Audience leakage: high-converting segments getting low spend
- Online→Offline leakage: digital demand not captured in stores/dealers
- Offline→Online leakage: offline campaigns not converting digitally
"""

import numpy as np
import pandas as pd
from typing import Dict, List


def timing_leakage(df: pd.DataFrame) -> Dict:
    """
    Compare seasonal spend patterns vs seasonal conversion patterns.
    Leakage occurs when spend peaks don't align with conversion peaks.
    """
    monthly = df.groupby("month" if "month" in df.columns else "date").agg(
        spend=("spend", "sum"),
        revenue=("revenue", "sum"),
        conversions=("conversions", "sum") if "conversions" in df.columns else ("conv", "sum"),
    ).reset_index().sort_values("month" if "month" in df.columns else "date")
    
    # Normalize to shares
    spend_share = monthly["spend"] / monthly["spend"].sum()
    rev_share = monthly["revenue"] / monthly["revenue"].sum()
    
    # Misalignment = absolute difference in shares
    monthly["spend_share"] = spend_share
    monthly["revenue_share"] = rev_share
    monthly["misalignment"] = (spend_share - rev_share).abs()
    
    # Identify over-spend (spend share > revenue share) and under-spend periods
    monthly["status"] = monthly.apply(
        lambda r: "overspend" if r["spend_share"] > r["revenue_share"] * 1.15
        else ("underspend" if r["spend_share"] < r["revenue_share"] * 0.85 else "aligned"),
        axis=1
    )
    
    # Calculate timing leakage: revenue lost from misalignment
    total_spend = monthly["spend"].sum()
    total_revenue = monthly["revenue"].sum()
    
    # If spend were allocated proportional to revenue seasonality
    optimal_spend = total_spend * rev_share
    actual_spend = monthly["spend"]
    
    # Use marginal efficiency: overspent periods have lower marginal ROI
    avg_roi = total_revenue / total_spend if total_spend > 0 else 0
    timing_loss = 0
    for _, row in monthly.iterrows():
        if row["status"] == "overspend":
            excess = row["spend"] - (total_spend * row["revenue_share"])
            timing_loss += excess * avg_roi * 0.3  # 30% marginal inefficiency on excess
    
    return {
        "total_timing_leakage": round(timing_loss, 0),
        "misalignment_score": round(float(monthly["misalignment"].mean() * 100), 1),
        "months": monthly[[monthly.columns[0], "spend_share", "revenue_share", "misalignment", "status"]].to_dict(orient="records"),
        "overspend_periods": int((monthly["status"] == "overspend").sum()),
        "underspend_periods": int((monthly["status"] == "underspend").sum()),
    }


def online_offline_leakage(df: pd.DataFrame) -> Dict:
    """
    Analyze revenue flow between online and offline channels.
    - Online demand not captured offline (digital leads → no store conversion)
    - Offline campaigns not converting digitally (TV ad → no website visit)
    """
    ch_type_col = "channel_type" if "channel_type" in df.columns else "ct"
    
    online = df[df[ch_type_col] == "online"]
    offline = df[df[ch_type_col] == "offline"]
    
    if len(online) == 0 or len(offline) == 0:
        return {"error": "Need both online and offline channel data"}
    
    # Monthly online vs offline correlation
    time_col = "month" if "month" in df.columns else "date"
    
    on_monthly = online.groupby(time_col).agg(
        on_spend=("spend", "sum"), on_rev=("revenue", "sum"),
        on_leads=("leads", "sum") if "leads" in df.columns else ("spend", "count"),
    ).reset_index()
    
    off_monthly = offline.groupby(time_col).agg(
        off_spend=("spend", "sum"), off_rev=("revenue", "sum"),
        off_leads=("leads", "sum") if "leads" in df.columns else ("spend", "count"),
    ).reset_index()
    
    merged = on_monthly.merge(off_monthly, on=time_col, how="outer").fillna(0)
    
    # Correlation between online spend and offline revenue (cross-channel effect)
    if len(merged) >= 4:
        on_off_corr = float(np.corrcoef(merged["on_spend"], merged["off_rev"])[0, 1])
        off_on_corr = float(np.corrcoef(merged["off_spend"], merged["on_rev"])[0, 1])
    else:
        on_off_corr = 0
        off_on_corr = 0
    
    # Estimate cross-channel contribution
    on_rev_total = float(online["revenue"].sum())
    off_rev_total = float(offline["revenue"].sum())
    on_spend_total = float(online["spend"].sum())
    off_spend_total = float(offline["spend"].sum())
    
    # Heuristic: if offline spend correlates with online revenue,
    # some online revenue is driven by offline campaigns
    off_contribution_to_online = max(0, off_on_corr * on_rev_total * 0.15)  # Conservative estimate
    on_contribution_to_offline = max(0, on_off_corr * off_rev_total * 0.10)
    
    return {
        "online_revenue": round(on_rev_total, 0),
        "offline_revenue": round(off_rev_total, 0),
        "online_spend": round(on_spend_total, 0),
        "offline_spend": round(off_spend_total, 0),
        "online_roi": round((on_rev_total - on_spend_total) / max(on_spend_total, 1), 2),
        "offline_roi": round((off_rev_total - off_spend_total) / max(off_spend_total, 1), 2),
        "cross_channel_correlation": {
            "online_spend_to_offline_revenue": round(on_off_corr, 3),
            "offline_spend_to_online_revenue": round(off_on_corr, 3),
        },
        "estimated_cross_contribution": {
            "offline_driving_online": round(off_contribution_to_online, 0),
            "online_driving_offline": round(on_contribution_to_offline, 0),
        },
        "monthly_trend": merged.to_dict(orient="records"),
    }


def audience_leakage(df: pd.DataFrame) -> Dict:
    """
    Identify high-converting audience segments receiving disproportionately low spend.
    """
    if "audience_segment" not in df.columns and "audience" not in df.columns:
        # Use region as proxy
        group_col = "region" if "region" in df.columns else "reg"
    else:
        group_col = "audience_segment" if "audience_segment" in df.columns else "audience"
    
    if group_col not in df.columns:
        return {"error": "No audience/region data available"}
    
    segments = df.groupby(group_col).agg(
        spend=("spend", "sum"),
        revenue=("revenue", "sum"),
        conversions=("conversions", "sum") if "conversions" in df.columns else ("conv", "sum"),
    ).reset_index()
    
    total_spend = segments["spend"].sum()
    total_rev = segments["revenue"].sum()
    
    segments["spend_share"] = segments["spend"] / total_spend
    segments["revenue_share"] = segments["revenue"] / total_rev
    segments["roi"] = (segments["revenue"] - segments["spend"]) / segments["spend"].clip(lower=1)
    segments["efficiency_ratio"] = segments["revenue_share"] / segments["spend_share"].clip(lower=0.01)
    
    # Underfunded = high revenue share, low spend share
    segments["status"] = segments.apply(
        lambda r: "underfunded" if r["efficiency_ratio"] > 1.3
        else ("overfunded" if r["efficiency_ratio"] < 0.7 else "balanced"),
        axis=1
    )
    
    # Calculate leakage from audience misallocation
    total_leakage = 0
    for _, row in segments.iterrows():
        if row["status"] == "underfunded":
            optimal_spend = total_spend * row["revenue_share"]
            additional_spend = optimal_spend - row["spend"]
            additional_revenue = additional_spend * row["roi"] * 0.5  # Conservative
            total_leakage += max(0, additional_revenue)
    
    return {
        "total_audience_leakage": round(total_leakage, 0),
        "segments": segments.to_dict(orient="records"),
        "underfunded_segments": int((segments["status"] == "underfunded").sum()),
        "overfunded_segments": int((segments["status"] == "overfunded").sum()),
        "group_by": group_col,
    }


def run_cross_channel_analysis(df: pd.DataFrame) -> Dict:
    """Run all cross-channel leakage analyses."""
    timing = timing_leakage(df)
    online_offline = online_offline_leakage(df)
    audience = audience_leakage(df)
    
    total_cross_leakage = (
        timing["total_timing_leakage"] +
        audience.get("total_audience_leakage", 0)
    )
    
    return {
        "timing_leakage": timing,
        "online_offline_flow": online_offline,
        "audience_leakage": audience,
        "total_cross_channel_leakage": round(total_cross_leakage, 0),
        "cross_channel_insights": _generate_insights(timing, online_offline, audience),
    }


def _generate_insights(timing, online_offline, audience) -> List[str]:
    """Generate human-readable cross-channel insights."""
    insights = []
    
    if timing["misalignment_score"] > 10:
        insights.append(
            f"Spend timing is misaligned with revenue seasonality "
            f"(score: {timing['misalignment_score']:.0f}%). "
            f"{timing['overspend_periods']} months are overspent relative to conversion potential."
        )
    
    if isinstance(online_offline, dict) and "cross_channel_correlation" in online_offline:
        cc = online_offline["cross_channel_correlation"]
        if cc.get("offline_spend_to_online_revenue", 0) > 0.3:
            insights.append(
                f"Offline spend shows {cc['offline_spend_to_online_revenue']:.0%} correlation "
                f"with online revenue — offline campaigns may be driving digital conversions."
            )
    
    if isinstance(audience, dict) and audience.get("underfunded_segments", 0) > 0:
        insights.append(
            f"{audience['underfunded_segments']} audience segments are underfunded relative "
            f"to their conversion efficiency. Estimated leakage: "
            f"${audience.get('total_audience_leakage', 0):,.0f}."
        )
    
    return insights


if __name__ == "__main__":
    from mock_data import generate_all_data
    
    data = generate_all_data()
    df = data["campaign_performance"]
    
    result = run_cross_channel_analysis(df)
    
    print("=== Cross-Channel Leakage ===")
    print(f"Total: ${result['total_cross_channel_leakage']:,.0f}")
    
    print(f"\nTiming Leakage: ${result['timing_leakage']['total_timing_leakage']:,.0f}")
    print(f"  Misalignment score: {result['timing_leakage']['misalignment_score']:.1f}%")
    
    print(f"\nOnline↔Offline Flow:")
    if "cross_channel_correlation" in result["online_offline_flow"]:
        cc = result["online_offline_flow"]["cross_channel_correlation"]
        print(f"  Online→Offline correlation: {cc['online_spend_to_offline_revenue']:.3f}")
        print(f"  Offline→Online correlation: {cc['offline_spend_to_online_revenue']:.3f}")
    
    print(f"\nAudience Leakage: ${result['audience_leakage'].get('total_audience_leakage', 0):,.0f}")
    
    print(f"\nInsights:")
    for insight in result["cross_channel_insights"]:
        print(f"  • {insight}")
