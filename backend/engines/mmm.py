"""
Bayesian Marketing Mix Model — Production Grade
================================================
Model: Revenue_t = baseline + Σ_c β_c · Hill(Adstock(Spend_c,t; λ_c); K_c) + season + ε_t

Libraries:
    pymc (NUTS sampler), arviz (diagnostics), scipy (MLE fallback), scikit-learn (metrics)
"""
import numpy as np
import pandas as pd
from typing import Dict, Optional
from sklearn.metrics import r2_score, mean_absolute_percentage_error
import warnings, logging
warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)

def geometric_adstock(x, decay):
    out = np.zeros_like(x, dtype=np.float64)
    out[0] = x[0]
    for t in range(1, len(x)):
        out[t] = x[t] + decay * out[t - 1]
    return out

def hill_saturation(x, half_sat, slope=1.0):
    x_s = np.maximum(x, 1e-10)
    return np.power(x_s, slope) / (np.power(half_sat, slope) + np.power(x_s, slope))

def prepare_mmm_data(df):
    time_col = "month" if "month" in df.columns else "date"
    monthly = df.groupby(time_col).agg(revenue=("revenue","sum"), total_spend=("spend","sum")).reset_index().sort_values(time_col)
    channels = sorted(df["channel"].unique())
    spend_matrix = {}
    for ch in channels:
        ch_agg = df[df["channel"]==ch].groupby(time_col)["spend"].sum()
        spend_matrix[ch] = monthly[time_col].map(ch_agg).fillna(0).values.astype(np.float64)
    if "month" in df.columns:
        month_nums = monthly["month"].apply(lambda x: int(str(x).split("-")[1]) if "-" in str(x) else 1).values
    else:
        month_nums = (np.arange(len(monthly)) % 12) + 1
    return {"revenue": monthly["revenue"].values.astype(np.float64), "spend_matrix": spend_matrix,
            "channels": channels, "n_periods": len(monthly), "month_nums": month_nums, "periods": monthly[time_col].values}

