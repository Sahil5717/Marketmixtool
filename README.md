# Yield Intelligence Platform
### Marketing ROI & Budget Optimization Engine

## Quick Start (Local)
```bash
cd backend && pip install -r requirements.txt
uvicorn api:app --reload --port 8000
```
- **Frontend:** http://localhost:8000/app
- **API Docs:** http://localhost:8000/docs

## Deploy to Railway
1. Push to GitHub: `git init && git add . && git commit -m "init" && git push`
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select repo → Railway auto-detects Dockerfile → deploys
4. Access: `https://your-app.railway.app/app`

## 16 Engines | 29 API Endpoints | 10 Screens | 22 Models

### Phase 1: Measurement & Optimization
Attribution (3 models), Response curves, Constrained optimizer, Diagnostics, Leakage, Trend analysis, Funnel analysis, ROI formulas (5), Data validation, Column mapping

### Phase 2: Intelligence  
Bayesian MMM (PyMC), Adstock/carryover, Prophet/ARIMA, Markov chain attribution, Cross-channel leakage

### Phase 3: Maturity
Shapley values, Multi-objective optimization, Geo-lift testing, Hierarchical forecasting, Automated recommendations, Model drift detection
