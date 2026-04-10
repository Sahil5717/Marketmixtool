"""
ROI Formula Engine (Phase 1)
Implements all 5 ROI calculations from the blueprint:
1. Base ROI = (Revenue - Cost) / Cost
2. Gross Margin ROI = (Gross Margin - Cost) / Cost
3. ROAS = Revenue / Ad Spend
4. Incremental ROI = (Incremental Revenue - Incremental Cost) / Incremental Cost
5. Marginal ROI = Delta Revenue / Delta Spend (from response curves)

Plus: campaign-level marginal ROI using response curve derivatives.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


DEFAULT_GROSS_MARGIN_PCT = 0.65  # 65% gross margin assumption


def compute_all_roi_formulas(
    df: pd.DataFrame,
    gross_margin_pct: float = DEFAULT_GROSS_MARGIN_PCT,
    group_by: str = "channel",
) -> pd.DataFrame:
    """
    Compute all 5 ROI formulas at the specified grouping level.
    """
    grouped = df.groupby(group_by).agg(
        total_spend=("spend", "sum"),
        total_revenue=("revenue", "sum"),
        total_conversions=("conversions", "sum"),
        total_clicks=("clicks", "sum"),
        total_impressions=("impressions", "sum"),
        total_leads=("leads", "sum"),
    ).reset_index()

    # 1. Base ROI
    grouped["base_roi"] = (grouped["total_revenue"] - grouped["total_spend"]) / grouped["total_spend"].clip(lower=1)

    # 2. Gross Margin ROI
    grouped["gross_margin"] = grouped["total_revenue"] * gross_margin_pct
    grouped["gross_margin_roi"] = (grouped["gross_margin"] - grouped["total_spend"]) / grouped["total_spend"].clip(lower=1)

    # 3. ROAS
    grouped["roas"] = grouped["total_revenue"] / grouped["total_spend"].clip(lower=1)

    # 4. Incremental ROI (comparing to baseline period)
    # Use first quarter as baseline, rest as incremental
    baseline = df[df["month"] <= df["month"].unique()[2]]  # First 3 months
    incremental = df[df["month"] > df["month"].unique()[2]]  # Remaining months

    if len(baseline) > 0 and len(incremental) > 0:
        bl_grouped = baseline.groupby(group_by).agg(
            bl_spend=("spend", "sum"),
            bl_revenue=("revenue", "sum"),
        ).reset_index()
        inc_grouped = incremental.groupby(group_by).agg(
            inc_spend=("spend", "sum"),
            inc_revenue=("revenue", "sum"),
        ).reset_index()

        merged = bl_grouped.merge(inc_grouped, on=group_by, how="outer").fillna(0)
        # Normalize to per-month
        bl_months = baseline["month"].nunique()
        inc_months = incremental["month"].nunique()
        merged["bl_spend_monthly"] = merged["bl_spend"] / max(bl_months, 1)
        merged["bl_revenue_monthly"] = merged["bl_revenue"] / max(bl_months, 1)
        merged["inc_spend_monthly"] = merged["inc_spend"] / max(inc_months, 1)
        merged["inc_revenue_monthly"] = merged["inc_revenue"] / max(inc_months, 1)

        merged["incremental_spend"] = merged["inc_spend_monthly"] - merged["bl_spend_monthly"]
        merged["incremental_revenue"] = merged["inc_revenue_monthly"] - merged["bl_revenue_monthly"]
        merged["incremental_roi"] = np.where(
            merged["incremental_spend"] > 0,
            (merged["incremental_revenue"] - merged["incremental_spend"]) / merged["incremental_spend"],
            0
        )

        grouped = grouped.merge(
            merged[[group_by, "incremental_roi", "incremental_spend", "incremental_revenue"]],
            on=group_by, how="left"
        )
    else:
        grouped["incremental_roi"] = 0
        grouped["incremental_spend"] = 0
        grouped["incremental_revenue"] = 0

    # Additional useful metrics
    grouped["cac"] = grouped["total_spend"] / grouped["total_conversions"].clip(lower=1)
    grouped["cpl"] = grouped["total_spend"] / grouped["total_leads"].clip(lower=1)
    grouped["ctr"] = grouped["total_clicks"] / grouped["total_impressions"].clip(lower=1)
    grouped["cvr"] = grouped["total_conversions"] / grouped["total_clicks"].clip(lower=1)

    return grouped


def compute_marginal_roi_by_campaign(
    df: pd.DataFrame,
    response_curves: Dict[str, Dict],
) -> pd.DataFrame:
    """
    Compute marginal ROI at the campaign level using channel response curves.
    Campaign marginal ROI = channel marginal ROI adjusted by campaign share.
    """
    # Get campaign spend
    camp_spend = df.groupby(["channel", "campaign"]).agg(
        spend=("spend", "sum"),
        revenue=("revenue", "sum"),
    ).reset_index()

    # Channel total spend
    ch_spend = df.groupby("channel")["spend"].sum()

    results = []
    for _, row in camp_spend.iterrows():
        ch = row["channel"]
        if ch not in response_curves:
            continue

        curve = response_curves[ch]
        # Campaign share of channel spend
        ch_total = ch_spend.get(ch, 1)
        camp_share = row["spend"] / ch_total if ch_total > 0 else 0

        # Channel-level marginal ROI at current spend
        a = curve.get("a", 1)
        b = curve.get("b", 0.5)
        if "params" in curve:
            a = curve["params"].get("a", a)
            b = curve["params"].get("b", b)

        monthly_spend = ch_total / 12
        channel_marginal = a * b * np.power(max(monthly_spend, 1), b - 1)

        # Campaign marginal is approximated as channel marginal
        # adjusted by campaign efficiency relative to channel average
        camp_roi = (row["revenue"] - row["spend"]) / max(row["spend"], 1)
        ch_avg_roi = (camp_spend[camp_spend["channel"] == ch]["revenue"].sum() -
                      camp_spend[camp_spend["channel"] == ch]["spend"].sum()) / max(ch_total, 1)

        efficiency_factor = camp_roi / max(ch_avg_roi, 0.01) if ch_avg_roi > 0 else 1
        efficiency_factor = np.clip(efficiency_factor, 0.1, 5.0)

        campaign_marginal = channel_marginal * efficiency_factor

        headroom = curve.get("headroom_pct", curve.get("hd", 50))

        results.append({
            "channel": ch,
            "campaign": row["campaign"],
            "spend": round(row["spend"], 0),
            "revenue": round(row["revenue"], 0),
            "base_roi": round(camp_roi, 2),
            "channel_marginal_roi": round(float(channel_marginal), 3),
            "campaign_marginal_roi": round(float(campaign_marginal), 3),
            "efficiency_factor": round(float(efficiency_factor), 2),
            "headroom_pct": round(float(headroom), 1),
            "recommendation": _marginal_recommendation(campaign_marginal, headroom),
        })

    return pd.DataFrame(results).sort_values("campaign_marginal_roi", ascending=False)


def compute_payback_period(
    df: pd.DataFrame,
    group_by: str = "channel",
) -> pd.DataFrame:
    """
    Estimate payback period: how many months until cumulative revenue
    exceeds cumulative spend for each channel.
    """
    results = []

    for group in df[group_by].unique():
        g_data = df[df[group_by] == group].sort_values("month")
        monthly = g_data.groupby("month").agg(
            spend=("spend", "sum"),
            revenue=("revenue", "sum"),
        ).reset_index()

        cum_spend = 0
        cum_revenue = 0
        payback_month = None

        for i, row in monthly.iterrows():
            cum_spend += row["spend"]
            cum_revenue += row["revenue"]
            if cum_revenue >= cum_spend and payback_month is None:
                payback_month = i + 1

        results.append({
            group_by: group,
            "payback_months": payback_month or len(monthly),
            "total_spend": round(cum_spend, 0),
            "total_revenue": round(cum_revenue, 0),
            "cumulative_roi": round((cum_revenue - cum_spend) / max(cum_spend, 1), 2),
            "profitable": cum_revenue > cum_spend,
        })

    return pd.DataFrame(results).sort_values("payback_months")


def _marginal_recommendation(marginal_roi: float, headroom: float) -> str:
    if marginal_roi > 2.0 and headroom > 20:
        return "Scale: high marginal returns with headroom"
    elif marginal_roi > 1.5:
        return "Monitor: good returns but watch for saturation"
    elif marginal_roi > 1.0:
        return "Hold: marginal returns above breakeven"
    elif marginal_roi > 0.5:
        return "Review: approaching diminishing returns"
    else:
        return "Reduce: below marginal efficiency threshold"


def run_full_roi_analysis(
    df: pd.DataFrame,
    response_curves: Dict = None,
    gross_margin_pct: float = DEFAULT_GROSS_MARGIN_PCT,
) -> Dict:
    """Run all ROI analyses and return combined results."""
    # Channel level
    channel_roi = compute_all_roi_formulas(df, gross_margin_pct, "channel")

    # Campaign level
    campaign_roi = compute_all_roi_formulas(df, gross_margin_pct, "campaign")

    # Marginal ROI by campaign
    marginal = None
    if response_curves:
        marginal = compute_marginal_roi_by_campaign(df, response_curves)

    # Payback period
    payback = compute_payback_period(df)

    return {
        "channel_roi": channel_roi.to_dict(orient="records"),
        "campaign_roi": campaign_roi.to_dict(orient="records"),
        "marginal_roi_by_campaign": marginal.to_dict(orient="records") if marginal is not None else [],
        "payback_periods": payback.to_dict(orient="records"),
        "roi_formulas": {
            "base_roi": "Base ROI = (Revenue - Marketing Cost) / Marketing Cost",
            "gross_margin_roi": f"Gross Margin ROI = (Revenue × {gross_margin_pct:.0%} - Cost) / Cost",
            "roas": "ROAS = Attributed Revenue / Ad Spend",
            "incremental_roi": "Incremental ROI = (ΔRevenue - ΔSpend) / ΔSpend (vs baseline period)",
            "marginal_roi": "Marginal ROI = dRevenue/dSpend (response curve derivative at current spend)",
        },
    }


if __name__ == "__main__":
    from mock_data import generate_all_data
    from response_curves import fit_response_curves

    data = generate_all_data()
    df = data["campaign_performance"]
    curves = fit_response_curves(df)

    results = run_full_roi_analysis(df, curves)

    print("=== Channel ROI (All 5 Formulas) ===")
    for r in results["channel_roi"]:
        print(f"  {r['channel']}:")
        print(f"    Base ROI:     {r['base_roi']:.2f}x")
        print(f"    GM ROI:       {r['gross_margin_roi']:.2f}x")
        print(f"    ROAS:         {r['roas']:.2f}x")
        print(f"    Incremental:  {r['incremental_roi']:.2f}x")

    print(f"\n=== Marginal ROI by Campaign (top 5) ===")
    for r in results["marginal_roi_by_campaign"][:5]:
        print(f"  {r['channel']}/{r['campaign']}: "
              f"marginal={r['campaign_marginal_roi']:.2f}x "
              f"headroom={r['headroom_pct']:.0f}% "
              f"→ {r['recommendation']}")

    print(f"\n=== Payback Periods ===")
    for r in results["payback_periods"]:
        print(f"  {r['channel']}: {r['payback_months']} months "
              f"(cum ROI: {r['cumulative_roi']:.2f}x)")