def fit_bayesian_mmm(data, n_draws=1000, n_tune=500, n_chains=2):
    """Full Bayesian MMM. Adstock decay is sampled jointly with betas via NUTS."""
    import pymc as pm
    import arviz as az
    revenue = data["revenue"]; channels = data["channels"]; n_ch = len(channels); T = data["n_periods"]
    spend_raw = np.column_stack([data["spend_matrix"][ch] for ch in channels])
    spend_scales = spend_raw.max(axis=0) + 1e-10
    spend_normed = spend_raw / spend_scales
    sin_s = np.sin(2*np.pi*data["month_nums"]/12); cos_s = np.cos(2*np.pi*data["month_nums"]/12)
    rev_mean, rev_std = revenue.mean(), revenue.std()+1e-10

    with pm.Model():
        baseline = pm.Normal("baseline", mu=rev_mean, sigma=rev_std)
        betas = pm.HalfNormal("betas", sigma=rev_std*0.5, shape=n_ch)
        decays = pm.Beta("decays", alpha=3, beta=3, shape=n_ch)
        half_sats = pm.LogNormal("half_sats", mu=-0.7, sigma=0.5, shape=n_ch)
        gamma = pm.Normal("gamma", mu=0, sigma=rev_std*0.1, shape=2)
        sigma = pm.HalfNormal("sigma", sigma=rev_std*0.3)
        mu = baseline + gamma[0]*sin_s + gamma[1]*cos_s
        for c in range(n_ch):
            ad_list = [spend_normed[0, c]]
            for t in range(1, T):
                ad_list.append(spend_normed[t, c] + decays[c]*ad_list[-1])
            ad_tensor = pm.math.stack(ad_list)
            sat = ad_tensor / (half_sats[c] + ad_tensor)
            mu = mu + betas[c] * sat * spend_scales[c]
        pm.Normal("obs", mu=mu, sigma=sigma, observed=revenue)
        trace = pm.sample(draws=n_draws, tune=n_tune, chains=n_chains, cores=1,
                          target_accept=0.9, return_inferencedata=True, progressbar=False, random_seed=42)

    summary = az.summary(trace, var_names=["betas","decays","baseline"])
    rhat_max = float(summary["r_hat"].max()); ess_min = float(summary["ess_bulk"].min())
    try: loo_score = float(az.loo(trace).loo)
    except: loo_score = None
    beta_means = trace.posterior["betas"].values.mean(axis=(0,1))
    beta_stds = trace.posterior["betas"].values.std(axis=(0,1))
    beta_hdi = az.hdi(trace, var_names=["betas"], hdi_prob=0.9)["betas"].values
    decay_means = trace.posterior["decays"].values.mean(axis=(0,1))
    decay_stds = trace.posterior["decays"].values.std(axis=(0,1))
    baseline_mean = float(trace.posterior["baseline"].values.mean())

    contributions = {}; total_media = 0
    for c, ch in enumerate(channels):
        spend = data["spend_matrix"][ch]; d = float(decay_means[c])
        hs = float(trace.posterior["half_sats"].values.mean(axis=(0,1))[c])
        ad = geometric_adstock(spend/spend_scales[c], d); sat = hill_saturation(ad, hs)
        contrib = max(0, float(beta_means[c]) * sat.sum() * spend_scales[c]); total_media += contrib
        contributions[ch] = {"contribution": round(contrib,0), "beta_mean": round(float(beta_means[c]),4),
            "beta_std": round(float(beta_stds[c]),4), "beta_hdi_90": [round(float(beta_hdi[c,0]),4), round(float(beta_hdi[c,1]),4)],
            "decay_mean": round(d,3), "decay_std": round(float(decay_stds[c]),3),
            "spend": round(float(spend.sum()),0)}

    total_rev = float(revenue.sum()); bl_contrib = max(0, total_rev - total_media)
    y_pred = np.full(T, baseline_mean)
    y_pred += float(trace.posterior["gamma"].values.mean(axis=(0,1))[0])*sin_s
    y_pred += float(trace.posterior["gamma"].values.mean(axis=(0,1))[1])*cos_s
    for c, ch in enumerate(channels):
        ad = geometric_adstock(data["spend_matrix"][ch]/spend_scales[c], float(decay_means[c]))
        hs = float(trace.posterior["half_sats"].values.mean(axis=(0,1))[c])
        y_pred += float(beta_means[c]) * hill_saturation(ad, hs) * spend_scales[c]
    for ch in channels:
        cc = contributions[ch]; cc["contribution_pct"] = round(cc["contribution"]/max(total_rev,1)*100,1)
        cc["mmm_roas"] = round(cc["contribution"]/max(cc["spend"],1),2)
        ci_w = cc["beta_std"]/max(cc["beta_mean"],0.001)
        cc["confidence"] = "High" if ci_w<0.25 else ("Medium" if ci_w<0.5 else "Low")
    return {"method":"bayesian_pymc","contributions":contributions,
        "baseline_contribution":round(bl_contrib,0),"baseline_pct":round(bl_contrib/max(total_rev,1)*100,1),
        "total_revenue":round(total_rev,0),
        "model_diagnostics":{"r_squared":round(float(r2_score(revenue,y_pred)),4),
            "mape":round(float(mean_absolute_percentage_error(revenue,y_pred)*100),2),
            "r_hat_max":round(rhat_max,4),"converged":rhat_max<1.05,"ess_min":round(ess_min,0),
            "loo_cv":loo_score,"n_draws":n_draws,"n_chains":n_chains,"n_periods":T},
        "fitted_values":y_pred.tolist(),"actual_values":revenue.tolist(),
        "channels":channels,"periods":[str(p) for p in data["periods"]]}

