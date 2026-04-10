"""
Diagnostics & Recommendation Engine
Rule-based engine that identifies specific problems and generates
actionable recommendations following the blueprint's quality standard.

Diagnostic Categories:
- Underfunded high performer
- Overfunded saturated channel
- Good engagement, poor conversion
- Strong conversion, poor economics
- Assist-heavy channel
- Channel cannibalization
- Poor funnel handoff
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


HURDLE_RATE = 1.5  # Minimum acceptable ROI
CAC_THRESHOLD_MULT = 1.5  # CAC exceeds median by this much = flagged


def run_diagnostics(
    campaign_df: pd.DataFrame,
    response_curves: Dict[str, Dict],
    attribution_results: Dict[str, pd.DataFrame],
    optimization_result: Optional[Dict] = None,
) -> List[Dict]:
    """
    Run all diagnostic rules and generate recommendations.
    Returns list of structured recommendations per blueprint quality standard.
    """
    recommendations = []
    
    # Aggregate channel-level metrics
    channel_metrics = _compute_channel_metrics(campaign_df)
    
    # 1. Underfunded high performers
    recommendations.extend(
        _detect_underfunded(channel_metrics, response_curves)
    )
    
    # 2. Overfunded saturated channels
    recommendations.extend(
        _detect_overfunded(channel_metrics, response_curves)
    )
    
    # 3. Good engagement, poor conversion
    recommendations.extend(
        _detect_engagement_conversion_mismatch(campaign_df)
    )
    
    # 4. Strong conversion, poor economics
    recommendations.extend(
        _detect_poor_economics(channel_metrics)
    )
    
    # 5. Assist-heavy channels (compare attribution models)
    if len(attribution_results) >= 2:
        recommendations.extend(
            _detect_assist_heavy(attribution_results)
        )
    
    # 6. Poor funnel handoff
    recommendations.extend(
        _detect_funnel_issues(campaign_df)
    )
    
    # 7. Channel cannibalization signals
    recommendations.extend(
        _detect_cannibalization(campaign_df)
    )
    
    # Sort by expected impact
    recommendations.sort(key=lambda r: r.get("expected_impact_revenue", 0), reverse=True)
    
    # Assign priority
    for i, rec in enumerate(recommendations):
        rec["priority"] = i + 1
        rec["id"] = f"REC-{i+1:03d}"
    
    return recommendations


def _compute_channel_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate campaign data to channel level with key metrics."""
    channel = df.groupby("channel").agg(
        total_spend=("spend", "sum"),
        total_revenue=("revenue", "sum"),
        total_impressions=("impressions", "sum"),
        total_clicks=("clicks", "sum"),
        total_leads=("leads", "sum"),
        total_conversions=("conversions", "sum"),
        avg_bounce_rate=("bounce_rate", "mean"),
        avg_form_completion=("form_completion_rate", "mean"),
        avg_nps=("nps_score", "mean"),
        channel_type=("channel_type", "first"),
    ).reset_index()
    
    channel["roi"] = (channel["total_revenue"] - channel["total_spend"]) / channel["total_spend"]
    channel["roas"] = channel["total_revenue"] / channel["total_spend"]
    channel["ctr"] = channel["total_clicks"] / channel["total_impressions"]
    channel["cvr"] = channel["total_conversions"] / channel["total_clicks"].clip(lower=1)
    channel["cac"] = channel["total_spend"] / channel["total_conversions"].clip(lower=1)
    channel["cpl"] = channel["total_spend"] / channel["total_leads"].clip(lower=1)
    
    return channel


