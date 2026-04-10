"""
Markov Chain Attribution (Phase 2)
Probabilistic multi-touch attribution using channel transition matrices.

Method:
1. Build transition probability matrix from journey data
2. Calculate conversion probability with all channels
3. Remove each channel and recalculate (removal effect)
4. Attribution = removal effect / sum(all removal effects) × total revenue
"""

import numpy as np
import pandas as pd
from typing import Dict, List
from itertools import combinations


def build_transition_matrix(journeys: List[Dict]) -> Dict:
    """
    Build channel-to-channel transition probability matrix from journey data.
    States: start → channels → conversion / null
    """
    states = set()
    transitions = {}
    
    for j in journeys:
        # Build path: start → ch1 → ch2 → ... → conversion/null
        path = ["start"]
        tps = sorted(j["tps"], key=lambda x: x.get("o", x.get("order", 0)))
        for tp in tps:
            ch = tp.get("ch", tp.get("channel", ""))
            if ch:
                path.append(ch)
                states.add(ch)
        
        end_state = "conversion" if j.get("cv", j.get("converted", False)) else "null"
        path.append(end_state)
        
        # Count transitions
        for i in range(len(path) - 1):
            from_state = path[i]
            to_state = path[i + 1]
            if from_state not in transitions:
                transitions[from_state] = {}
            transitions[from_state][to_state] = transitions[from_state].get(to_state, 0) + 1
    
    # Convert counts to probabilities
    prob_matrix = {}
    for from_state, to_states in transitions.items():
        total = sum(to_states.values())
        prob_matrix[from_state] = {
            to: count / total for to, count in to_states.items()
        }
    
    all_states = sorted(states) + ["conversion", "null"]
    
    return {
        "matrix": prob_matrix,
        "channels": sorted(states),
        "all_states": ["start"] + all_states,
        "n_journeys": len(journeys),
        "n_converted": sum(1 for j in journeys if j.get("cv", j.get("converted", False))),
    }


def calculate_conversion_probability(
    prob_matrix: Dict,
    channels: List[str],
    max_steps: int = 100,
) -> float:
    """
    Calculate total conversion probability by simulating Markov chain
    until absorption (conversion or null).
    Uses matrix power method for efficiency.
    """
    all_states = ["start"] + channels + ["conversion", "null"]
    n = len(all_states)
    state_idx = {s: i for i, s in enumerate(all_states)}
    
    # Build transition matrix
    T = np.zeros((n, n))
    for from_state, to_states in prob_matrix.items():
        if from_state not in state_idx:
            continue
        i = state_idx[from_state]
        for to_state, prob in to_states.items():
            if to_state not in state_idx:
                continue
            j = state_idx[to_state]
            T[i, j] = prob
    
    # Make conversion and null absorbing states
    conv_idx = state_idx["conversion"]
    null_idx = state_idx["null"]
    T[conv_idx, :] = 0
    T[conv_idx, conv_idx] = 1
    T[null_idx, :] = 0
    T[null_idx, null_idx] = 1
    
    # Calculate absorption probability starting from "start"
    # Use matrix power to simulate many steps
    state = np.zeros(n)
    state[state_idx["start"]] = 1.0
    
    for _ in range(max_steps):
        state = state @ T
        # Check convergence
        if state[conv_idx] + state[null_idx] > 0.999:
            break
    
    return float(state[conv_idx])


def removal_effect(
    prob_matrix: Dict,
    channels: List[str],
    channel_to_remove: str,
) -> float:
    """
    Calculate conversion probability after removing a channel.
    Removing = redirecting all transitions to/from that channel to "null".
    """
    modified_matrix = {}
    
    for from_state, to_states in prob_matrix.items():
        if from_state == channel_to_remove:
            # This channel redirects everything to null
            modified_matrix[from_state] = {"null": 1.0}
            continue
        
        new_to = {}
        removed_prob = to_states.get(channel_to_remove, 0)
        
        for to_state, prob in to_states.items():
            if to_state == channel_to_remove:
                continue  # Skip transitions TO removed channel
            new_to[to_state] = prob
        
        # Redistribute removed probability to null
        if removed_prob > 0:
            new_to["null"] = new_to.get("null", 0) + removed_prob
        
        # Renormalize
        total = sum(new_to.values())
        if total > 0:
            new_to = {k: v / total for k, v in new_to.items()}
        
        modified_matrix[from_state] = new_to
    
    remaining_channels = [ch for ch in channels if ch != channel_to_remove]
    return calculate_conversion_probability(modified_matrix, remaining_channels)


