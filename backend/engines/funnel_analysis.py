"""
Funnel Conversion Analysis Engine (Phase 1)
- Stage-by-stage conversion rates
- Drop-off identification with severity ranking
- Channel-level funnel comparison
- Benchmark vs actual comparison
- Bottleneck detection and quantification
"""

import pandas as pd
import numpy as np
from typing import Dict, List


FUNNEL_STAGES = ["impressions", "clicks", "leads", "mqls", "sqls", "conversions"]
STAGE_LABELS = {
    "impressions": "Impressions",
    "clicks": "Clicks",
    "leads": "Leads",
    "mqls": "MQLs",
    "sqls": "SQLs",
    "conversions": "Conversions",
}


def compute_funnel(df: pd.DataFrame, group_by: str = None) -> List[Dict]:
    """
    Compute full funnel metrics with conversion rates between each stage.
    Optionally grouped by channel, campaign, region, etc.
    """
    if group_by:
        groups = df.groupby(group_by)
    else:
        groups = [(None, df)]

    results = []
    for group_key, group_df in groups:
        volumes = {}
        for stage in FUNNEL_STAGES:
            if stage in group_df.columns:
                volumes[stage] = int(group_df[stage].sum())
            elif stage == "impressions" and "imps" in group_df.columns:
                volumes[stage] = int(group_df["imps"].sum())
            elif stage == "conversions" and "conv" in group_df.columns:
                volumes[stage] = int(group_df["conv"].sum())
            else:
                volumes[stage] = 0

        stages = []
        for i, stage in enumerate(FUNNEL_STAGES):
            vol = volumes[stage]
            prev_vol = volumes[FUNNEL_STAGES[i - 1]] if i > 0 else None
            conv_rate = vol / prev_vol if prev_vol and prev_vol > 0 else None
            drop_off = 1 - conv_rate if conv_rate is not None else None

            stages.append({
                "stage": STAGE_LABELS.get(stage, stage),
                "stage_key": stage,
                "volume": vol,
                "conversion_rate": round(conv_rate, 4) if conv_rate is not None else None,
                "drop_off_rate": round(drop_off, 4) if drop_off is not None else None,
                "from_stage": STAGE_LABELS.get(FUNNEL_STAGES[i - 1]) if i > 0 else None,
            })

        result = {
            "stages": stages,
            "overall_conversion": round(
                volumes["conversions"] / volumes["impressions"], 6
            ) if volumes["impressions"] > 0 else 0,
            "total_volume_top": volumes["impressions"],
            "total_volume_bottom": volumes["conversions"],
        }
        if group_key is not None:
            result["group"] = group_key

        results.append(result)

    return results


def identify_bottlenecks(
    funnel: List[Dict],
    benchmark_rates: Dict[str, float] = None,
) -> List[Dict]:
    """
    Identify funnel bottlenecks by comparing stage conversion rates
    against benchmarks or cross-channel medians.
    """
    if benchmark_rates is None:
        benchmark_rates = {
            "clicks": 0.02,        # CTR benchmark
            "leads": 0.08,         # Click-to-lead
            "mqls": 0.45,          # Lead-to-MQL
            "sqls": 0.38,          # MQL-to-SQL
            "conversions": 0.25,   # SQL-to-conversion
        }

    bottlenecks = []
    stages = funnel[0]["stages"] if funnel else []

    for stage_data in stages:
        if stage_data["conversion_rate"] is None:
            continue

        stage_key = stage_data["stage_key"]
        benchmark = benchmark_rates.get(stage_key)

        if benchmark and stage_data["conversion_rate"] < benchmark * 0.7:
            # Calculate lost volume
            prev_idx = FUNNEL_STAGES.index(stage_key) - 1
            prev_vol = stages[prev_idx]["volume"] if prev_idx >= 0 else 0
            expected_vol = prev_vol * benchmark
            actual_vol = stage_data["volume"]
            lost_vol = max(0, expected_vol - actual_vol)

            bottlenecks.append({
                "stage": stage_data["stage"],
                "from_stage": stage_data["from_stage"],
                "actual_rate": round(stage_data["conversion_rate"], 4),
                "benchmark_rate": round(benchmark, 4),
                "gap_pct": round((benchmark - stage_data["conversion_rate"]) / benchmark * 100, 1),
                "lost_volume": int(lost_vol),
                "severity": "critical" if stage_data["conversion_rate"] < benchmark * 0.5 else "warning",
                "recommendation": _get_bottleneck_recommendation(stage_key, stage_data["conversion_rate"], benchmark),
            })

    return sorted(bottlenecks, key=lambda x: x["gap_pct"], reverse=True)


def channel_funnel_comparison(df: pd.DataFrame) -> Dict:
    """
    Compare funnel metrics across channels to identify best/worst
    at each stage.
    """
    funnels = compute_funnel(df, group_by="channel")

    comparison = {}
    for stage_idx, stage_key in enumerate(FUNNEL_STAGES[1:], 1):
        rates = []
        for funnel in funnels:
            stage_data = funnel["stages"][stage_idx]
            if stage_data["conversion_rate"] is not None:
                rates.append({
                    "channel": funnel["group"],
                    "rate": stage_data["conversion_rate"],
                })

        if rates:
            rates.sort(key=lambda x: x["rate"], reverse=True)
            median_rate = np.median([r["rate"] for r in rates])

            comparison[stage_key] = {
                "stage_label": STAGE_LABELS.get(stage_key, stage_key),
                "best": rates[0],
                "worst": rates[-1],
                "median": round(float(median_rate), 4),
                "spread": round(rates[0]["rate"] - rates[-1]["rate"], 4),
                "all_rates": rates,
            }

    return comparison