def _detect_underfunded(
    metrics: pd.DataFrame, curves: Dict[str, Dict]
) -> List[Dict]:
    """Find channels with high ROI and headroom on response curve."""
    recs = []
    median_roi = metrics["roi"].median()
    
    for _, row in metrics.iterrows():
        ch = row["channel"]
        if ch not in curves:
            continue
        
        curve = curves[ch]
        headroom = curve.get("headroom_pct", 0)
        marginal_roi = curve.get("current_marginal_roi", 0)
        
        if row["roi"] > median_roi * 1.3 and headroom > 20 and marginal_roi > HURDLE_RATE:
            # Calculate recommended increase
            increase_pct = min(headroom * 0.5, 40)  # Don't recommend more than 40% increase
            additional_spend = row["total_spend"] * increase_pct / 100
            expected_additional_rev = additional_spend * marginal_roi * 0.8  # Conservative
            
            recs.append({
                "type": "SCALE",
                "channel": ch,
                "campaign": "All campaigns",
                "rationale": (
                    f"{ch} has ROI of {row['roi']:.2f}x (above median {median_roi:.2f}x) "
                    f"with {headroom:.0f}% headroom on the response curve. "
                    f"Marginal ROI at current spend is {marginal_roi:.2f}x, "
                    f"well above the {HURDLE_RATE}x hurdle rate."
                ),
                "action": f"Increase spend by {increase_pct:.0f}% (${additional_spend:,.0f})",
                "expected_impact_revenue": round(expected_additional_rev, 0),
                "expected_impact_roi": round(marginal_roi * 0.8, 2),
                "confidence": "High" if curve.get("r_squared", 0) > 0.7 else "Medium",
                "effort": "Low",
                "evidence": {
                    "current_roi": round(row["roi"], 2),
                    "marginal_roi": round(marginal_roi, 2),
                    "headroom_pct": round(headroom, 1),
                    "r_squared": round(curve.get("r_squared", 0), 3),
                },
            })
    
    return recs


def _detect_overfunded(
    metrics: pd.DataFrame, curves: Dict[str, Dict]
) -> List[Dict]:
    """Find channels past saturation or with marginal ROI below hurdle."""
    recs = []
    
    for _, row in metrics.iterrows():
        ch = row["channel"]
        if ch not in curves:
            continue
        
        curve = curves[ch]
        marginal_roi = curve.get("current_marginal_roi", 0)
        headroom = curve.get("headroom_pct", 0)
        
        if marginal_roi < HURDLE_RATE and headroom < 15:
            reduce_pct = min(30, max(10, (HURDLE_RATE - marginal_roi) / HURDLE_RATE * 50))
            savings = row["total_spend"] * reduce_pct / 100
            
            recs.append({
                "type": "REDUCE",
                "channel": ch,
                "campaign": "All campaigns",
                "rationale": (
                    f"{ch} marginal ROI has fallen to {marginal_roi:.2f}x, "
                    f"below the {HURDLE_RATE}x hurdle rate, with only {headroom:.0f}% "
                    f"headroom remaining on the response curve. "
                    f"Spend is near or past the saturation point."
                ),
                "action": f"Reduce spend by {reduce_pct:.0f}% (save ${savings:,.0f})",
                "expected_impact_revenue": round(-savings * marginal_roi, 0),
                "expected_impact_roi": round(0.1, 2),
                "reallocation_target": "Redirect to underfunded high-ROI channels",
                "confidence": "High" if curve.get("r_squared", 0) > 0.7 else "Medium",
                "effort": "Low",
                "evidence": {
                    "marginal_roi": round(marginal_roi, 2),
                    "headroom_pct": round(headroom, 1),
                    "saturation_spend": round(curve.get("saturation_spend", 0), 0),
                },
            })
    
    return recs


def _detect_engagement_conversion_mismatch(df: pd.DataFrame) -> List[Dict]:
    """Find campaigns with high CTR but low conversion rate."""
    recs = []
    
    campaign_metrics = df.groupby(["channel", "campaign"]).agg(
        spend=("spend", "sum"),
        clicks=("clicks", "sum"),
        impressions=("impressions", "sum"),
        conversions=("conversions", "sum"),
        bounce_rate=("bounce_rate", "mean"),
        form_completion=("form_completion_rate", "mean"),
    ).reset_index()
    
    campaign_metrics["ctr"] = campaign_metrics["clicks"] / campaign_metrics["impressions"].clip(lower=1)
    campaign_metrics["cvr"] = campaign_metrics["conversions"] / campaign_metrics["clicks"].clip(lower=1)
    
    median_ctr = campaign_metrics["ctr"].median()
    median_cvr = campaign_metrics["cvr"].median()
    
    for _, row in campaign_metrics.iterrows():
        if row["ctr"] > median_ctr * 1.5 and row["cvr"] < median_cvr * 0.6:
            suppressed_conversions = row["clicks"] * (median_cvr - row["cvr"])
            suppressed_revenue = suppressed_conversions * 1800  # avg AOV
            
            recs.append({
                "type": "FIX",
                "channel": row["channel"],
                "campaign": row["campaign"],
                "rationale": (
                    f"{row['campaign']} has strong CTR ({row['ctr']:.1%}, "
                    f"{row['ctr']/median_ctr:.1f}x median) but poor conversion "
                    f"({row['cvr']:.2%}, {row['cvr']/median_cvr:.1f}x median). "
                    f"Bounce rate is {row['bounce_rate']:.0%} and form completion "
                    f"is {row['form_completion']:.0%}. This signals a landing page "
                    f"or journey friction issue."
                ),
                "action": "Audit landing page, test alternative CTAs, review form UX",
                "expected_impact_revenue": round(suppressed_revenue * 0.4, 0),
                "expected_impact_roi": 0,
                "confidence": "High",
                "effort": "Medium",
                "evidence": {
                    "ctr": round(row["ctr"], 4),
                    "cvr": round(row["cvr"], 4),
                    "bounce_rate": round(row["bounce_rate"], 3),
                    "suppressed_conversions": round(suppressed_conversions, 0),
                },
            })
    
    return recs


