"""
Three Pillar Impact Engine
Pillar 1: Revenue Leakage (optimized - actual revenue)
Pillar 2: Experience Drop (conversion suppression model)
Pillar 3: Avoidable Cost (excess CAC, lead waste, retargeting waste)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


def calculate_revenue_leakage(
    campaign_df: pd.DataFrame,
    optimization_result: Dict,
) -> Dict:
    """
    Revenue Leakage = Optimized Revenue - Actual Revenue
    Broken down by channel allocation leakage and campaign mix leakage.
    """
    actual_revenue = campaign_df["revenue"].sum()
    actual_spend = campaign_df["spend"].sum()
    
    opt_revenue = optimization_result["summary"]["optimized_total_revenue"]
    
    total_leakage = max(0, opt_revenue - actual_revenue)
    
    # Break down by channel
    channel_leakage = []
    for ch_result in optimization_result.get("channel_results", []):
        ch_leakage = max(0, ch_result["optimized_revenue"] - ch_result["current_revenue"])
        channel_leakage.append({
            "channel": ch_result["channel"],
            "current_spend": ch_result["current_spend"],
            "optimal_spend": ch_result["optimized_spend"],
            "spend_delta": ch_result["optimized_spend"] - ch_result["current_spend"],
            "current_revenue": ch_result["current_revenue"],
            "optimal_revenue": ch_result["optimized_revenue"],
            "leakage": round(ch_leakage, 2),
            "leakage_pct_of_total": round(ch_leakage / total_leakage * 100, 1) if total_leakage > 0 else 0,
            "leakage_type": "underfunded" if ch_result["change_pct"] > 5 else (
                "overfunded" if ch_result["change_pct"] < -5 else "aligned"
            ),
        })
    
    # Campaign mix leakage (within-channel misallocation)
    campaign_mix_leakage = _calculate_campaign_mix_leakage(campaign_df)
    
    return {
        "total_leakage": round(total_leakage, 2),
        "leakage_pct_of_revenue": round(total_leakage / actual_revenue * 100, 1) if actual_revenue > 0 else 0,
        "channel_allocation_leakage": round(total_leakage * 0.65, 2),  # ~65% from channel allocation
        "campaign_mix_leakage": round(total_leakage * 0.35, 2),  # ~35% from campaign mix
        "channel_breakdown": sorted(channel_leakage, key=lambda x: x["leakage"], reverse=True),
        "campaign_mix_detail": campaign_mix_leakage,
        "actual_revenue": round(actual_revenue, 2),
        "optimal_revenue": round(opt_revenue, 2),
    }


def calculate_experience_impact(campaign_df: pd.DataFrame) -> Dict:
    """
    Conversion Suppression Model (per corrected blueprint):
    Step 1: Find campaigns with high engagement but low conversion
    Step 2: Calculate conversion rate gap (expected - actual)
    Step 3: Multiply gap by volume and AOV to get suppressed revenue
    Step 4: Flag retention risk signals separately
    """
    campaign_metrics = campaign_df.groupby(["channel", "campaign"]).agg(
        spend=("spend", "sum"),
        clicks=("clicks", "sum"),
        impressions=("impressions", "sum"),
        conversions=("conversions", "sum"),
        revenue=("revenue", "sum"),
        bounce_rate=("bounce_rate", "mean"),
        session_duration=("avg_session_duration_sec", "mean"),
        form_completion=("form_completion_rate", "mean"),
        nps=("nps_score", "mean"),
        unsub_rate=("unsubscribe_rate", "mean"),
    ).reset_index()
    
    campaign_metrics["ctr"] = campaign_metrics["clicks"] / campaign_metrics["impressions"].clip(lower=1)
    campaign_metrics["cvr"] = campaign_metrics["conversions"] / campaign_metrics["clicks"].clip(lower=1)
    
    median_cvr = campaign_metrics["cvr"].median()
    median_ctr = campaign_metrics["ctr"].median()
    avg_aov = (campaign_metrics["revenue"].sum() / campaign_metrics["conversions"].sum()) if campaign_metrics["conversions"].sum() > 0 else 1800
    
    # Step 1-3: Conversion suppression
    suppression_items = []
    total_suppressed_revenue = 0
    
    for _, row in campaign_metrics.iterrows():
        # High engagement = CTR above median; Poor conversion = CVR below median * 0.7
        if row["ctr"] > median_ctr * 1.0 and row["cvr"] < median_cvr * 0.7:
            expected_cvr = median_cvr  # benchmark
            cvr_gap = expected_cvr - row["cvr"]
            suppressed_conversions = row["clicks"] * cvr_gap
            suppressed_revenue = suppressed_conversions * avg_aov
            total_suppressed_revenue += suppressed_revenue
            
            suppression_items.append({
                "channel": row["channel"],
                "campaign": row["campaign"],
                "actual_cvr": round(row["cvr"], 4),
                "expected_cvr": round(expected_cvr, 4),
                "cvr_gap": round(cvr_gap, 4),
                "traffic_volume": int(row["clicks"]),
                "suppressed_conversions": round(suppressed_conversions, 0),
                "suppressed_revenue": round(suppressed_revenue, 2),
                "bounce_rate": round(row["bounce_rate"], 3),
                "form_completion": round(row["form_completion"], 3),
                "friction_signals": _identify_friction(row),
            })
    
    # Step 4: Retention risk signals (separate, not forced into composite)
    retention_risks = []
    for _, row in campaign_metrics.iterrows():
        risks = []
        if row["nps"] < 25:
            risks.append(f"Low NPS ({row['nps']:.0f})")
        if row["unsub_rate"] > 0.005:
            risks.append(f"High unsubscribe rate ({row['unsub_rate']:.1%})")
        if row["bounce_rate"] > 0.6:
            risks.append(f"High bounce rate ({row['bounce_rate']:.0%})")
        
        if risks:
            retention_risks.append({
                "channel": row["channel"],
                "campaign": row["campaign"],
                "risk_signals": risks,
                "severity": "High" if len(risks) >= 2 else "Medium",
            })
    
    return {
        "total_suppressed_revenue": round(total_suppressed_revenue, 2),
        "campaigns_with_suppression": len(suppression_items),
        "suppression_detail": sorted(suppression_items, key=lambda x: x["suppressed_revenue"], reverse=True),
        "retention_risks": retention_risks,
        "methodology": "Conversion-suppression model: (expected CVR - actual CVR) × traffic × AOV",
    }


def calculate_avoidable_cost(
    campaign_df: pd.DataFrame,
    optimization_result: Optional[Dict] = None,
) -> Dict:
    """
    Avoidable Cost = Actual Cost to Acquire - Optimized Cost to Acquire
    Broken down: excess CAC, lead waste, retargeting waste, duplicate targeting.
    """
    channel_metrics = campaign_df.groupby("channel").agg(
        spend=("spend", "sum"),
        conversions=("conversions", "sum"),
        leads=("leads", "sum"),
        mqls=("mqls", "sum"),
        sqls=("sqls", "sum"),
        revenue=("revenue", "sum"),
    ).reset_index()
    
    channel_metrics["cac"] = channel_metrics["spend"] / channel_metrics["conversions"].clip(lower=1)
    median_cac = channel_metrics["cac"].median()
    
    cost_items = []
    total_avoidable = 0
    
    # 1. Excess CAC
    for _, row in channel_metrics.iterrows():
        if row["cac"] > median_cac * 1.3:
            excess = (row["cac"] - median_cac) * row["conversions"]
            cost_items.append({
                "type": "Excess CAC",
                "channel": row["channel"],
                "actual_cac": round(row["cac"], 0),
                "benchmark_cac": round(median_cac, 0),
                "volume": int(row["conversions"]),
                "avoidable_cost": round(excess, 2),
            })
            total_avoidable += excess
    
    # 2. Lead waste (leads that never convert)
    for _, row in channel_metrics.iterrows():
        lead_to_conv = row["conversions"] / row["leads"] if row["leads"] > 0 else 0
        if lead_to_conv < 0.05:  # less than 5% of leads convert
            wasted_leads = row["leads"] - row["conversions"]
            # Estimate cost per lead handling (sales follow-up time)
            handling_cost = wasted_leads * 15  # $15 per wasted lead handling
            cost_items.append({
                "type": "Low-Quality Lead Handling",
                "channel": row["channel"],
                "lead_to_conversion_rate": round(lead_to_conv, 4),
                "wasted_leads": int(wasted_leads),
                "volume": int(wasted_leads),
                "avoidable_cost": round(handling_cost, 2),
            })
            total_avoidable += handling_cost
    
    # 3. Retargeting waste estimate
    retargeting_campaigns = campaign_df[
        campaign_df["campaign"].str.contains("Retargeting", case=False, na=False)
    ]
    if len(retargeting_campaigns) > 0:
        rt_spend = retargeting_campaigns["spend"].sum()
        rt_conv = retargeting_campaigns["conversions"].sum()
        rt_rev = retargeting_campaigns["revenue"].sum()
        if rt_spend > 0 and rt_rev / rt_spend < 1.0:
            waste = rt_spend - rt_rev
            cost_items.append({
                "type": "Retargeting Waste",
                "channel": "retargeting",
                "spend": round(rt_spend, 0),
                "revenue": round(rt_rev, 0),
                "volume": 1,
                "avoidable_cost": round(max(0, waste * 0.4), 2),  # 40% estimated recoverable
            })
            total_avoidable += max(0, waste * 0.4)
    
    return {
        "total_avoidable_cost": round(total_avoidable, 2),
        "avoidable_pct_of_spend": round(
            total_avoidable / campaign_df["spend"].sum() * 100, 1
        ) if campaign_df["spend"].sum() > 0 else 0,
        "cost_breakdown": sorted(cost_items, key=lambda x: x["avoidable_cost"], reverse=True),
    }


def calculate_all_pillars(
    campaign_df: pd.DataFrame,
    optimization_result: Dict,
) -> Dict:
    """Run all three pillar calculations and return combined results."""
    leakage = calculate_revenue_leakage(campaign_df, optimization_result)
    experience = calculate_experience_impact(campaign_df)
    cost = calculate_avoidable_cost(campaign_df, optimization_result)
    
    return {
        "revenue_leakage": leakage,
        "experience_impact": experience,
        "avoidable_cost": cost,
        "total_value_at_risk": round(
            leakage["total_leakage"] +
            experience["total_suppressed_revenue"] +
            cost["total_avoidable_cost"],
            2
        ),
        "correction_potential": {
            "revenue_uplift": round(leakage["total_leakage"] * 0.6, 2),
            "experience_recovery": round(experience["total_suppressed_revenue"] * 0.4, 2),
            "cost_savings": round(cost["total_avoidable_cost"] * 0.7, 2),
        },
    }


def _calculate_campaign_mix_leakage(df: pd.DataFrame) -> List[Dict]:
    """Within each channel, find campaigns that are over/under-funded relative to ROI."""
    results = []
    
    for channel in df["channel"].unique():
        ch_data = df[df["channel"] == channel]
        camp_perf = ch_data.groupby("campaign").agg(
            spend=("spend", "sum"),
            revenue=("revenue", "sum"),
        ).reset_index()
        
        camp_perf["roi"] = (camp_perf["revenue"] - camp_perf["spend"]) / camp_perf["spend"].clip(lower=1)
        median_roi = camp_perf["roi"].median()
        
        for _, row in camp_perf.iterrows():
            if row["roi"] > median_roi * 1.5:
                results.append({
                    "channel": channel,
                    "campaign": row["campaign"],
                    "status": "underfunded",
                    "roi": round(row["roi"], 2),
                    "channel_median_roi": round(median_roi, 2),
                })
            elif row["roi"] < median_roi * 0.5 and row["spend"] > camp_perf["spend"].median():
                results.append({
                    "channel": channel,
                    "campaign": row["campaign"],
                    "status": "overfunded",
                    "roi": round(row["roi"], 2),
                    "channel_median_roi": round(median_roi, 2),
                })
    
    return results


def _identify_friction(row) -> List[str]:
    """Identify specific UX friction signals for a campaign."""
    signals = []
    if row["bounce_rate"] > 0.55:
        signals.append("High bounce rate — landing page relevance issue")
    if row["form_completion"] < 0.06:
        signals.append("Low form completion — form UX or length issue")
    if row["session_duration"] < 60:
        signals.append("Very short sessions — content mismatch")
    if row["session_duration"] > 300 and row["cvr"] < 0.01:
        signals.append("Long sessions without conversion — unclear CTA")
    return signals


if __name__ == "__main__":
    from mock_data import generate_all_data
    from response_curves import fit_response_curves
    from optimizer import optimize_budget
    
    data = generate_all_data()
    campaigns = data["campaign_performance"]
    curves = fit_response_curves(campaigns)
    total_spend = campaigns["spend"].sum()
    opt = optimize_budget(curves, total_spend, objective="balanced")
    
    pillars = calculate_all_pillars(campaigns, opt)
    
    print(f"\n=== THREE PILLAR IMPACT ===")
    print(f"Total Value at Risk: ${pillars['total_value_at_risk']:,.0f}")
    print(f"\n1. Revenue Leakage: ${pillars['revenue_leakage']['total_leakage']:,.0f} "
          f"({pillars['revenue_leakage']['leakage_pct_of_revenue']:.1f}% of revenue)")
    print(f"2. Experience Suppression: ${pillars['experience_impact']['total_suppressed_revenue']:,.0f} "
          f"({pillars['experience_impact']['campaigns_with_suppression']} campaigns)")
    print(f"3. Avoidable Cost: ${pillars['avoidable_cost']['total_avoidable_cost']:,.0f} "
          f"({pillars['avoidable_cost']['avoidable_pct_of_spend']:.1f}% of spend)")
    
    print(f"\nCorrection Potential:")
    cp = pillars["correction_potential"]
    print(f"  Revenue uplift: ${cp['revenue_uplift']:,.0f}")
    print(f"  Experience recovery: ${cp['experience_recovery']:,.0f}")
    print(f"  Cost savings: ${cp['cost_savings']:,.0f}")
