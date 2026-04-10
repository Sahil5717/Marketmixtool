"""Multi-Objective Optimization (Phase 3) - Pareto-optimal allocation balancing competing goals."""
import numpy as np
from scipy.optimize import minimize
from typing import Dict, List, Optional

def multi_objective_optimize(curves, budget, weights=None, constraints=None, n_solutions=5):
    """Generate Pareto frontier of solutions trading off revenue vs ROI vs cost vs leakage."""
    if weights is None:
        weight_sets = [
            {"name": "Max Revenue", "revenue": .8, "roi": .1, "cost": .05, "leakage": .05},
            {"name": "Balanced Growth", "revenue": .5, "roi": .3, "cost": .1, "leakage": .1},
            {"name": "Balanced", "revenue": .4, "roi": .3, "cost": .15, "leakage": .15},
            {"name": "Efficiency Focus", "revenue": .2, "roi": .5, "cost": .2, "leakage": .1},
            {"name": "Cost Minimizer", "revenue": .15, "roi": .25, "cost": .4, "leakage": .2},
        ]
    else:
        weight_sets = [{"name": "Custom", **weights}]
    
    channels = list(curves.keys()); n = len(channels)
    pred = lambda ch, s: curves[ch].get("a",1) * np.power(max(s/12,1), curves[ch].get("b",.5)) * 12
    cur = {ch: curves[ch].get("avgSpend", curves[ch].get("current_avg_spend", 10000)) * 12 for ch in channels}
    
    solutions = []
    for ws in weight_sets:
        # Greedy optimization with these weights
        al = {ch: budget / n for ch in channels}
        step = budget * .005
        for _ in range(200):
            scores = []
            for ch in channels:
                rev = pred(ch, al[ch])
                roi = (rev - al[ch]) / max(al[ch], 1)
                c = curves[ch]
                marginal = c.get("a",1) * c.get("b",.5) * np.power(max(al[ch]/12,1), c.get("b",.5)-1)
                score = ws.get("revenue",.4)*rev/1e6 + ws.get("roi",.3)*roi + ws.get("cost",.15)*(1-al[ch]/budget) + ws.get("leakage",.15)*marginal
                scores.append({"ch": ch, "score": score, "marginal": marginal})
            scores.sort(key=lambda x: x["score"], reverse=True)
            best, worst = scores[0], scores[-1]
            if al[worst["ch"]] - step < budget * .02 or al[best["ch"]] + step > budget * .4: continue
            al[worst["ch"]] -= step; al[best["ch"]] += step
        
        total_rev = sum(pred(ch, al[ch]) for ch in channels)
        total_roi = (total_rev - budget) / budget
        solutions.append({
            "name": ws["name"], "weights": {k:v for k,v in ws.items() if k!="name"},
            "allocation": {ch: round(al[ch], 0) for ch in channels},
            "total_revenue": round(total_rev, 0), "total_roi": round(total_roi, 3),
            "total_spend": round(budget, 0),
        })
    
    return {"solutions": solutions, "n_channels": n, "budget": round(budget, 0),
            "pareto_frontier": [{"revenue": s["total_revenue"], "roi": s["total_roi"], "name": s["name"]} for s in solutions]}

