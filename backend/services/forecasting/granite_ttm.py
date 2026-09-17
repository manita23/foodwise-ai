"""
Forecasting service.

In mock mode  → returns a deterministic sinusoidal forecast so the UI
                looks realistic without any API call.
In real mode  → calls the watsonx.ai Forecast API with Granite TTM.
"""
from __future__ import annotations

import math
import random
from typing import List

import httpx

from backend.config.settings import get_settings

settings = get_settings()

# watsonx.ai Forecast API endpoint
_FORECAST_URL = (
    f"{settings.watsonx_url}/ml/v1/wx_data/time_series/forecast"
    "?version=2024-11-14"
)


def _mock_forecast(
    history: List[float], horizon: int, avg_headcount: float
) -> List[dict]:
    """Return a plausible-looking sinusoidal forecast."""
    base = sum(history[-10:]) / max(len(history[-10:]), 1) if history else 30.0
    result = []
    for i in range(horizon):
        noise = random.uniform(-0.05, 0.05)
        wave = math.sin(i * 0.8) * 0.08
        predicted = round(base * (1 + wave + noise), 2)
        portion_kg = base / max(avg_headcount, 1)
        surplus = round(predicted - avg_headcount * portion_kg, 2)
        result.append(
            {
                "step": i + 1,
                "predicted_kg": max(predicted, 0),
                "surplus_kg": surplus,
            }
        )
    return result


def _real_forecast(
    time_series: List[dict], horizon: int, avg_headcount: float
) -> List[dict]:
    """
    Call watsonx.ai Forecast API.
    Requires at least 512 data points per channel for granite-ttm-512-96-r2.
    """
    # Obtain IAM bearer token
    iam_resp = httpx.post(
        "https://iam.cloud.ibm.com/identity/token",
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": settings.watsonx_api_key,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    iam_resp.raise_for_status()
    token = iam_resp.json()["access_token"]

    payload = {
        "model_id": settings.granite_ttm_model,
        "project_id": settings.watsonx_project_id,
        "schema": {
            "timestamp_column": "date",
            "target_columns": ["consumption_kg"],
        },
        "data": time_series,
        "parameters": {"prediction_length": horizon},
    }
    resp = httpx.post(
        _FORECAST_URL,
        json=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        timeout=60,
    )
    resp.raise_for_status()
    raw = resp.json()

    # Parse the 96-point response and return only `horizon` points
    forecast_values = (
        raw.get("results", [{}])[0]
        .get("forecast", {})
        .get("consumption_kg", [])[:horizon]
    )
    results = []
    for i, val in enumerate(forecast_values):
        portion_kg = val / max(avg_headcount, 1)
        surplus = round(val - avg_headcount * portion_kg, 2)
        results.append(
            {
                "step": i + 1,
                "predicted_kg": round(val, 2),
                "surplus_kg": surplus,
            }
        )
    return results


def run_forecast(
    history: List[float],
    time_series: List[dict],
    horizon: int,
    avg_headcount: float,
) -> tuple[List[dict], str]:
    """
    Returns (forecast_points, model_name).
    Chooses mock vs real based on settings.ai_mode.
    """
    if settings.ai_mode == "real":
        return _real_forecast(time_series, horizon, avg_headcount), settings.granite_ttm_model
    return _mock_forecast(history, horizon, avg_headcount), f"{settings.granite_ttm_model} [mock]"