def fit_ols_mmm(data):
    """OLS fallback with bootstrap uncertainty. Used when PyMC unavailable."""
    from numpy.linalg import lstsq
    revenue = data["revenue"]; channels = data["channels"]; T = data["n_periods"]
    best_decays = {}
    for ch in channels:
        spend = data["spend_matrix"][ch]
        if spend.sum()==0: best_decays[ch]=0.0; continue
        best_c, best_d = -1, 0.5
        for d in np.arange(0.05, 0.95, 0.05):
            ad = geometric_adstock(spend, d)
            if ad.std()>0:
                corr = np.corrcoef(ad, revenue)[0,1]
                if corr>best_c: best_c=corr; best_d=d
        best_decays[ch] = round(best_d, 2)
    X = np.zeros((T, len(channels)))
    for c, ch in enumerate(channels):
        ad = geometric_adstock(data["spend_matrix"][ch], best_decays[ch])
        hs = float(np.median(ad[ad>0])) if np.any(ad>0) else 1.0
        X[:,c] = hill_saturation(ad, hs)
    sin_s = np.sin(2*np.pi*data["month_nums"]/12); cos_s = np.cos(2*np.pi*data["month_nums"]/12)
    X_full = np.column_stack([np.ones(T), X, sin_s, cos_s])
    coeffs,_,_,_ = lstsq(X_full, revenue, rcond=None)
    baseline_mean = float(coeffs[0]); beta_means = np.abs(coeffs[1:1+len(channels)])
    n_boot=100; beta_boot=np.zeros((n_boot,len(channels)))
    for b in range(n_boot):
        idx=np.random.choice(T,T,replace=True)
        try: cb,_,_,_=lstsq(X_full[idx],revenue[idx],rcond=None); beta_boot[b]=np.abs(cb[1:1+len(channels)])
        except: beta_boot[b]=beta_means
    beta_stds = beta_boot.std(axis=0)
    y_pred = X_full @ coeffs
    contributions = {}; total_media=0
    for c, ch in enumerate(channels):
        contrib=max(0,float(beta_means[c]*X[:,c].sum())); total_media+=contrib
        contributions[ch]={"contribution":round(contrib,0),"beta_mean":round(float(beta_means[c]),4),
            "beta_std":round(float(beta_stds[c]),4),"decay_mean":best_decays[ch],
            "spend":round(float(data["spend_matrix"][ch].sum()),0)}
    total_rev=float(revenue.sum()); bl=max(0,total_rev-total_media)
    for ch in channels:
        cc=contributions[ch]; cc["contribution_pct"]=round(cc["contribution"]/max(total_rev,1)*100,1)
        cc["mmm_roas"]=round(cc["contribution"]/max(cc["spend"],1),2)
        ci_w=cc["beta_std"]/max(cc["beta_mean"],0.001)
        cc["confidence"]="High" if ci_w<0.3 else ("Medium" if ci_w<0.6 else "Low")
    return {"method":"ols_bootstrap","contributions":contributions,
        "baseline_contribution":round(bl,0),"baseline_pct":round(bl/max(total_rev,1)*100,1),
        "total_revenue":round(total_rev,0),
        "model_diagnostics":{"r_squared":round(float(r2_score(revenue,y_pred)),4),
            "mape":round(float(mean_absolute_percentage_error(revenue,y_pred)*100),2),
            "n_bootstrap":n_boot,"n_periods":T,
            "warning":"OLS fallback — no Bayesian uncertainty. CIs are bootstrap approximations."},
        "fitted_values":y_pred.tolist(),"actual_values":revenue.tolist(),
        "channels":channels,"periods":[str(p) for p in data["periods"]]}

def run_mmm(df, method="auto", n_draws=1000):
    """Public API: run MMM with auto-fallback. bayesian → ols."""
    data = prepare_mmm_data(df)
    if data["n_periods"]<6: logger.warning(f"Only {data['n_periods']} periods — MMM needs 12+ for reliability")
    if method=="auto":
        try:
            result = fit_bayesian_mmm(data, n_draws=n_draws)
            logger.info(f"Bayesian MMM: R²={result['model_diagnostics']['r_squared']:.3f}")
            return _finalize(result)
        except Exception as e:
            logger.warning(f"Bayesian failed ({e}), using OLS")
        return _finalize(fit_ols_mmm(data))
    elif method=="bayesian": return _finalize(fit_bayesian_mmm(data, n_draws=n_draws))
    elif method=="ols": return _finalize(fit_ols_mmm(data))
    else: raise ValueError(f"Unknown method: {method}")

def _finalize(r):
    if "contributions" in r:
        sc = sorted(r["contributions"].items(), key=lambda x:x[1]["contribution"], reverse=True)
        r["ranked_contributions"] = [{"rank":i+1,"channel":ch,**info} for i,(ch,info) in enumerate(sc)]
    return r
