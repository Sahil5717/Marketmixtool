"""
Budget Optimization Engine
Constrained optimization that allocates budget across channels to maximize
the selected objective function (revenue, ROI, balanced).

Uses scipy.optimize.minimize with SLSQP solver for constrained optimization.
Response curves from the response_curves engine define the spend-return relationship.
"""

import numpy as np
from scipy.optimize import minimize
from typing import Dict, List, Optional, Tuple
import json


def optimize_budget(
    response_curves: Dict[str, Dict],
    total_budget: float,
    objective: str = "balanced",
    objective_weights: Optional[Dict[str, float]] = None,
    min_spend_pct: float = 0.02,
    max_spend_pct: float = 0.40,
    locked_channels: Optional[Dict[str, float]] = None,
    current_allocation: Optional[Dict[str, float]] = None,
) -> Dict:
    """
    Optimize budget allocation across channels.
    
    Args:
        response_curves: Fitted curves from response_curves engine
        total_budget: Total annual budget to allocate
        objective: "maximize_revenue", "maximize_roi", "minimize_cac", "balanced"
        objective_weights: For balanced objective {revenue: 0.4, roi: 0.3, leakage: 0.15, cost: 0.15}
        min_spend_pct: Minimum % of budget per channel
        max_spend_pct: Maximum % of budget per channel
        locked_channels: {channel: fixed_spend} for channels that can't be changed
        current_allocation: Current spend per channel (for comparison)
    
    Returns:
        Optimization results with recommended allocation, projected outcomes, rationale
    """
    channels = [ch for ch in response_curves.keys() if ch not in (locked_channels or {})]
    n = len(channels)
    
    if n == 0:
        return {"error": "No channels available for optimization"}
    
    locked = locked_channels or {}
    locked_total = sum(locked.values())
    available_budget = total_budget - locked_total
    
    if available_budget <= 0:
        return {"error": "Locked channel spend exceeds total budget"}
    
    # Default weights for balanced objective
    if objective_weights is None:
        objective_weights = {"revenue": 0.4, "roi": 0.3, "leakage": 0.15, "cost": 0.15}
    
    # Current allocation for comparison
    if current_allocation is None:
        current_allocation = {
            ch: info["current_avg_spend"] * 12
            for ch, info in response_curves.items()
        }
    
    def _predicted_revenue(spend: float, curve: Dict) -> float:
        """Predict revenue given annual spend using response curve."""
        monthly = spend / 12
        if curve["model"] == "power_law":
            a, b = curve["params"]["a"], curve["params"]["b"]
            return float(a * np.power(max(monthly, 1), b) * 12)
        elif curve["model"] == "hill":
            a, b, K = curve["params"]["a"], curve["params"]["b"], curve["params"]["K"]
            xb = np.power(max(monthly, 1), b)
            Kb = np.power(K, b)
            return float(a * xb / (Kb + xb) * 12)
        else:
            return float(curve["params"]["slope"] * monthly * 12)
    
    def _objective_function(x):
        """Negative of objective (we minimize, so negate to maximize)."""
        allocation = dict(zip(channels, x))
        # Add locked channels
        for ch, spend in locked.items():
            allocation[ch] = spend
        
        total_revenue = sum(
            _predicted_revenue(allocation[ch], response_curves[ch])
            for ch in allocation if ch in response_curves
        )
        total_spend = sum(allocation.values())
        
        if objective == "maximize_revenue":
            return -total_revenue
        
        elif objective == "maximize_roi":
            roi = (total_revenue - total_spend) / total_spend if total_spend > 0 else 0
            return -roi
        
        elif objective == "minimize_cac":
            # Estimate conversions from revenue / avg AOV
            avg_aov = 1800
            conversions = total_revenue / avg_aov
            cac = total_spend / conversions if conversions > 0 else float("inf")
            return cac
        
        elif objective == "balanced":
            # Current baseline
            current_rev = sum(
                _predicted_revenue(current_allocation.get(ch, 0), response_curves[ch])
                for ch in response_curves
            )
            current_spend = sum(current_allocation.values())
            
            rev_gain = (total_revenue - current_rev) / current_rev if current_rev > 0 else 0
            roi_val = (total_revenue - total_spend) / total_spend if total_spend > 0 else 0
            current_roi = (current_rev - current_spend) / current_spend if current_spend > 0 else 0
            roi_improvement = roi_val - current_roi
            
            # Leakage reduction (how much closer to optimal we are)
            leakage_reduction = max(0, rev_gain)
            
            # Cost efficiency
            cost_reduction = max(0, (current_spend - total_spend) / current_spend) if current_spend > 0 else 0
            
            w = objective_weights
            score = (
                w.get("revenue", 0.4) * rev_gain +
                w.get("roi", 0.3) * roi_improvement +
                w.get("leakage", 0.15) * leakage_reduction +
                w.get("cost", 0.15) * cost_reduction
            )
            return -score
        
        return -total_revenue
    
    # Bounds: min and max spend per channel
    bounds = [(available_budget * min_spend_pct, available_budget * max_spend_pct)] * n
    
    # Constraint: total allocation equals available budget
    constraints = [
        {"type": "eq", "fun": lambda x: np.sum(x) - available_budget}
    ]
    
    # Initial guess: equal allocation
    x0 = np.ones(n) * (available_budget / n)
    
    # Run optimizer
    result = minimize(
        _objective_function,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000, "ftol": 1e-10},
    )
    
    if not result.success:
        # Fallback: try with relaxed constraints
        result = minimize(
            _objective_function,
            x0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 5000, "ftol": 1e-8},
        )
    
    # Build results
    optimized_allocation = dict(zip(channels, result.x))
    for ch, spend in locked.items():
        optimized_allocation[ch] = spend
    
    # Calculate metrics for optimized vs current
    channel_results = []
    for ch in response_curves:
        opt_spend = optimized_allocation.get(ch, 0)
        cur_spend = current_allocation.get(ch, 0)
        opt_revenue = _predicted_revenue(opt_spend, response_curves[ch])
        cur_revenue = _predicted_revenue(cur_spend, response_curves[ch])
        
        opt_roi = (opt_revenue - opt_spend) / opt_spend if opt_spend > 0 else 0
        cur_roi = (cur_revenue - cur_spend) / cur_spend if cur_spend > 0 else 0
        
        # Marginal ROI at optimized spend
        curve = response_curves[ch]
        monthly_opt = opt_spend / 12
        if curve["model"] == "power_law":
            a, b = curve["params"]["a"], curve["params"]["b"]
            marginal = a * b * np.power(max(monthly_opt, 1), b - 1)
        elif curve["model"] == "hill":
            a, b, K = curve["params"]["a"], curve["params"]["b"], curve["params"]["K"]
            Kb = K ** b
            xb = max(monthly_opt, 1) ** b
            marginal = a * b * (max(monthly_opt, 1) ** (b - 1)) * Kb / ((Kb + xb) ** 2)
        else:
            marginal = curve["params"]["slope"]
        
        channel_results.append({
            "channel": ch,
            "current_spend": round(cur_spend, 2),
            "optimized_spend": round(opt_spend, 2),
            "change_pct": round((opt_spend - cur_spend) / cur_spend * 100, 1) if cur_spend > 0 else 0,
            "current_revenue": round(cur_revenue, 2),
            "optimized_revenue": round(opt_revenue, 2),
            "revenue_change": round(opt_revenue - cur_revenue, 2),
            "current_roi": round(cur_roi, 3),
            "optimized_roi": round(opt_roi, 3),
            "marginal_roi_at_optimized": round(float(marginal), 3),
            "confidence": response_curves[ch].get("r_squared", 0),
            "is_locked": ch in locked,
        })
    
    total_opt_revenue = sum(r["optimized_revenue"] for r in channel_results)
    total_cur_revenue = sum(r["current_revenue"] for r in channel_results)
    total_opt_spend = sum(r["optimized_spend"] for r in channel_results)
    total_cur_spend = sum(r["current_spend"] for r in channel_results)
    
    return {
        "success": result.success,
        "objective": objective,
        "objective_weights": objective_weights,
        "total_budget": total_budget,
        "channel_results": channel_results,
        "summary": {
            "current_total_spend": round(total_cur_spend, 2),
            "optimized_total_spend": round(total_opt_spend, 2),
            "current_total_revenue": round(total_cur_revenue, 2),
            "optimized_total_revenue": round(total_opt_revenue, 2),
            "revenue_uplift": round(total_opt_revenue - total_cur_revenue, 2),
            "revenue_uplift_pct": round(
                (total_opt_revenue - total_cur_revenue) / total_cur_revenue * 100, 1
            ) if total_cur_revenue > 0 else 0,
            "current_overall_roi": round(
                (total_cur_revenue - total_cur_spend) / total_cur_spend, 3
            ) if total_cur_spend > 0 else 0,
            "optimized_overall_roi": round(
                (total_opt_revenue - total_opt_spend) / total_opt_spend, 3
            ) if total_opt_spend > 0 else 0,
        },
        "rationale": _generate_rationale(channel_results, objective),
    }