def funnel_revenue_impact(df: pd.DataFrame) -> Dict:
    """
    Quantify revenue impact of funnel improvements.
    Shows: if each stage improved to median, how much additional revenue?
    """
    total_funnel = compute_funnel(df)[0]
    channel_funnels = compute_funnel(df, group_by="channel")
    comparison = channel_funnel_comparison(df)

    # Average revenue per conversion
    total_rev = df["revenue"].sum() if "revenue" in df.columns else df.get("rev", pd.Series([0])).sum()
    total_conv = total_funnel["total_volume_bottom"]
    avg_rev_per_conv = total_rev / max(total_conv, 1)

    impacts = []
    for stage_key, comp in comparison.items():
        for ch_data in comp["all_rates"]:
            if ch_data["rate"] < comp["median"]:
                # Find channel funnel
                ch_funnel = next((f for f in channel_funnels if f["group"] == ch_data["channel"]), None)
                if not ch_funnel:
                    continue

                stage_idx = FUNNEL_STAGES.index(stage_key)
                prev_vol = ch_funnel["stages"][stage_idx - 1]["volume"] if stage_idx > 0 else 0
                additional_vol = prev_vol * (comp["median"] - ch_data["rate"])

                # Cascade through remaining stages
                cascade_rate = 1.0
                for remaining_idx in range(stage_idx + 1, len(FUNNEL_STAGES)):
                    remaining_data = ch_funnel["stages"][remaining_idx]
                    if remaining_data["conversion_rate"]:
                        cascade_rate *= remaining_data["conversion_rate"]

                additional_conversions = additional_vol * cascade_rate
                additional_revenue = additional_conversions * avg_rev_per_conv

                if additional_revenue > 1000:
                    impacts.append({
                        "channel": ch_data["channel"],
                        "stage": comp["stage_label"],
                        "current_rate": round(ch_data["rate"], 4),
                        "target_rate": round(comp["median"], 4),
                        "additional_conversions": round(additional_conversions, 0),
                        "additional_revenue": round(additional_revenue, 0),
                    })

    return {
        "impacts": sorted(impacts, key=lambda x: x["additional_revenue"], reverse=True),
        "total_addressable": round(sum(i["additional_revenue"] for i in impacts), 0),
        "avg_revenue_per_conversion": round(avg_rev_per_conv, 0),
    }


def _get_bottleneck_recommendation(stage: str, actual: float, benchmark: float) -> str:
    recs = {
        "clicks": "Review ad copy, targeting, and creative. Test new ad formats. Check keyword relevance.",
        "leads": "Optimize landing pages. Simplify forms. Test value propositions. Review CTA placement.",
        "mqls": "Review lead scoring criteria. Improve nurture sequences. Check content relevance at this stage.",
        "sqls": "Align marketing-sales handoff. Review qualification criteria. Check lead routing and response time.",
        "conversions": "Audit sales process. Review pricing and objection handling. Check competitive positioning.",
    }
    return recs.get(stage, f"Investigate {stage} conversion drop-off.")


def run_full_funnel_analysis(df: pd.DataFrame) -> Dict:
    """Run all funnel analyses and return combined results."""
    overall = compute_funnel(df)
    by_channel = compute_funnel(df, group_by="channel")
    bottlenecks = identify_bottlenecks(overall)
    comparison = channel_funnel_comparison(df)
    impact = funnel_revenue_impact(df)

    return {
        "overall_funnel": overall[0] if overall else {},
        "channel_funnels": by_channel,
        "bottlenecks": bottlenecks,
        "channel_comparison": comparison,
        "revenue_impact": impact,
    }


if __name__ == "__main__":
    from mock_data import generate_all_data

    data = generate_all_data()
    df = data["campaign_performance"]

    results = run_full_funnel_analysis(df)

    print("=== Overall Funnel ===")
    for s in results["overall_funnel"]["stages"]:
        rate_str = f"{s['conversion_rate']:.1%}" if s["conversion_rate"] else "—"
        drop_str = f"{s['drop_off_rate']:.1%}" if s["drop_off_rate"] else "—"
        print(f"  {s['stage']}: {s['volume']:,} (conv: {rate_str}, drop: {drop_str})")

    print(f"\n=== Bottlenecks ({len(results['bottlenecks'])}) ===")
    for b in results["bottlenecks"]:
        print(f"  [{b['severity']}] {b['from_stage']}→{b['stage']}: "
              f"{b['actual_rate']:.1%} vs {b['benchmark_rate']:.1%} "
              f"(gap: {b['gap_pct']:.0f}%, lost: {b['lost_volume']:,})")

    print(f"\n=== Revenue Impact ===")
    print(f"  Total addressable: ${results['revenue_impact']['total_addressable']:,.0f}")
    for i in results["revenue_impact"]["impacts"][:5]:
        print(f"  {i['channel']} {i['stage']}: +${i['additional_revenue']:,.0f} "
              f"({i['current_rate']:.1%}→{i['target_rate']:.1%})")
