# Yield Intelligence Platform
### Omnichannel Marketing ROI & Budget Optimization Engine

An end-to-end marketing analytics tool that measures current ROI, diagnoses value leakage, and optimizes next-year budget allocation using statistical models.

---

## Quick Start (Local)

```bash
# 1. Install dependencies
cd backend && pip install -r requirements.txt

# 2. Start server
uvicorn api:app --reload --port 8000

# 3. Access
# Frontend: http://localhost:8000/app
# API Docs: http://localhost:8000/docs
# Health:   http://localhost:8000/api/health
```

## Deploy to Railway

```bash
# 1. Push to GitHub
git init && git add . && git commit -m "deploy" && git push

# 2. Go to railway.app → New Project → Deploy from GitHub
# 3. Select repo → Railway detects Dockerfile → deploys automatically
# 4. Access: https://your-app.railway.app/app
```

## Deploy with Docker

```bash
docker build -t yield-intelligence .
docker run -p 8000:8000 yield-intelligence
# Access: http://localhost:8000/app
```

---

## Architecture

```
yield-intelligence/
├── backend/
│   ├── api.py                     # FastAPI — 28 endpoints
│   ├── mock_data.py               # 48-month demo data generator
│   ├── validator.py               # Upload validation
│   ├── test_integration.py        # 69-test integration suite
│   ├── engines/
│   │   ├── response_curves.py     # scipy.optimize.curve_fit (power-law + Hill)
│   │   ├── optimizer.py           # scipy.optimize.minimize (SLSQP, multi-start)
│   │   ├── mmm.py                 # PyMC Bayesian MMM → OLS fallback
│   │   ├── adstock.py             # scipy differential_evolution (decay fitting)
│   │   ├── forecasting.py         # Prophet → ARIMA → linear fallback
│   │   ├── diagnostics.py         # scipy.stats (t-test, z-test per recommendation)
│   │   ├── leakage.py             # 3-pillar value leakage analysis
│   │   ├── attribution.py         # Last-touch, linear, position-based
│   │   ├── markov_attribution.py  # Markov chain with bootstrap CIs
│   │   ├── shapley.py             # Exact Shapley values (2^N coalitions)
│   │   ├── geo_lift.py            # Synthetic control (statsmodels OLS)
│   │   ├── trend_analysis.py      # Kendall tau, Grubbs, Levene
│   │   ├── funnel_analysis.py     # Binomial CI, proportions z-test
│   │   ├── roi_formulas.py        # 5 ROI variants with bootstrap CIs
│   │   ├── cross_channel.py       # Pearson/KS test for timing leakage
│   │   ├── multi_objective.py     # Pareto frontier optimization
│   │   ├── hierarchical_forecast.py # Per-group forecast + reconciliation
│   │   ├── automated_recs.py      # Model-driven anomaly detection
│   │   ├── mapping.py             # Auto column mapping (fuzzy match)
│   │   └── data_splitter.py       # Routes reporting vs training data
│   └── data/
│       └── upload_template.csv
├── frontend/
│   ├── app.jsx                    # React frontend (7 screens)
│   └── index.html                 # Host page
├── templates/
│   ├── INPUT_FORMAT_SPECIFICATION.md
│   ├── campaign_performance_template.csv
│   └── user_journeys_template.csv
├── docs/
│   ├── model_specification.md
│   ├── kpi_formula_spec.md
│   ├── data_dictionary.md
│   └── technology_stack.md
├── Dockerfile
├── Procfile
├── railway.toml
├── requirements.txt
└── LICENSE
```

## Data Requirements

| Purpose | Time Window | Minimum |
|---------|-------------|---------|
| ROI, KPIs, diagnostics | Last 12 months | 12 months |
| Response curves, adstock | Full history | 24 months |
| MMM (Bayesian) | Full history | 36 months |
| Forecasting | Full history | 24 months |

**Upload one file with 3–5 years of data.** The system auto-splits:
- Last 12 months → reporting (ROI, diagnostics, recommendations)
- Full history → model training (curves, MMM, forecasting)

## API Endpoints (28 total)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/health` | Deployment monitoring |
| POST | `/api/load-mock-data` | Load 48-month demo data |
| POST | `/api/upload` | Upload campaign CSV/XLSX |
| POST | `/api/upload-journeys` | Upload journey data for attribution |
| POST | `/api/run-analysis` | Run all engines |
| GET | `/api/full-state` | All data shaped for frontend |
| GET | `/api/current-state` | KPIs + channel matrix |
| GET | `/api/data-readiness` | Engine sufficiency checks |
| GET | `/api/response-curves` | Fitted curves with R², RMSE |
| GET | `/api/recommendations` | Statistical recommendations |
| GET | `/api/pillars` | Revenue leakage + CX + cost |
| POST | `/api/optimize` | Budget optimization (SLSQP) |
| GET | `/api/sensitivity` | Multi-budget sensitivity |
| GET | `/api/business-case` | Executive summary |
| GET | `/api/forecast` | Prophet/ARIMA forecast |
| POST | `/api/mmm` | Bayesian Marketing Mix Model |
| POST | `/api/adstock` | Adstock decay fitting |
| GET | `/api/markov-attribution` | Markov chain attribution |
| GET | `/api/shapley` | Shapley value attribution |
| GET | `/api/trend-analysis` | Trend + anomaly detection |
| GET | `/api/funnel-analysis` | Funnel bottleneck analysis |
| GET | `/api/roi-analysis` | 5 ROI formulas per channel |
| GET | `/api/cross-channel` | Cross-channel leakage |
| GET | `/api/geo-lift/{region}` | Synthetic control test |
| POST | `/api/multi-objective` | Pareto frontier |
| GET | `/api/hierarchical-forecast` | Per-group forecast |
| GET | `/api/automated-recommendations` | Model-driven recs |
| GET | `/api/model-health` | Model drift detection |

## Run Tests

```bash
cd backend && python test_integration.py
# Expected: 69 passed, 0 failed
```

## Statistical Libraries

| Library | Engine | Purpose |
|---------|--------|---------|
| scipy.optimize.curve_fit | Response curves | Nonlinear least-squares fitting |
| scipy.optimize.minimize | Optimizer | Constrained SLSQP with multi-start |
| scipy.optimize.differential_evolution | Adstock | Global decay parameter optimization |
| scipy.stats | All diagnostics | t-test, z-test, Kendall tau, Levene, Grubbs, KS |
| scikit-learn | Response curves, ROI | R², RMSE, MAPE, Leave-One-Out CV |
| pymc | MMM | Bayesian MCMC (NUTS sampler) |
| arviz | MMM | Posterior diagnostics (R-hat, ESS, HDI) |
| statsmodels | Forecasting, Geo-lift | ARIMA, ADF test, OLS, seasonal decomposition |
| prophet | Forecasting | Time-series with seasonality + changepoints |

## License

MIT License. See [LICENSE](LICENSE).
