"""
FastAPI Backend — Marketing ROI & Budget Optimization Engine
All imports updated to match upgraded engine function names.
Run: uvicorn api:app --reload --port 8000
"""
import os, sys, json, tempfile
from typing import Optional, Dict
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

# ═══ CORRECTED IMPORTS — matching upgraded engine function names ═══
from mock_data import generate_all_data, export_to_csv
from validator import validate_data
from engines.attribution import run_all_attribution, compute_attribution_roi
from engines.response_curves import fit_response_curves                       # ✅ unchanged
from engines.optimizer import optimize_budget, sensitivity_analysis            # ✅ unchanged
from engines.diagnostics import generate_recommendations                      # ✅ was: run_diagnostics
from engines.leakage import run_three_pillars                                 # ✅ was: calculate_all_pillars
from engines.trend_analysis import run_trend_analysis                         # ✅ was: run_full_trend_analysis
from engines.funnel_analysis import run_funnel_analysis                       # ✅ was: run_full_funnel_analysis
from engines.roi_formulas import compute_all_roi                              # ✅ was: run_full_roi_analysis
from engines.adstock import compute_channel_adstock                           # ✅ unchanged
from engines.mmm import run_mmm                                              # ✅ unchanged
from engines.markov_attribution import run_markov_attribution                 # ✅ was: markov_attribution
from engines.forecasting import run_forecast                                  # ✅ was: run_full_forecast
from engines.cross_channel import run_cross_channel_analysis                  # ✅ unchanged
from engines.shapley import compute_shapley_values                            # ✅ was: run_shapley
from engines.multi_objective import pareto_optimize                           # ✅ was: multi_objective_optimize
from engines.geo_lift import run_geo_lift                                     # ✅ was: design_geo_test
from engines.hierarchical_forecast import run_hierarchical_forecast           # ✅ was: hierarchical_forecast
from engines.automated_recs import automated_recommendations, check_model_drift, track_realization

