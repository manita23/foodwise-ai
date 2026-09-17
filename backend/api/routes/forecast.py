"""POST /api/v1/forecast"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.models.database import get_db
from backend.models.schemas import ForecastRequest, ForecastResponse, ForecastPoint
from backend.services.data import repository
from backend.services.forecasting.granite_ttm import run_forecast
from backend.config.settings import get_settings

router = APIRouter(prefix="/forecast", tags=["forecast"])
settings = get_settings()


@router.post("", response_model=ForecastResponse)
def forecast(req: ForecastRequest, db: Session = Depends(get_db)):
    # Pull history from DB
    records = repository.get_consumption_history(
        db, meal_type=req.meal_type, item_name=req.item_name, days=90
    )

    history = [r.quantity_kg for r in records]
    time_series = [
        {"date": r.recorded_at.isoformat(), "consumption_kg": r.quantity_kg}
        for r in records
    ]

    # Average headcount over the same window
    meal_ids = list({r.meal_id for r in records})
    avg_headcount = 200.0  # fallback
    if meal_ids:
        from backend.models.database import Headcount
        hcs = (
            db.query(Headcount)
            .filter(Headcount.meal_id.in_(meal_ids))
            .all()
        )
        if hcs:
            avg_headcount = sum((h.confirmed or h.estimated) for h in hcs) / len(hcs)

    # If no history, generate synthetic baseline so mock mode always returns data
    if not history:
        import math, random
        history = [30 + 10 * math.sin(i * 0.4) + random.uniform(-2, 2) for i in range(30)]
        time_series = []

    raw_points, model_used = run_forecast(
        history=history,
        time_series=time_series,
        horizon=req.horizon_meals,
        avg_headcount=avg_headcount,
    )

    forecast_points = [
        ForecastPoint(
            label=f"Meal +{p['step']}",
            predicted_kg=p["predicted_kg"],
            surplus_kg=p["surplus_kg"],
        )
        for p in raw_points
    ]

    return ForecastResponse(
        meal_type=req.meal_type,
        forecast=forecast_points,
        model_used=model_used,
        mode=settings.ai_mode,
    )