def sensitivity_analysis(
    response_curves: Dict[str, Dict],
    base_budget: float,
    budget_variations: List[float] = None,
    objective: str = "balanced",
) -> List[Dict]:
    """
    Run optimization at different budget levels to show sensitivity.
    """
    if budget_variations is None:
        budget_variations = [-0.20, -0.10, 0.0, 0.10, 0.20, 0.50]
    
    results = []
    for var in budget_variations:
        budget = base_budget * (1 + var)
        opt = optimize_budget(response_curves, budget, objective=objective)
        
        results.append({
            "budget_change_pct": round(var * 100, 0),
            "total_budget": round(budget, 0),
            "projected_revenue": opt["summary"]["optimized_total_revenue"],
            "projected_roi": opt["summary"]["optimized_overall_roi"],
            "revenue_vs_base": round(
                opt["summary"]["optimized_total_revenue"] - results[0]["projected_revenue"], 2
            ) if results else 0,
        })
    
    return results


def _generate_rationale(channel_results: List[Dict], objective: str) -> List[str]:
    """Generate human-readable rationale for optimization decisions."""
    rationale = []
    
    increases = [r for r in channel_results if r["change_pct"] > 5]
    decreases = [r for r in channel_results if r["change_pct"] < -5]
    
    increases.sort(key=lambda r: r["change_pct"], reverse=True)
    decreases.sort(key=lambda r: r["change_pct"])
    
    for r in increases[:3]:
        rationale.append(
            f"INCREASE {r['channel']} by {r['change_pct']:+.0f}%: "
            f"Marginal ROI of {r['marginal_roi_at_optimized']:.2f} indicates headroom. "
            f"Expected revenue gain: ${r['revenue_change']:,.0f}."
        )
    
    for r in decreases[:3]:
        rationale.append(
            f"REDUCE {r['channel']} by {abs(r['change_pct']):.0f}%: "
            f"Diminishing returns at current spend (marginal ROI {r['marginal_roi_at_optimized']:.2f}). "
            f"Reallocating to higher-return channels."
        )
    
    return rationale


if __name__ == "__main__":
    from mock_data import generate_all_data
    from response_curves import fit_response_curves
    
    data = generate_all_data()
    curves = fit_response_curves(data["campaign_performance"])
    
    # Get current total spend
    current_spend = data["campaign_performance"]["spend"].sum()
    
    print(f"\n=== Optimizing ${current_spend:,.0f} budget ===")
    
    for obj in ["maximize_revenue", "maximize_roi", "balanced"]:
        result = optimize_budget(curves, current_spend, objective=obj)
        print(f"\n--- {obj.upper()} ---")
        print(f"Revenue uplift: {result['summary']['revenue_uplift_pct']:+.1f}%")
        print(f"ROI: {result['summary']['current_overall_roi']:.2f} → {result['summary']['optimized_overall_roi']:.2f}")
        for r in result["rationale"]:
            print(f"  {r}")
    
    print("\n=== Sensitivity Analysis ===")
    sens = sensitivity_analysis(curves, current_spend)
    for s in sens:
        print(f"  Budget {s['budget_change_pct']:+.0f}%: "
              f"${s['total_budget']:,.0f} → Revenue ${s['projected_revenue']:,.0f}, "
              f"ROI {s['projected_roi']:.2f}")