app = FastAPI(title="Marketing ROI & Budget Optimization Engine", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

from engines.data_splitter import split_data, validate_split

# In-memory state
_state: Dict = {
    "campaign_data": None, "journey_data": None, "validation": None,
    "curves": None, "attribution": None, "attribution_roi": None,
    "optimization": None, "diagnostics": None, "pillars": None,
    "trend_analysis": None, "funnel_analysis": None, "roi_analysis": None,
    "data_split": None,  # reporting vs training split metadata
    "reporting_data": None,  # last 12 months for ROI/KPIs
    "training_data": None,   # full history for models
}

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)): return int(obj)
        if isinstance(obj, (np.floating,)): return float(obj)
        if isinstance(obj, (np.bool_,)): return bool(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        if isinstance(obj, pd.Timestamp): return obj.isoformat()
        if isinstance(obj, (bool,)): return bool(obj)
        return super().default(obj)

def _j(obj):
    """Safely serialize numpy/pandas objects to JSON."""
    return json.loads(json.dumps(obj, cls=NumpyEncoder))


def _ensure_analysis():
    """Lazy execution: auto-run analysis if data is loaded but engines haven't run."""
    if _state["campaign_data"] is not None and _state["curves"] is None:
        _run_all_engines()


def _get_data_warnings():
    """Return warnings about data quality and sufficiency."""
    warnings = []
    df = _state.get("reporting_data")
    if df is None: df = _state.get("campaign_data")
    if df is None: return ["No data loaded"]
    n_rows = len(df)
    n_channels = df["channel"].nunique() if "channel" in df.columns else 0
    n_months = df["month"].nunique() if "month" in df.columns else 0
    if n_rows < 50: warnings.append(f"Only {n_rows} rows — results may be statistically weak. Upload more data for reliable outputs.")
    if n_channels < 3: warnings.append(f"Only {n_channels} channels — optimizer needs 3+ channels for meaningful reallocation.")
    if n_months < 6: warnings.append(f"Only {n_months} months of reporting data — KPIs may not represent full seasonal cycle.")
    training = _state.get("training_data")
    if training is not None:
        t_months = training["month"].nunique() if "month" in training.columns else 0
        if t_months < 24: warnings.append(f"Only {t_months} months of training data — response curves and forecasts have wide uncertainty.")
        if t_months < 36: warnings.append(f"Only {t_months} months for MMM — Bayesian model needs 36+ months for convergent posteriors.")
    return warnings


# ═══════════════════════════════════════════════
#  CORE ENDPOINTS
# ═══════════════════════════════════════════════

@app.get("/")
def root():
    return {"status": "ok", "engine": "Marketing ROI & Budget Optimization Engine v2.0",
            "engines_loaded": True, "api_version": "2.0"}


@app.get("/api/health")
def health_check():
    """Health endpoint for deployment monitoring."""
    data_loaded = _state["campaign_data"] is not None
    engines_run = _state["curves"] is not None
    return {
        "status": "healthy" if data_loaded and engines_run else "ready" if not data_loaded else "data_loaded",
        "data_loaded": data_loaded,
        "engines_run": engines_run,
        "reporting_rows": len(_state["reporting_data"]) if _state.get("reporting_data") is not None else 0,
        "training_rows": len(_state["training_data"]) if _state.get("training_data") is not None else 0,
        "engines_available": {
            "curves": _state["curves"] is not None and len(_state["curves"]) > 0,
            "optimization": _state["optimization"] is not None,
            "diagnostics": _state["diagnostics"] is not None and len(_state["diagnostics"]) > 0,
            "pillars": _state["pillars"] is not None,
            "attribution": _state["attribution"] is not None,
        },
    }


@app.post("/api/load-mock-data")
def load_mock_data():
    """Load demo data and run all engines automatically."""
    data = generate_all_data()
    _state["campaign_data"] = data["campaign_performance"]
    _state["journey_data"] = data["user_journeys"]
    _state["validation"] = validate_data(_state["campaign_data"])
    
    # Auto-run all engines so subsequent calls work
    _run_all_engines()
    
    return _j({
        "status": "ok",
        "rows": len(_state["campaign_data"]),
        "journey_rows": len(_state["journey_data"]),
        "channels": int(_state["campaign_data"]["channel"].nunique()),
        "campaigns": int(_state["campaign_data"]["campaign"].nunique()),
        "total_spend": float(_state["campaign_data"]["spend"].sum()),
        "total_revenue": float(_state["campaign_data"]["revenue"].sum()),
        "engines_run": True,
    })


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read(); tmp.write(content); tmp_path = tmp.name
    try:
        if suffix == ".csv": df = pd.read_csv(tmp_path)
        elif suffix in (".xlsx", ".xls"): df = pd.read_excel(tmp_path)
        else: raise HTTPException(400, f"Unsupported: {suffix}")
        _state["campaign_data"] = df
        _state["validation"] = validate_data(df)
        return _j({"filename": file.filename, "rows": len(df), "columns": list(df.columns),
                    "validation": _state["validation"]})
    finally:
        os.unlink(tmp_path)


@app.post("/api/upload-journeys")
async def upload_journey_file(file: UploadFile = File(...)):
    """Upload user journey CSV/XLSX for multi-touch attribution."""
    suffix = Path(file.filename).suffix.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read(); tmp.write(content); tmp_path = tmp.name
    try:
        if suffix == ".csv": df = pd.read_csv(tmp_path)
        elif suffix in (".xlsx", ".xls"): df = pd.read_excel(tmp_path)
        else: raise HTTPException(400, f"Unsupported: {suffix}")
        _state["journey_data"] = df
        return _j({"filename": file.filename, "rows": len(df), "columns": list(df.columns),
                    "status": "Journey data loaded. Re-run /api/run-analysis to include in attribution."})
    finally:
        os.unlink(tmp_path)


def _normalize_date_columns(df):
    """Ensure both 'date' and 'month' columns exist for cross-engine compatibility."""
    df = df.copy()
    if "date" in df.columns and "month" not in df.columns:
        df["month"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m")
    elif "month" in df.columns and "date" not in df.columns:
        df["date"] = pd.to_datetime(df["month"].astype(str).apply(lambda x: x+"-01" if len(str(x))<=7 else x), errors="coerce")
    if "channel_type" not in df.columns:
        df["channel_type"] = df.get("ct", "online")
    for col, alt in [("conversions","conv"),("impressions","imps"),("revenue","rev"),("campaign","camp"),("channel","ch")]:
        if col not in df.columns and alt in df.columns:
            df[col] = df[alt]
    for col in ["impressions","clicks","leads","mqls","sqls","conversions","spend","revenue",
                "bounce_rate","avg_session_duration_sec","form_completion_rate","nps_score"]:
        if col not in df.columns: df[col] = 0
    if "region" not in df.columns: df["region"] = "All"
    if "product" not in df.columns: df["product"] = "All"
    return df


def _run_all_engines():
    """Run all engines. Each engine is wrapped in try/except — one failure never crashes the chain."""
    df = _state["campaign_data"]
    if df is None: return
    
    df = _normalize_date_columns(df)
    _state["campaign_data"] = df
    
    # Split data
    date_col = "month" if "month" in df.columns else "date"
    try:
        split = split_data(df, reporting_months=12, date_column=date_col)
        _state["data_split"] = split["metadata"]
        reporting_df = _normalize_date_columns(split["reporting"])
        training_df = _normalize_date_columns(split["training"])
    except Exception as e:
        print(f"[WARN] Split failed ({e}), using full dataset")
        _state["data_split"] = {"reporting_period":{"months":0},"training_period":{"months":0},"error":str(e)}
        reporting_df = df; training_df = df
    _state["reporting_data"] = reporting_df
    _state["training_data"] = training_df
    
    # Response curves
    try:
        _state["curves"] = fit_response_curves(training_df, model_type=_state.get("_model_type", "power_law"))
        print(f"[OK] Curves: {len(_state['curves'])} channels")
    except Exception as e:
        print(f"[FAIL] Curves: {e}"); _state["curves"] = {}
    
    # Attribution
    attr_dicts = {}
    try:
        if _state["journey_data"] is not None:
            _state["attribution"] = run_all_attribution(_state["journey_data"])
            _state["attribution_roi"] = compute_attribution_roi(_state["attribution"], reporting_df)
            for mn, md in _state["attribution"].items():
                try:
                    if hasattr(md, "groupby"): attr_dicts[mn] = md.groupby("channel")["attributed_revenue"].sum().to_dict()
                    elif isinstance(md, dict): attr_dicts[mn] = md
                except: pass
            print(f"[OK] Attribution: {len(attr_dicts)} models")
    except Exception as e:
        print(f"[FAIL] Attribution: {e}"); _state["attribution"] = {}
    
    # Optimization
    try:
        rs = float(reporting_df["spend"].sum())
        _state["optimization"] = optimize_budget(_state["curves"], rs, objective="balanced")
        print(f"[OK] Optimizer: uplift={_state['optimization'].get('summary',{}).get('uplift_pct',0):.1f}%")
    except Exception as e:
        print(f"[FAIL] Optimizer: {e}")
        _state["optimization"] = {"channels":[],"summary":{"total_budget":0,"current_revenue":0,"optimized_revenue":0,"revenue_uplift":0,"uplift_pct":0,"current_roi":0,"optimized_roi":0}}
    
    # Diagnostics
    try:
        _state["diagnostics"] = generate_recommendations(reporting_df, _state["curves"], attr_dicts)
        print(f"[OK] Recs: {len(_state['diagnostics'])}")
    except Exception as e:
        print(f"[FAIL] Recs: {e}"); _state["diagnostics"] = []
    
    # Pillars
    try:
        _state["pillars"] = run_three_pillars(reporting_df, _state["optimization"])
        print(f"[OK] Pillars: risk={_state['pillars'].get('total_value_at_risk',0):,.0f}")
    except Exception as e:
        print(f"[FAIL] Pillars: {e}")
        _state["pillars"] = {"revenue_leakage":{"total_leakage":0,"leakage_pct":0,"by_channel":[]},"experience_suppression":{"total_suppression":0,"items":[]},"avoidable_cost":{"total_avoidable_cost":0,"items":[]},"total_value_at_risk":0,"correction_potential":{"reallocation_uplift":0,"cx_fix_recovery":0,"cost_savings":0,"total_recoverable":0}}
    
    # Trend, funnel, ROI
    try: _state["trend_analysis"] = run_trend_analysis(training_df); print("[OK] Trends")
    except Exception as e: print(f"[FAIL] Trends: {e}"); _state["trend_analysis"] = {}
    try: _state["funnel_analysis"] = run_funnel_analysis(reporting_df); print("[OK] Funnel")
    except Exception as e: print(f"[FAIL] Funnel: {e}"); _state["funnel_analysis"] = {}
    try: _state["roi_analysis"] = compute_all_roi(reporting_df, _state["curves"]); print("[OK] ROI")
    except Exception as e: print(f"[FAIL] ROI: {e}"); _state["roi_analysis"] = []


@app.post("/api/run-analysis")
def run_full_analysis(model_type: str = "power_law"):
    """Run all engines on current data. Accepts model_type: power_law or hill."""
    if _state["campaign_data"] is None:
        raise HTTPException(400, "No data loaded")
    _state["_model_type"] = model_type
    _run_all_engines()
    return _j({
        "status": "complete",
        "model_type": model_type,
        "response_curves_channels": list(_state["curves"].keys()) if _state["curves"] else [],
        "recommendations_count": len(_state["diagnostics"]) if _state["diagnostics"] else 0,
        "total_value_at_risk": _state["pillars"].get("total_value_at_risk", 0) if _state["pillars"] else 0,
        "optimization_uplift": _state["optimization"].get("summary",{}).get("uplift_pct",0) if _state["optimization"] else 0,
    })


# ═══════════════════════════════════════════════
#  CURRENT STATE
# ═══════════════════════════════════════════════

@app.get("/api/data-readiness")
def get_data_readiness():
    """Show what data is available, which engines can run, and what needs more data."""
    if _state["data_split"] is None:
        raise HTTPException(400, "No data loaded")
    split_meta = _state["data_split"]
    # Re-validate
    split = split_data(_state["campaign_data"], reporting_months=12,
                       date_column="month" if "month" in _state["campaign_data"].columns else "date")
    readiness = validate_split(split)
    return _j({
        "periods": split_meta,
        "engine_readiness": readiness["engine_readiness"],
        "overall_ready": readiness["overall_ready"],
        "warnings": readiness["warnings"],
        "recommendation": (
            "Upload 3+ years of historical data for reliable MMM and forecasting. "
            "Current reporting period uses the most recent 12 months for ROI and diagnostics."
        ) if not readiness["overall_ready"] else "All engines have sufficient data.",
    })


@app.get("/api/current-state")
def get_current_state(attribution_model: str = "last_touch"):
    if _state["campaign_data"] is None:
        raise HTTPException(400, "No data loaded")
    # Use REPORTING period (last 12 months) for current-state KPIs
    df = _state["reporting_data"] if _state["reporting_data"] is not None else _state["campaign_data"]
    
    total_spend = float(df["spend"].sum())
    total_revenue = float(df["revenue"].sum())
    total_conv = int(df["conversions"].sum())
    
    summary = {
        "total_spend": total_spend, "total_revenue": total_revenue,
        "roi": (total_revenue - total_spend) / max(total_spend, 1),
        "roas": total_revenue / max(total_spend, 1),
        "total_conversions": total_conv,
        "cac": total_spend / max(total_conv, 1),
    }
    
    # Channel-campaign matrix
    matrix = df.groupby(["channel", "campaign", "channel_type"]).agg(
        spend=("spend","sum"), revenue=("revenue","sum"), impressions=("impressions","sum"),
        clicks=("clicks","sum"), leads=("leads","sum"), conversions=("conversions","sum"),
    ).reset_index()
    matrix["roi"] = (matrix["revenue"] - matrix["spend"]) / matrix["spend"].clip(lower=1)
    matrix["roas"] = matrix["revenue"] / matrix["spend"].clip(lower=1)
    matrix["cac"] = matrix["spend"] / matrix["conversions"].clip(lower=1)
    
    # Monthly trends (use month if available, else date)
    time_col = "month" if "month" in df.columns else "date"
    trends = df.groupby(time_col).agg(
        spend=("spend","sum"), revenue=("revenue","sum"), conversions=("conversions","sum"),
    ).reset_index()
    trends.rename(columns={time_col: "month"}, inplace=True)
    trends["roi"] = (trends["revenue"] - trends["spend"]) / trends["spend"].clip(lower=1)
    
    # Online vs offline
    split = df.groupby("channel_type").agg(spend=("spend","sum"), revenue=("revenue","sum")).reset_index()
    
    # Attribution
    attr_data = None
    if _state["attribution_roi"] and attribution_model in _state["attribution_roi"]:
        attr_data = _state["attribution_roi"][attribution_model].to_dict(orient="records")
    
    return _j({"summary": summary, "channel_campaign_matrix": matrix.to_dict(orient="records"),
               "monthly_trends": trends.to_dict(orient="records"),
               "online_offline_split": split.to_dict(orient="records"),
               "attribution": attr_data, "attribution_model": attribution_model})


@app.get("/api/full-state")
def get_full_state():
    """
    Returns ALL data the frontend needs in a single call, shaped to match
    the frontend's internal data model. This is the primary integration endpoint.
    """
    if _state["campaign_data"] is None:
        raise HTTPException(400, "No data loaded — call POST /api/load-mock-data first")
    
    df = _state["reporting_data"] if _state["reporting_data"] is not None else _state["campaign_data"]
    
    # Build rows array matching frontend shape
    col_map = {"channel":"ch","campaign":"camp","channel_type":"ct","impressions":"imps",
               "conversions":"conv","revenue":"rev","bounce_rate":"br",
               "avg_session_duration_sec":"sd","form_completion_rate":"fc","nps_score":"nps"}
    rows = []
    for _, r in df.iterrows():
        row = {}
        for col in df.columns:
            key = col_map.get(col, col)
            val = r[col]
            if isinstance(val, (np.integer,)): val = int(val)
            elif isinstance(val, (np.floating,)): val = float(val)
            row[key] = val
        # Add ml (month label) from month
        m_str = str(r.get("month", ""))
        if "-" in m_str:
            try: row["ml"] = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][int(m_str.split("-")[1])]
            except: row["ml"] = m_str
        rows.append(row)
    
    # Build optimizer in frontend shape
    opt_data = None
    if _state["optimization"] and "summary" in _state["optimization"]:
        opt = _state["optimization"]
        opt_channels = [{"channel":c["channel"], "cS":round(c.get("current_spend",0)),
            "oS":round(c.get("optimized_spend",0)), "chg":round(c.get("change_pct",0),1),
            "cR":round(c.get("current_revenue",0)), "oR":round(c.get("optimized_revenue",0)),
            "rChg":round(c.get("revenue_delta",0)),
            "cROI":round(c.get("current_roi",0),3), "oROI":round(c.get("optimized_roi",0),3),
            "mROI":round(c.get("marginal_roi",0),4), "locked":c.get("locked",False)}
            for c in opt.get("channels",[])]
        sm = opt.get("summary",{})
        opt_summary = {"cRev":round(sm.get("current_revenue",0)),
            "oRev":round(sm.get("optimized_revenue",0)),
            "uplift":round(sm.get("uplift_pct",0),2),
            "cROI":round(sm.get("current_roi",0),3),
            "oROI":round(sm.get("optimized_roi",0),3)}
        opt_data = {"channels":opt_channels, "summary":opt_summary}
    
    # Build pillars in frontend shape
    pl_data = None
    if _state["pillars"]:
        p = _state["pillars"]
        leak = p.get("revenue_leakage",{})
        exp = p.get("experience_suppression",{})
        cost = p.get("avoidable_cost",{})
        pl_data = {
            "leak":{"total":leak.get("total_leakage",0),"pct":leak.get("leakage_pct",0),
                "byCh":[{"channel":c.get("channel",""),"leakage":c.get("leakage",0),"type":c.get("type","")} 
                    for c in leak.get("by_channel",[])]},
            "exp":{"total":exp.get("total_suppression",0),
                "items":[{"ch":i.get("channel",""),"camp":i.get("campaign",""),"cvr":i.get("cvr",0),
                    "sR":i.get("suppressed_revenue",0),"br":i.get("bounce_rate",0)} for i in exp.get("items",[])]},
            "cost":{"total":cost.get("total_avoidable_cost",0),
                "items":[{"ch":i.get("channel",""),"cac":i.get("cac",0),"av":i.get("avoidable_cost",0)} for i in cost.get("items",[])]},
            "totalRisk":p.get("total_value_at_risk",0)
        }
    
    # Build recs in frontend shape
    recs_data = []
    if _state["diagnostics"]:
        for r in _state["diagnostics"]:
            recs_data.append({"type":r.get("type",""),"ch":r.get("channel",""),
                "camp":r.get("campaign",""),"rationale":r.get("rationale",""),
                "action":r.get("action",""),"impact":r.get("impact",0),
                "conf":r.get("confidence","Medium"),"effort":r.get("effort","Medium"),
                "id":r.get("id",""),"priority":r.get("priority",0)})
    
    # Build attribution in frontend shape (simple {channel: revenue} dicts)
    attr_data = {}
    if _state["attribution"]:
        for model_name, model_data in _state["attribution"].items():
            if hasattr(model_data, "groupby"):
                attr_data[model_name] = model_data.groupby("channel")["attributed_revenue"].sum().to_dict()
            elif isinstance(model_data, dict):
                attr_data[model_name] = model_data
    
    # Build curves in frontend shape
    curves_data = {}
    if _state["curves"]:
        for ch, info in _state["curves"].items():
            if "error" in info: continue
            p = info.get("params",{})
            curves_data[ch] = {"a":p.get("a",1),"b":p.get("b",0.5),
                "avgSpend":info.get("current_avg_spend",0),"satSpend":info.get("saturation_spend",0),
                "mROI":info.get("marginal_roi",0),"hd":info.get("headroom_pct",0),
                "cp":info.get("curve_points",[])}
    
    tS = float(df["spend"].sum())
    
    return _j({
        "rows": rows,
        "opt": opt_data or {"channels":[],"summary":{"cRev":0,"oRev":0,"uplift":0,"cROI":0,"oROI":0}},
        "pl": pl_data or {"leak":{"total":0,"pct":0,"byCh":[]},"exp":{"total":0,"items":[]},"cost":{"total":0,"items":[]},"totalRisk":0},
        "attr": attr_data,
        "curves": curves_data,
        "tS": tS,
        "recs": recs_data,
        "dataReadiness": _state.get("data_split"),
        "apiMode": True,
        "warnings": _get_data_warnings(),
    })


@app.get("/api/deep-dive/{channel}")
def get_channel_deep_dive(channel: str):
    if _state["campaign_data"] is None: raise HTTPException(400, "No data loaded")
    df = _state["campaign_data"]
    ch_data = df[df["channel"] == channel]
    if len(ch_data) == 0: raise HTTPException(404, f"Channel '{channel}' not found")
    
    trend = ch_data.groupby("month").agg(spend=("spend","sum"),revenue=("revenue","sum"),conversions=("conversions","sum"),leads=("leads","sum")).reset_index()
    trend["roi"] = (trend["revenue"] - trend["spend"]) / trend["spend"]
    regional = ch_data.groupby("region").agg(spend=("spend","sum"),revenue=("revenue","sum"),conversions=("conversions","sum")).reset_index()
    regional["roi"] = (regional["revenue"] - regional["spend"]) / regional["spend"]
    funnel = {s: int(ch_data[s].sum()) for s in ["impressions","clicks","leads","mqls","sqls","conversions"]}
    cx = {"avg_bounce_rate":float(ch_data["bounce_rate"].mean()),"avg_session_duration":float(ch_data["avg_session_duration_sec"].mean()),
          "avg_form_completion":float(ch_data["form_completion_rate"].mean()),"avg_nps":float(ch_data["nps_score"].mean())}
    curve_data = _state["curves"].get(channel) if _state["curves"] else None
    return _j({"channel":channel,"monthly_trend":trend.to_dict(orient="records"),
               "regional_breakdown":regional.to_dict(orient="records"),"funnel":funnel,"cx_signals":cx,"response_curve":curve_data})


# ═══════════════════════════════════════════════
#  ANALYSIS ENDPOINTS
# ═══════════════════════════════════════════════

@app.get("/api/validation")
def get_validation():
    if _state["validation"] is None: raise HTTPException(400, "No data loaded")
    return _j(_state["validation"])

@app.get("/api/response-curves")
def get_response_curves():
    _ensure_analysis()
    if _state["curves"] is None: raise HTTPException(400, "No data loaded — upload data or call /api/load-mock-data first")
    return _j(_state["curves"])

@app.get("/api/recommendations")
def get_recommendations():
    _ensure_analysis()
    if _state["diagnostics"] is None: raise HTTPException(400, "No data loaded — upload data or call /api/load-mock-data first")
    return _j(_state["diagnostics"])

@app.post("/api/optimize")
def run_optimization(
    total_budget: Optional[float] = None,
    objective: str = "balanced",
    model_type: str = "power_law",
    weight_revenue: float = 0.4,
    weight_roi: float = 0.3,
    weight_leakage: float = 0.15,
    weight_cost: float = 0.15,
):
    """Run optimization with custom objective, weights, and model type."""
    _ensure_analysis()
    if _state["curves"] is None: raise HTTPException(400, "No data loaded — upload data or call /api/load-mock-data first")
    
    # Re-fit curves if model type changed
    if model_type != _state.get("_model_type", "power_law"):
        _state["_model_type"] = model_type
        training_df = _state.get("training_data")
        if training_df is None: training_df = _state["campaign_data"]
        training_df = _normalize_date_columns(training_df)
        _state["curves"] = fit_response_curves(training_df, model_type=model_type)
    
    if total_budget is None: total_budget = float(_state["campaign_data"]["spend"].sum())
    weights = {"revenue": weight_revenue, "roi": weight_roi, "leakage": weight_leakage, "cost": weight_cost}
    result = optimize_budget(_state["curves"], total_budget, objective=objective, objective_weights=weights)
    _state["optimization"] = result
    reporting_df = _state.get("reporting_data")
    if reporting_df is None: reporting_df = _state["campaign_data"]
    _state["pillars"] = run_three_pillars(reporting_df, result)
    return _j(result)

@app.get("/api/sensitivity")
def get_sensitivity(objective: str = "balanced"):
    _ensure_analysis()
    if _state["curves"] is None: raise HTTPException(400, "No data loaded — upload data or call /api/load-mock-data first")
    base_budget = float(_state["campaign_data"]["spend"].sum())
    return _j(sensitivity_analysis(_state["curves"], base_budget, objective))

@app.get("/api/pillars")
def get_pillars():
    _ensure_analysis()
    if _state["pillars"] is None: raise HTTPException(400, "No data loaded — upload data or call /api/load-mock-data first")
    return _j(_state["pillars"])

@app.get("/api/business-case")
def get_business_case():
    if not all([_state["optimization"], _state["pillars"], _state["diagnostics"]]):
        raise HTTPException(400, "Run full analysis first")
    opt = _state["optimization"]; pillars = _state["pillars"]; recs = _state["diagnostics"]
    return _j({
        "optimization_summary": opt.get("summary", {}),
        "value_at_risk": pillars.get("total_value_at_risk", 0),
        "correction_potential": pillars.get("correction_potential", {}),
        "top_recommendations": recs[:5] if isinstance(recs, list) else [],
        "implementation_phases": [
            {"phase": "Immediate (0-30 days)", "actions": [r for r in recs if r.get("effort") == "Low"][:3]},
            {"phase": "Short-term (30-90 days)", "actions": [r for r in recs if r.get("effort") == "Medium"][:3]},
            {"phase": "Strategic (90+ days)", "actions": [r for r in recs if r.get("effort") == "High"][:3]},
        ] if isinstance(recs, list) else [],
    })

@app.get("/api/trend-analysis")
def get_trend_analysis():
    if _state["trend_analysis"] is None:
        if _state["campaign_data"] is not None:
            _state["trend_analysis"] = run_trend_analysis(_state["campaign_data"])  # ✅ fixed
        else: raise HTTPException(400, "No data loaded")
    return _j(_state["trend_analysis"])

@app.get("/api/funnel-analysis")
def get_funnel_analysis():
    if _state["funnel_analysis"] is None:
        if _state["campaign_data"] is not None:
            _state["funnel_analysis"] = run_funnel_analysis(_state["campaign_data"])  # ✅ fixed
        else: raise HTTPException(400, "No data loaded")
    return _j(_state["funnel_analysis"])

@app.get("/api/roi-analysis")
def get_roi_analysis(gross_margin_pct: float = 0.65):
    if _state["campaign_data"] is None: raise HTTPException(400, "No data loaded")
    return _j(compute_all_roi(_state["campaign_data"], _state.get("curves"), gross_margin_pct))  # ✅ fixed

@app.get("/api/download-template")
def download_template():
    template_path = os.path.join(os.path.dirname(__file__), "data", "upload_template.csv")
    if os.path.exists(template_path):
        with open(template_path) as f: return JSONResponse(content={"csv": f.read()})
    raise HTTPException(404, "Template not found")


# ═══════════════════════════════════════════════
#  PHASE 2 ENDPOINTS
# ═══════════════════════════════════════════════

@app.post("/api/adstock")
def run_adstock(adstock_type: str = "geometric"):
    if _state["campaign_data"] is None: raise HTTPException(400, "No data loaded")
    return _j(compute_channel_adstock(_state["campaign_data"], adstock_type))

@app.post("/api/mmm")
def run_mmm_endpoint():
    """Run Bayesian MMM (PyMC → OLS fallback)."""
    if _state["campaign_data"] is None: raise HTTPException(400, "No data loaded")
    return _j(run_mmm(_state["campaign_data"], method="auto"))  # ✅ updated call signature

@app.get("/api/markov-attribution")
def get_markov_attribution():
    if _state["journey_data"] is None: raise HTTPException(400, "No journey data")
    j_groups = {}
    for _, row in _state["journey_data"].iterrows():
        jid = row["journey_id"]
        if jid not in j_groups:
            j_groups[jid] = {"id":jid,"tps":[],"cv":row["converted"],"rv":0,"nt":row["total_touchpoints"]}
        j_groups[jid]["tps"].append({"ch":row["channel"],"camp":row["campaign"],"o":row["touchpoint_order"]})
        if row["conversion_revenue"] > 0: j_groups[jid]["rv"] = row["conversion_revenue"]
    return _j(run_markov_attribution(list(j_groups.values())))  # ✅ fixed name

@app.get("/api/forecast")
def get_forecast(periods: int = 12):
    if _state["campaign_data"] is None: raise HTTPException(400, "No data loaded")
    return _j(run_forecast(_state["campaign_data"], "revenue", periods))  # ✅ fixed name + args

@app.get("/api/cross-channel")
def get_cross_channel():
    if _state["campaign_data"] is None: raise HTTPException(400, "No data loaded")
    return _j(run_cross_channel_analysis(_state["campaign_data"]))


# ═══════════════════════════════════════════════
#  PHASE 3 ENDPOINTS
# ═══════════════════════════════════════════════

@app.get("/api/shapley")
def get_shapley():
    """Shapley values require response curves for the value function."""
    _ensure_analysis()
    if _state["curves"] is None: raise HTTPException(400, "No data loaded — upload data or call /api/load-mock-data first")
    curves = _state["curves"]
    channels = list(curves.keys())
    def value_fn(coalition):
        total = 0
        for ch in coalition:
            if ch in curves and "params" in curves[ch]:
                p = curves[ch]["params"]
                a, b = p.get("a",1), p.get("b",0.5)
                avg = curves[ch].get("current_avg_spend", 1000)
                total += a * np.power(max(avg, 1), b) * 12
        return total
    return _j(compute_shapley_values(channels, value_fn))  # ✅ fixed name + args

@app.post("/api/multi-objective")
def run_multi_objective(n_solutions: int = 30):
    _ensure_analysis()
    if _state["curves"] is None: raise HTTPException(400, "No data loaded — upload data or call /api/load-mock-data first")
    budget = float(_state["campaign_data"]["spend"].sum())
    return _j(pareto_optimize(_state["curves"], budget, n_points=n_solutions))  # ✅ fixed name

@app.get("/api/geo-lift/{region}")
def get_geo_lift(region: str):
    if _state["campaign_data"] is None: raise HTTPException(400, "No data loaded")
    return _j(run_geo_lift(_state["campaign_data"], test_region=region))  # ✅ fixed name

@app.get("/api/hierarchical-forecast")
def get_hierarchical_forecast(periods: int = 12):
    if _state["campaign_data"] is None: raise HTTPException(400, "No data loaded")
    return _j(run_hierarchical_forecast(_state["campaign_data"], periods=periods))  # ✅ fixed name

@app.get("/api/automated-recommendations")
def get_automated_recs():
    if _state["campaign_data"] is None: raise HTTPException(400, "No data loaded")
    return _j(automated_recommendations(_state["campaign_data"],
        response_curves=_state.get("curves"), attribution_results=_state.get("attribution")))

@app.get("/api/model-health")
def get_model_health():
    _ensure_analysis()
    if _state["curves"] is None: raise HTTPException(400, "No data loaded — upload data or call /api/load-mock-data first")
    return _j(check_model_drift(_state["curves"], _state["campaign_data"]))


# ═══════════════════════════════════════════════
#  FRONTEND SERVING
# ═══════════════════════════════════════════════

from starlette.staticfiles import StaticFiles

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if not os.path.isdir(frontend_dir):
    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")

try:
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
except Exception:
    pass

@app.get("/app", response_class=HTMLResponse)
def serve_frontend():
    for p in [os.path.join(frontend_dir, "index.html"),
              os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")]:
        if os.path.exists(p):
            with open(p) as f: return HTMLResponse(f.read())
    return HTMLResponse("<h1>Frontend not found</h1>", status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