def markov_attribution(journeys: List[Dict]) -> Dict:
    """
    Full Markov chain attribution pipeline.
    Returns channel-level attributed revenue with removal effects.
    """
    # Build transition matrix
    tm = build_transition_matrix(journeys)
    channels = tm["channels"]
    matrix = tm["matrix"]
    
    # Calculate base conversion probability
    base_prob = calculate_conversion_probability(matrix, channels)
    
    # Calculate removal effect for each channel
    removal_effects = {}
    for ch in channels:
        removed_prob = removal_effect(matrix, channels, ch)
        effect = max(0, base_prob - removed_prob)
        removal_effects[ch] = {
            "base_probability": round(base_prob, 4),
            "removed_probability": round(removed_prob, 4),
            "removal_effect": round(effect, 4),
        }
    
    # Normalize removal effects to get attribution weights
    total_effect = sum(r["removal_effect"] for r in removal_effects.values())
    
    # Calculate total revenue from converted journeys
    total_revenue = sum(
        j.get("rv", j.get("revenue", 0))
        for j in journeys
        if j.get("cv", j.get("converted", False))
    )
    
    # Distribute revenue
    results = {}
    for ch in channels:
        weight = removal_effects[ch]["removal_effect"] / total_effect if total_effect > 0 else 1 / len(channels)
        results[ch] = {
            **removal_effects[ch],
            "attribution_weight": round(weight, 4),
            "attributed_revenue": round(total_revenue * weight, 0),
            "attributed_pct": round(weight * 100, 1),
        }
    
    # Transition probabilities for visualization
    top_transitions = []
    for from_state, to_states in matrix.items():
        if from_state in ["conversion", "null"]:
            continue
        for to_state, prob in sorted(to_states.items(), key=lambda x: -x[1])[:3]:
            if prob > 0.05:
                top_transitions.append({
                    "from": from_state,
                    "to": to_state,
                    "probability": round(prob, 3),
                })
    
    return {
        "channel_attribution": results,
        "base_conversion_probability": round(base_prob, 4),
        "total_revenue_attributed": round(total_revenue, 0),
        "n_journeys": tm["n_journeys"],
        "n_converted": tm["n_converted"],
        "conversion_rate": round(tm["n_converted"] / max(tm["n_journeys"], 1), 4),
        "top_transitions": sorted(top_transitions, key=lambda x: -x["probability"])[:20],
        "model": "markov_chain_removal_effect",
    }


if __name__ == "__main__":
    from mock_data import generate_all_data
    
    data = generate_all_data()
    journeys = data["user_journeys"]
    
    # Convert journey format
    js = []
    j_groups = {}
    for _, row in journeys.iterrows():
        jid = row["journey_id"]
        if jid not in j_groups:
            j_groups[jid] = {"id": jid, "tps": [], "cv": row["converted"], "rv": 0, "nt": row["total_touchpoints"]}
        j_groups[jid]["tps"].append({"ch": row["channel"], "camp": row["campaign"], "o": row["touchpoint_order"]})
        if row["conversion_revenue"] > 0:
            j_groups[jid]["rv"] = row["conversion_revenue"]
    
    js = list(j_groups.values())
    
    print("Running Markov Chain Attribution...")
    result = markov_attribution(js)
    
    print(f"\nBase conversion probability: {result['base_conversion_probability']:.2%}")
    print(f"Journeys: {result['n_journeys']} ({result['n_converted']} converted)")
    
    print("\nChannel Attribution:")
    sorted_ch = sorted(result["channel_attribution"].items(), key=lambda x: -x[1]["attributed_revenue"])
    for ch, info in sorted_ch:
        print(f"  {ch}: ${info['attributed_revenue']:,.0f} ({info['attributed_pct']:.1f}%) "
              f"weight={info['attribution_weight']:.3f} "
              f"removal_effect={info['removal_effect']:.4f}")
    
    print("\nTop Transitions:")
    for t in result["top_transitions"][:10]:
        print(f"  {t['from']} → {t['to']}: {t['probability']:.1%}")
