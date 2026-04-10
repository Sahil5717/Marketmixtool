"""
FastAPI Backend for Marketing ROI & Budget Optimization Engine
Serves all engine outputs as REST endpoints.

Run: uvicorn api:app --reload --port 8000
"""

import os
import sys
import json
import tempfile
from typing import Optional, Dict, List
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pandas as pd
import numpy as np

# Add parent dir for imports
sys.path.insert(0, os.path.dirname(__file__))

from mock_data import generate_all_data, export_to_csv
from validator import validate_data
from engines.attribution import run_all_attribution, compute_attribution_roi
from engines.response_curves import fit_response_curves, get_marginal_roi_table
from engines.optimizer import optimize_budget, sensitivity_analysis
from engines.diagnostics import run_diagnostics
from engines.leakage import calculate_all_pillars
from engines.trend_analysis import run_full_trend_analysis
from engines.funnel_analysis import run_full_funnel_analysis
from engines.roi_formulas import run_full_roi_analysis
from engines.adstock import compute_channel_adstock
from engines.mmm import run_mmm
from engines.markov_attribution import markov_attribution
from engines.forecasting import run_full_forecast
from engines.cross_channel import run_cross_channel_analysis
from engines.shapley import run_shapley
from engines.multi_objective import multi_objective_optimize
from engines.geo_lift import design_geo_test
from engines.hierarchical_forecast import hierarchical_forecast
from engines.automated_recs import automated_recommendations, check_model_drift, track_realization

