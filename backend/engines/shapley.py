"""Shapley Value Attribution (Phase 3) - Monte Carlo sampling approach."""
import numpy as np
import random
from math import factorial
from typing import Dict, List

def run_shapley(df, curves, n_samples=500, seed=42):
    """Compute Shapley values using response curves and Monte Carlo sampling."""
    random.seed(seed); np.random.seed(seed)
    ch_col = "channel" if "channel" in df.columns else "ch"
    channels = sorted(df[ch_col].unique())
    ch_spend = {}
    for ch in channels:
        ch_spend[ch] = float(df[df[ch_col]==ch]["spend"].sum())
    
    def coalition_value(subset):
        total = 0
        for ch in subset:
            if ch not in curves: continue
            c = curves[ch]
            a = c.get("a", c.get("params",{}).get("a",1))
            b = c.get("b", c.get("params",{}).get("b",0.5))
            s = ch_spend.get(ch, 0)
            rev = a * np.power(max(s/12,1), b) * 12
            synergy = 1 + 0.02 * (len(subset)-1)
            total += rev * synergy
        return total
    
    n = len(channels)
    sv = {ch: 0.0 for ch in channels}
    
    for _ in range(n_samples):
        perm = list(channels)
        random.shuffle(perm)
        prev_val = 0
        current = set()
        for ch in perm:
            current.add(ch)
            val = coalition_value(current)
            sv[ch] += val - prev_val
            prev_val = val
    
    for ch in channels:
        sv[ch] /= n_samples
    
    total = sum(sv.values())
    total_rev = float(df["revenue"].sum() if "revenue" in df.columns else df["rev"].sum())
    
    if total > 0:
        scale = total_rev / total
        sv = {ch: v * scale for ch, v in sv.items()}
    
    results = {}
    for ch in channels:
        results[ch] = {
            "shapley_value": round(sv[ch], 0),
            "shapley_pct": round(sv[ch]/total_rev*100, 1) if total_rev > 0 else 0,
            "spend": round(ch_spend.get(ch,0), 0),
            "shapley_roas": round(sv[ch]/max(ch_spend.get(ch,0),1), 2),
        }
    
    return {
        "shapley_values": dict(sorted(results.items(), key=lambda x: -x[1]["shapley_value"])),
        "total_revenue": round(total_rev, 0),
        "n_channels": n,
        "n_samples": n_samples,
        "model": "monte_carlo_shapley",
    }