def _detect_poor_economics(metrics: pd.DataFrame) -> List[Dict]:
    """Find channels with good conversion but high CAC."""
    recs = []
    median_cac = metrics["cac"].median()
    median_cvr = metrics["cvr"].median()
    
    for _, row in metrics.iterrows():
        if row["cvr"] > median_cvr * 0.9 and row["cac"] > median_cac * CAC_THRESHOLD_MULT:
            recs.append({
                "type": "RETARGET",
                "channel": row["channel"],
                "campaign": "All campaigns",
                "rationale": (
                    f"{row['channel']} converts well ({row['cvr']:.2%}) but CAC "
                    f"is ${row['cac']:,.0f} ({row['cac']/median_cac:.1f}x median ${median_cac:,.0f}). "
                    f"Bid strategy or audience targeting may be driving up costs."
                ),
                "action": "Review bid strategy, tighten audience targeting, test lookalikes",
                "expected_impact_revenue": 0,
                "expected_impact_roi": round((row["cac"] - median_cac) / row["cac"], 2),
                "confidence": "Medium",
                "effort": "Medium",
                "evidence": {
                    "cac": round(row["cac"], 0),
                    "median_cac": round(median_cac, 0),
                    "cvr": round(row["cvr"], 4),
                },
            })
    
    return recs


def _detect_assist_heavy(attr_results: Dict[str, pd.DataFrame]) -> List[Dict]:
    """Find channels that look weak on last-touch but strong on multi-touch."""
    recs = []
    
    if "last_touch" not in attr_results or "linear" not in attr_results:
        return recs
    
    lt = attr_results["last_touch"].groupby("channel")["attributed_revenue"].sum()
    lin = attr_results["linear"].groupby("channel")["attributed_revenue"].sum()
    
    for ch in lt.index:
        if ch not in lin.index:
            continue
        lt_rev = float(lt[ch])
        lin_rev = float(lin[ch])
        
        if lt_rev > 0 and lin_rev / lt_rev > 1.5:
            recs.append({
                "type": "MAINTAIN",
                "channel": ch,
                "campaign": "All campaigns",
                "rationale": (
                    f"{ch} appears weak on last-touch (${lt_rev:,.0f}) but strong on "
                    f"linear attribution (${lin_rev:,.0f}, {lin_rev/lt_rev:.1f}x higher). "
                    f"This channel assists conversions in other channels. "
                    f"Cutting based on last-touch alone would damage overall performance."
                ),
                "action": "Maintain current spend; do not cut based on last-touch metrics",
                "expected_impact_revenue": round(lin_rev - lt_rev, 0),
                "expected_impact_roi": 0,
                "confidence": "Medium",
                "effort": "None",
                "evidence": {
                    "last_touch_revenue": round(lt_rev, 0),
                    "linear_revenue": round(lin_rev, 0),
                    "assist_ratio": round(lin_rev / lt_rev, 2),
                },
            })
    
    return recs