app = FastAPI(
    title="Marketing ROI & Budget Optimization Engine",
    version="1.0.0",
    description="Omnichannel Performance Measurement | Diagnostic Intelligence | Forward Optimization",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- In-memory state ---
_state: Dict = {
    "campaign_data": None,
    "journey_data": None,
    "validation": None,
    "curves": None,
    "attribution": None,
    "attribution_roi": None,
    "optimization": None,
    "diagnostics": None,
    "pillars": None,
    "trend_analysis": None,
    "funnel_analysis": None,
    "roi_analysis": None,
}


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        return super().default(obj)


def _jsonify(obj):
    return json.loads(json.dumps(obj, cls=NumpyEncoder))


# --- Endpoints ---

@app.get("/")
def root():
    return {"status": "ok", "engine": "Marketing ROI & Budget Optimization Engine v1.0"}


@app.post("/api/load-mock-data")
def load_mock_data():
    """Load pre-generated mock data for demo purposes."""
    data = generate_all_data()
    _state["campaign_data"] = data["campaign_performance"]
    _state["journey_data"] = data["user_journeys"]
    
    # Run validation
    _state["validation"] = validate_data(_state["campaign_data"])
    
    summary = {
        "rows": len(_state["campaign_data"]),
        "journey_rows": len(_state["journey_data"]),
        "channels": int(_state["campaign_data"]["channel"].nunique()),
        "campaigns": int(_state["campaign_data"]["campaign"].nunique()),
        "months": int(_state["campaign_data"]["month"].nunique()),
        "total_spend": float(_state["campaign_data"]["spend"].sum()),
        "total_revenue": float(_state["campaign_data"]["revenue"].sum()),
        "validation": _state["validation"],
    }
    return _jsonify(summary)


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload CSV or Excel file with campaign data."""
    suffix = Path(file.filename).suffix.lower()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        if suffix == ".csv":
            df = pd.read_csv(tmp_path)
        elif suffix in (".xlsx", ".xls"):
            df = pd.read_excel(tmp_path)
        else:
            raise HTTPException(400, f"Unsupported file type: {suffix}")
        
        _state["campaign_data"] = df
        _state["validation"] = validate_data(df)
        
        return _jsonify({
            "filename": file.filename,
            "rows": len(df),
            "columns": list(df.columns),
            "validation": _state["validation"],
        })
    finally:
        os.unlink(tmp_path)


@app.get("/api/validation")
def get_validation():
    if _state["validation"] is None:
        raise HTTPException(400, "No data loaded")
    return _jsonify(_state["validation"])


@app.get("/api/current-state")
def get_current_state(attribution_model: str = "last_touch"):
    """Get current-state KPIs and performance data."""
    if _state["campaign_data"] is None:
        raise HTTPException(400, "No data loaded")
    
    df = _state["campaign_data"]
    
    # Run attribution if not cached
    if _state["attribution"] is None and _state["journey_data"] is not None:
        _state["attribution"] = run_all_attribution(_state["journey_data"])
        _state["attribution_roi"] = compute_attribution_roi(_state["attribution"], df)
    
    # Overall KPIs
    total_spend = float(df["spend"].sum())
    total_revenue = float(df["revenue"].sum())
    total_conversions = int(df["conversions"].sum())
    
    kpis = {
        "total_spend": total_spend,
        "total_revenue": total_revenue,
        "roi": (total_revenue - total_spend) / total_spend if total_spend > 0 else 0,
        "roas": total_revenue / total_spend if total_spend > 0 else 0,
        "total_conversions": total_conversions,
        "cac": total_spend / total_conversions if total_conversions > 0 else 0,
        "avg_conversion_rate": float(df["conversions"].sum() / df["clicks"].sum()) if df["clicks"].sum() > 0 else 0,
    }
    
    # Channel-campaign matrix
    matrix = df.groupby(["channel", "campaign", "channel_type"]).agg(
        spend=("spend", "sum"),
        revenue=("revenue", "sum"),
        impressions=("impressions", "sum"),
        clicks=("clicks", "sum"),
        leads=("leads", "sum"),
        conversions=("conversions", "sum"),
    ).reset_index()
    
    matrix["roi"] = (matrix["revenue"] - matrix["spend"]) / matrix["spend"].clip(lower=1)
    matrix["roas"] = matrix["revenue"] / matrix["spend"].clip(lower=1)
    matrix["ctr"] = matrix["clicks"] / matrix["impressions"].clip(lower=1)
    matrix["cvr"] = matrix["conversions"] / matrix["clicks"].clip(lower=1)
    matrix["cac"] = matrix["spend"] / matrix["conversions"].clip(lower=1)
    
    # Monthly trends
    trends = df.groupby("month").agg(
        spend=("spend", "sum"),
        revenue=("revenue", "sum"),
        conversions=("conversions", "sum"),
    ).reset_index()
    trends["roi"] = (trends["revenue"] - trends["spend"]) / trends["spend"]
    
    # Online vs offline split
    split = df.groupby("channel_type").agg(
        spend=("spend", "sum"),
        revenue=("revenue", "sum"),
    ).reset_index()
    
    # Attribution data
    attr_data = None
    if _state["attribution_roi"] and attribution_model in _state["attribution_roi"]:
        attr_df = _state["attribution_roi"][attribution_model]
        attr_data = attr_df.to_dict(orient="records")
    
    return _jsonify({
        "kpis": kpis,
        "channel_campaign_matrix": matrix.to_dict(orient="records"),
        "monthly_trends": trends.to_dict(orient="records"),
        "online_offline_split": split.to_dict(orient="records"),
        "attribution": attr_data,
        "attribution_model": attribution_model,
    })


@app.get("/api/deep-dive/{channel}")
def get_channel_deep_dive(channel: str):
    """Get deep-dive data for a specific channel."""
    if _state["campaign_data"] is None:
        raise HTTPException(400, "No data loaded")
    
    df = _state["campaign_data"]
    ch_data = df[df["channel"] == channel]
    
    if len(ch_data) == 0:
        raise HTTPException(404, f"Channel '{channel}' not found")
    
    # Monthly trend for this channel
    trend = ch_data.groupby("month").agg(
        spend=("spend", "sum"),
        revenue=("revenue", "sum"),
        conversions=("conversions", "sum"),
        leads=("leads", "sum"),
    ).reset_index()
    trend["roi"] = (trend["revenue"] - trend["spend"]) / trend["spend"]
    
    # Regional breakdown
    regional = ch_data.groupby("region").agg(
        spend=("spend", "sum"),
        revenue=("revenue", "sum"),
        conversions=("conversions", "sum"),
    ).reset_index()
    regional["roi"] = (regional["revenue"] - regional["spend"]) / regional["spend"]
    
    # Funnel
    funnel = {
        "impressions": int(ch_data["impressions"].sum()),
        "clicks": int(ch_data["clicks"].sum()),
        "leads": int(ch_data["leads"].sum()),
        "mqls": int(ch_data["mqls"].sum()),
        "sqls": int(ch_data["sqls"].sum()),
        "conversions": int(ch_data["conversions"].sum()),
    }
    
    # CX signals
    cx = {
        "avg_bounce_rate": float(ch_data["bounce_rate"].mean()),
        "avg_session_duration": float(ch_data["avg_session_duration_sec"].mean()),
        "avg_form_completion": float(ch_data["form_completion_rate"].mean()),
        "avg_nps": float(ch_data["nps_score"].mean()),
    }
    
    # Response curve if available
    curve_data = None
    if _state["curves"] and channel in _state["curves"]:
        curve_data = _state["curves"][channel]
    
    return _jsonify({
        "channel": channel,
        "monthly_trend": trend.to_dict(orient="records"),
        "regional_breakdown": regional.to_dict(orient="records"),
        "funnel": funnel,
        "cx_signals": cx,
        "response_curve": curve_data,
    })


@app.post("/api/run-analysis")
def run_full_analysis():
    """Run all engines: response curves, attribution, optimization, diagnostics, pillars."""
    if _state["campaign_data"] is None:
        raise HTTPException(400, "No data loaded")
    
    df = _state["campaign_data"]
    
    # 1. Response curves
    _state["curves"] = fit_response_curves(df, model_type="power_law")
    
    # 2. Attribution
    if _state["journey_data"] is not None:
        _state["attribution"] = run_all_attribution(_state["journey_data"])
        _state["attribution_roi"] = compute_attribution_roi(_state["attribution"], df)
    
    # 3. Optimization
    total_spend = float(df["spend"].sum())
    _state["optimization"] = optimize_budget(
        _state["curves"], total_spend, objective="balanced"
    )
    
    # 4. Diagnostics
    _state["diagnostics"] = run_diagnostics(
        df, _state["curves"],
        _state["attribution"] or {},
        _state["optimization"],
    )
    
    # 5. Three pillars
    _state["pillars"] = calculate_all_pillars(df, _state["optimization"])
    
    # 6. Trend & Variance Analysis
    _state["trend_analysis"] = run_full_trend_analysis(df)
    
    # 7. Funnel Analysis
    _state["funnel_analysis"] = run_full_funnel_analysis(df)
    
    # 8. Complete ROI Analysis
    _state["roi_analysis"] = run_full_roi_analysis(df, _state["curves"])
    
    return _jsonify({
        "status": "complete",
        "response_curves": {ch: {k: v for k, v in info.items() if k != "monthly_data"}
                           for ch, info in _state["curves"].items()},
        "optimization_summary": _state["optimization"]["summary"],
        "recommendations_count": len(_state["diagnostics"]),
        "total_value_at_risk": _state["pillars"]["total_value_at_risk"],
    })


@app.get("/api/response-curves")
def get_response_curves():
    if _state["curves"] is None:
        raise HTTPException(400, "Run analysis first")
    return _jsonify(_state["curves"])


@app.get("/api/recommendations")
def get_recommendations():
    if _state["diagnostics"] is None:
        raise HTTPException(400, "Run analysis first")
    return _jsonify(_state["diagnostics"])


@app.post("/api/optimize")
def run_optimization(
    total_budget: Optional[float] = None,
    objective: str = "balanced",
):
    """Run or re-run optimization with custom parameters."""
    if _state["curves"] is None:
        raise HTTPException(400, "Run analysis first to fit response curves")
    
    if total_budget is None:
        total_budget = float(_state["campaign_data"]["spend"].sum())
    
    result = optimize_budget(_state["curves"], total_budget, objective=objective)
    _state["optimization"] = result
    
    # Re-run pillars with new optimization
    _state["pillars"] = calculate_all_pillars(_state["campaign_data"], result)
    
    return _jsonify(result)


@app.get("/api/sensitivity")
def get_sensitivity(objective: str = "balanced"):
    if _state["curves"] is None:
        raise HTTPException(400, "Run analysis first")
    
    base_budget = float(_state["campaign_data"]["spend"].sum())
    result = sensitivity_analysis(_state["curves"], base_budget, objective=objective)
    return _jsonify(result)


@app.get("/api/pillars")
def get_pillars():
    if _state["pillars"] is None:
        raise HTTPException(400, "Run analysis first")
    return _jsonify(_state["pillars"])


@app.get("/api/business-case")
def get_business_case():
    """Generate business case summary from all engine outputs."""
    if not all([_state["optimization"], _state["pillars"], _state["diagnostics"]]):
        raise HTTPException(400, "Run full analysis first")
    
    opt = _state["optimization"]
    pillars = _state["pillars"]
    recs = _state["diagnostics"]
    
    return _jsonify({
        "optimization_summary": opt["summary"],
        "rationale": opt.get("rationale", []),
        "value_at_risk": pillars["total_value_at_risk"],
        "correction_potential": pillars["correction_potential"],
        "top_recommendations": recs[:5],
        "implementation_phases": [
            {"phase": "Immediate (0-30 days)", "actions": [r for r in recs if r.get("effort") == "Low"][:3]},
            {"phase": "Short-term (30-90 days)", "actions": [r for r in recs if r.get("effort") == "Medium"][:3]},
            {"phase": "Strategic (90+ days)", "actions": [r for r in recs if r.get("effort") == "High"][:3]},
        ],
    })


@app.get("/api/trend-analysis")
def get_trend_analysis():
    """Get trend & variance analysis results."""
    if _state["trend_analysis"] is None:
        if _state["campaign_data"] is not None:
            _state["trend_analysis"] = run_full_trend_analysis(_state["campaign_data"])
        else:
            raise HTTPException(400, "Run analysis first")
    return _jsonify(_state["trend_analysis"])


@app.get("/api/funnel-analysis")
def get_funnel_analysis():
    """Get funnel conversion analysis with bottleneck detection."""
    if _state["funnel_analysis"] is None:
        if _state["campaign_data"] is not None:
            _state["funnel_analysis"] = run_full_funnel_analysis(_state["campaign_data"])
        else:
            raise HTTPException(400, "Run analysis first")
    return _jsonify(_state["funnel_analysis"])


@app.get("/api/roi-analysis")
def get_roi_analysis(gross_margin_pct: float = 0.65):
    """Get all 5 ROI formulas + marginal ROI by campaign."""
    if _state["campaign_data"] is None:
        raise HTTPException(400, "No data loaded")
    result = run_full_roi_analysis(
        _state["campaign_data"],
        _state.get("curves"),
        gross_margin_pct
    )
    return _jsonify(result)


@app.get("/api/marginal-roi-table")
def get_marginal_roi_table_endpoint():
    """Get marginal ROI at various spend levels per channel."""
    if _state["curves"] is None:
        raise HTTPException(400, "Run analysis first")
    table = get_marginal_roi_table(_state["curves"])
    return _jsonify(table.to_dict(orient="records"))


@app.get("/api/download-template")
def download_template():
    """Download CSV upload template."""
    import os
    template_path = os.path.join(os.path.dirname(__file__), "data", "upload_template.csv")
    if os.path.exists(template_path):
        with open(template_path) as f:
            content = f.read()
        return JSONResponse(content={"csv": content, "filename": "upload_template.csv"})


# ═══ Phase 2 Endpoints ═══

@app.post("/api/adstock")
def run_adstock(adstock_type: str = "geometric"):
    """Fit adstock parameters per channel."""
    if _state["campaign_data"] is None:
        raise HTTPException(400, "No data loaded")
    result = compute_channel_adstock(_state["campaign_data"], adstock_type)
    return _jsonify(result)


@app.post("/api/mmm")
def run_mmm_endpoint():
    """Run Bayesian Marketing Mix Model."""
    if _state["campaign_data"] is None:
        raise HTTPException(400, "No data loaded")
    adstock = compute_channel_adstock(_state["campaign_data"], "geometric")
    result = run_mmm(_state["campaign_data"], adstock)
    return _jsonify(result)


@app.get("/api/markov-attribution")
def get_markov_attribution():
    """Run Markov chain attribution on journey data."""
    if _state["journey_data"] is None:
        raise HTTPException(400, "No journey data loaded")
    # Convert DataFrame to list of dicts
    j_groups = {}
    for _, row in _state["journey_data"].iterrows():
        jid = row["journey_id"]
        if jid not in j_groups:
            j_groups[jid] = {"id": jid, "tps": [], "cv": row["converted"], "rv": 0, "nt": row["total_touchpoints"]}
        j_groups[jid]["tps"].append({"ch": row["channel"], "camp": row["campaign"], "o": row["touchpoint_order"]})
        if row["conversion_revenue"] > 0:
            j_groups[jid]["rv"] = row["conversion_revenue"]
    js = list(j_groups.values())
    result = markov_attribution(js)
    return _jsonify(result)


@app.get("/api/forecast")
def get_forecast(periods: int = 12):
    """Run Prophet/ARIMA forecast."""
    if _state["campaign_data"] is None:
        raise HTTPException(400, "No data loaded")
    result = run_full_forecast(_state["campaign_data"], periods)
    return _jsonify(result)


@app.get("/api/cross-channel")
def get_cross_channel():
    """Run cross-channel leakage analysis."""
    if _state["campaign_data"] is None:
        raise HTTPException(400, "No data loaded")
    result = run_cross_channel_analysis(_state["campaign_data"])
    return _jsonify(result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# ═══ Phase 3 Endpoints ═══

@app.get("/api/shapley")
def get_shapley():
    """Run Shapley value attribution."""
    if _state["campaign_data"] is None or _state["curves"] is None:
        raise HTTPException(400, "Run analysis first")
    result = run_shapley(_state["campaign_data"], _state["curves"], n_samples=300)
    return _jsonify(result)


@app.post("/api/multi-objective")
def run_multi_objective(n_solutions: int = 30):
    """Run multi-objective optimization for Pareto frontier."""
    if _state["curves"] is None:
        raise HTTPException(400, "Run analysis first")
    budget = float(_state["campaign_data"]["spend"].sum())
    result = multi_objective_optimize(_state["curves"], budget, n_solutions=n_solutions)
    return _jsonify(result)


@app.get("/api/geo-lift/{channel}")
def get_geo_lift_design(channel: str):
    """Design a geo-lift test for a channel."""
    if _state["campaign_data"] is None:
        raise HTTPException(400, "No data loaded")
    result = design_geo_test(_state["campaign_data"], channel)
    return _jsonify(result)


@app.get("/api/hierarchical-forecast")
def get_hierarchical_forecast(periods: int = 12):
    """Run hierarchical forecasting."""
    if _state["campaign_data"] is None:
        raise HTTPException(400, "No data loaded")
    result = hierarchical_forecast(_state["campaign_data"], periods)
    return _jsonify(result)


@app.get("/api/automated-recommendations")
def get_automated_recs():
    """Get model-driven automated recommendations."""
    if _state["campaign_data"] is None:
        raise HTTPException(400, "No data loaded")
    result = automated_recommendations(
        _state["campaign_data"],
        response_curves=_state.get("curves"),
        attribution_results=_state.get("attribution"),
    )
    return _jsonify(result)


@app.get("/api/model-health")
def get_model_health():
    """Check model drift and recalibration needs."""
    if _state["curves"] is None or _state["campaign_data"] is None:
        raise HTTPException(400, "Run analysis first")
    result = check_model_drift(_state["curves"], _state["campaign_data"])
    return _jsonify(result)


# ═══ Frontend Serving ═══

from fastapi.responses import HTMLResponse, FileResponse
from starlette.staticfiles import StaticFiles

# Serve JSX as static file
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if not os.path.isdir(frontend_dir):
    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if not os.path.isdir(frontend_dir):
    frontend_dir = "/app/frontend"

try:
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
except Exception:
    pass

@app.get("/app", response_class=HTMLResponse)
def serve_frontend():
    """Serve the React frontend."""
    html_path = None
    for p in [
        os.path.join(frontend_dir, "index.html"),
        os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html"),
        "/app/frontend/index.html",
    ]:
        if os.path.exists(p):
            html_path = p
            break
    
    if not html_path:
        return HTMLResponse("<h1>Frontend not found</h1>", status_code=404)
    
    with open(html_path, "r") as f:
        return HTMLResponse(f.read())
