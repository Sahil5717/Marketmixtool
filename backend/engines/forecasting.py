"""
Time-Series Forecasting Engine (Phase 2)
Prophet and ARIMA models for next-year revenue/spend/conversion prediction.

Two methods:
1. Prophet (preferred) — handles seasonality, holidays, trend changes
2. ARIMA (fallback) — classical time-series via statsmodels
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings("ignore")


def forecast_prophet(
    df: pd.DataFrame,
    metric: str = "revenue",
    periods: int = 12,
    freq: str = "MS",
) -> Dict:
    """
    Forecast using Facebook Prophet.
    Returns point forecast + confidence intervals.
    """
    try:
        from prophet import Prophet
        
        # Prepare data
        monthly = df.groupby("month" if "month" in df.columns else "date").agg(
            **{metric: (metric, "sum")}
        ).reset_index()
        
        time_col = "month" if "month" in df.columns else "date"
        prophet_df = pd.DataFrame({
            "ds": pd.to_datetime(monthly[time_col]),
            "y": monthly[metric].values,
        })
        
        # Fit model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10,
        )
        model.fit(prophet_df)
        
        # Forecast
        future = model.make_future_dataframe(periods=periods, freq=freq)
        forecast = model.predict(future)
        
        # Extract results
        historical = forecast[forecast["ds"].isin(prophet_df["ds"])]
        future_only = forecast[~forecast["ds"].isin(prophet_df["ds"])]
        
        return {
            "method": "prophet",
            "metric": metric,
            "historical": {
                "dates": prophet_df["ds"].dt.strftime("%Y-%m").tolist(),
                "actual": prophet_df["y"].tolist(),
                "fitted": historical["yhat"].tolist(),
            },
            "forecast": {
                "dates": future_only["ds"].dt.strftime("%Y-%m").tolist(),
                "predicted": future_only["yhat"].tolist(),
                "lower": future_only["yhat_lower"].tolist(),
                "upper": future_only["yhat_upper"].tolist(),
            },
            "summary": {
                "forecast_total": round(float(future_only["yhat"].sum()), 0),
                "forecast_lower": round(float(future_only["yhat_lower"].sum()), 0),
                "forecast_upper": round(float(future_only["yhat_upper"].sum()), 0),
                "historical_total": round(float(prophet_df["y"].sum()), 0),
                "yoy_change_pct": round(
                    (future_only["yhat"].sum() - prophet_df["y"].sum()) / prophet_df["y"].sum() * 100, 1
                ),
                "periods_forecast": periods,
            },
        }
    except Exception as e:
        print(f"Prophet failed: {e}")
        return forecast_arima(df, metric, periods)


def forecast_arima(
    df: pd.DataFrame,
    metric: str = "revenue",
    periods: int = 12,
) -> Dict:
    """
    Forecast using ARIMA via statsmodels.
    Fallback when Prophet is unavailable.
    """
    try:
        from statsmodels.tsa.arima.model import ARIMA
        from statsmodels.tsa.stattools import adfuller
        
        monthly = df.groupby("month" if "month" in df.columns else "date").agg(
            **{metric: (metric, "sum")}
        ).reset_index().sort_values("month" if "month" in df.columns else "date")
        
        y = monthly[metric].values
        
        # Check stationarity
        adf_result = adfuller(y)
        d = 0 if adf_result[1] < 0.05 else 1
        
        # Fit ARIMA(1,d,1) — simple but robust
        model = ARIMA(y, order=(1, d, 1))
        fitted = model.fit()
        
        # Forecast
        forecast_result = fitted.get_forecast(steps=periods)
        pred_mean = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int(alpha=0.2)
        
        time_col = "month" if "month" in df.columns else "date"
        dates = monthly[time_col].tolist()
        
        # Generate future dates
        last_date = pd.to_datetime(dates[-1])
        future_dates = pd.date_range(last_date + pd.DateOffset(months=1), periods=periods, freq="MS")
        
        return {
            "method": "arima",
            "metric": metric,
            "historical": {
                "dates": [str(d) for d in dates],
                "actual": y.tolist(),
                "fitted": fitted.fittedvalues.tolist(),
            },
            "forecast": {
                "dates": future_dates.strftime("%Y-%m").tolist(),
                "predicted": pred_mean.tolist(),
                "lower": conf_int.iloc[:, 0].tolist(),
                "upper": conf_int.iloc[:, 1].tolist(),
            },
            "summary": {
                "forecast_total": round(float(pred_mean.sum()), 0),
                "forecast_lower": round(float(conf_int.iloc[:, 0].sum()), 0),
                "forecast_upper": round(float(conf_int.iloc[:, 1].sum()), 0),
                "historical_total": round(float(y.sum()), 0),
                "yoy_change_pct": round((pred_mean.sum() - y.sum()) / y.sum() * 100, 1),
                "periods_forecast": periods,
                "aic": round(float(fitted.aic), 1),
            },
        }
    except Exception as e:
        # Ultimate fallback: simple trend extrapolation
        return _simple_forecast(df, metric, periods, str(e))


def _simple_forecast(df, metric, periods, error_msg):
    """Linear trend extrapolation as last resort."""
    monthly = df.groupby("month" if "month" in df.columns else "date").agg(
        **{metric: (metric, "sum")}
    ).reset_index().sort_values("month" if "month" in df.columns else "date")
    
    y = monthly[metric].values
    x = np.arange(len(y))
    slope, intercept = np.polyfit(x, y, 1)
    
    future_x = np.arange(len(y), len(y) + periods)
    predicted = slope * future_x + intercept
    
    return {
        "method": "linear_trend_fallback",
        "metric": metric,
        "historical": {"dates": monthly.iloc[:, 0].tolist(), "actual": y.tolist(), "fitted": (slope * x + intercept).tolist()},
        "forecast": {
            "dates": [f"2026-{str(i+1).padStart(2,'0')}" for i in range(periods)],
            "predicted": predicted.tolist(),
            "lower": (predicted * 0.85).tolist(),
            "upper": (predicted * 1.15).tolist(),
        },
        "summary": {
            "forecast_total": round(float(predicted.sum()), 0),
            "historical_total": round(float(y.sum()), 0),
            "yoy_change_pct": round((predicted.sum() - y.sum()) / y.sum() * 100, 1),
            "fallback_reason": error_msg,
        },
    }


def forecast_by_channel(
    df: pd.DataFrame,
    metric: str = "revenue",
    periods: int = 12,
) -> Dict[str, Dict]:
    """Run forecasts per channel."""
    results = {}
    for ch in df["channel"].unique():
        ch_df = df[df["channel"] == ch]
        if len(ch_df.groupby("month" if "month" in ch_df.columns else "date")) < 6:
            continue
        results[ch] = forecast_prophet(ch_df, metric, periods)
    return results


def run_full_forecast(
    df: pd.DataFrame,
    periods: int = 12,
) -> Dict:
    """Run forecasts for revenue, spend, and conversions at total and channel level."""
    return {
        "revenue_forecast": forecast_prophet(df, "revenue", periods),
        "spend_forecast": forecast_prophet(df, "spend", periods),
        "channel_forecasts": forecast_by_channel(df, "revenue", periods),
    }


if __name__ == "__main__":
    from mock_data import generate_all_data
    
    data = generate_all_data()
    df = data["campaign_performance"]
    
    print("=== Revenue Forecast ===")
    rev = forecast_prophet(df, "revenue", 12)
    print(f"Method: {rev['method']}")
    print(f"Historical: ${rev['summary']['historical_total']:,.0f}")
    print(f"Forecast: ${rev['summary']['forecast_total']:,.0f} "
          f"[${rev['summary']['forecast_lower']:,.0f} - ${rev['summary']['forecast_upper']:,.0f}]")
    print(f"YoY Change: {rev['summary']['yoy_change_pct']:+.1f}%")
    
    print("\n=== Channel Forecasts ===")
    ch_fc = forecast_by_channel(df, "revenue", 12)
    for ch, fc in ch_fc.items():
        print(f"  {ch}: ${fc['summary']['forecast_total']:,.0f} ({fc['summary']['yoy_change_pct']:+.1f}%)")