def _detect_funnel_issues(df: pd.DataFrame) -> List[Dict]:
    """Find channels with significant funnel drop-offs."""
    recs = []
    
    channel_funnel = df.groupby("channel").agg(
        leads=("leads", "sum"),
        mqls=("mqls", "sum"),
        sqls=("sqls", "sum"),
        conversions=("conversions", "sum"),
    ).reset_index()
    
    channel_funnel["lead_to_mql"] = channel_funnel["mqls"] / channel_funnel["leads"].clip(lower=1)
    channel_funnel["mql_to_sql"] = channel_funnel["sqls"] / channel_funnel["mqls"].clip(lower=1)
    channel_funnel["sql_to_conv"] = channel_funnel["conversions"] / channel_funnel["sqls"].clip(lower=1)
    
    median_l2m = channel_funnel["lead_to_mql"].median()
    median_m2s = channel_funnel["mql_to_sql"].median()
    median_s2c = channel_funnel["sql_to_conv"].median()
    
    for _, row in channel_funnel.iterrows():
        worst_stage = None
        worst_ratio = 1.0
        
        if row["lead_to_mql"] < median_l2m * 0.6:
            worst_stage = "Lead → MQL"
            worst_ratio = row["lead_to_mql"] / median_l2m
        if row["mql_to_sql"] < median_m2s * 0.6:
            if worst_ratio > row["mql_to_sql"] / median_m2s:
                worst_stage = "MQL → SQL"
                worst_ratio = row["mql_to_sql"] / median_m2s
        if row["sql_to_conv"] < median_s2c * 0.6:
            if worst_ratio > row["sql_to_conv"] / median_s2c:
                worst_stage = "SQL → Conversion"
                worst_ratio = row["sql_to_conv"] / median_s2c
        
        if worst_stage:
            recs.append({
                "type": "RESEQUENCE",
                "channel": row["channel"],
                "campaign": "All campaigns",
                "rationale": (
                    f"{row['channel']} has a significant drop-off at {worst_stage} "
                    f"({worst_ratio:.0%} of median). This suggests a handoff problem "
                    f"between funnel stages."
                ),
                "action": f"Audit {worst_stage} handoff; review nurture sequence and timing",
                "expected_impact_revenue": 0,
                "expected_impact_roi": 0,
                "confidence": "Medium",
                "effort": "Medium",
                "evidence": {
                    "worst_stage": worst_stage,
                    "stage_rate_vs_median": round(worst_ratio, 2),
                },
            })
    
    return recs


def _detect_cannibalization(df: pd.DataFrame) -> List[Dict]:
    """Detect potential channel overlap / cannibalization signals."""
    recs = []
    
    # Look at channels with correlated spend increases but not proportional revenue increases
    monthly = df.groupby(["month", "channel"]).agg(
        spend=("spend", "sum"),
        revenue=("revenue", "sum"),
    ).reset_index()
    
    channels = monthly["channel"].unique()
    
    for i, ch1 in enumerate(channels):
        for ch2 in channels[i+1:]:
            s1 = monthly[monthly["channel"] == ch1].sort_values("month")["spend"].values
            s2 = monthly[monthly["channel"] == ch2].sort_values("month")["spend"].values
            r1 = monthly[monthly["channel"] == ch1].sort_values("month")["revenue"].values
            r2 = monthly[monthly["channel"] == ch2].sort_values("month")["revenue"].values
            
            if len(s1) != len(s2) or len(s1) < 6:
                continue
            
            spend_corr = np.corrcoef(s1, s2)[0, 1]
            # If spend highly correlated but combined revenue growth is sublinear
            combined_rev = r1 + r2
            combined_spend = s1 + s2
            efficiency = combined_rev / combined_spend
            efficiency_trend = np.polyfit(range(len(efficiency)), efficiency, 1)[0]
            
            if spend_corr > 0.7 and efficiency_trend < -0.001:
                recs.append({
                    "type": "CONSOLIDATE",
                    "channel": f"{ch1} + {ch2}",
                    "campaign": "Cross-channel",
                    "rationale": (
                        f"{ch1} and {ch2} spend is highly correlated (r={spend_corr:.2f}) "
                        f"but combined efficiency is declining. This may indicate "
                        f"audience overlap or cannibalization."
                    ),
                    "action": "Audit audience overlap; consider sequencing instead of parallel spend",
                    "expected_impact_revenue": 0,
                    "expected_impact_roi": 0,
                    "confidence": "Low",
                    "effort": "High",
                    "evidence": {
                        "spend_correlation": round(spend_corr, 2),
                        "efficiency_trend": round(efficiency_trend, 4),
                    },
                })
    
    return recs


if __name__ == "__main__":
    from mock_data import generate_all_data
    from response_curves import fit_response_curves
    from attribution import run_all_attribution
    
    data = generate_all_data()
    curves = fit_response_curves(data["campaign_performance"])
    attr = run_all_attribution(data["user_journeys"])
    
    recs = run_diagnostics(data["campaign_performance"], curves, attr)
    
    print(f"\n=== {len(recs)} Recommendations Generated ===\n")
    for rec in recs:
        print(f"[{rec['id']}] {rec['type']} | {rec['channel']}")
        print(f"  {rec['rationale']}")
        print(f"  Action: {rec['action']}")
        print(f"  Impact: ${rec.get('expected_impact_revenue', 0):,.0f} | "
              f"Confidence: {rec['confidence']} | Effort: {rec['effort']}")
        print()
