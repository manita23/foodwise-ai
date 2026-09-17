"""Data access layer — wraps SQLAlchemy queries."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.database import Meal, Consumption, WasteRecord, Headcount, Recommendation


# ── Meals ─────────────────────────────────────────────────────────────────

def create_meal(db: Session, meal_date: str, meal_type: str,
                menu_items: str = "", confirmed: int = 0, estimated: int = 0) -> Meal:
    meal = Meal(meal_date=meal_date, meal_type=meal_type, menu_items=menu_items)
    db.add(meal)
    db.flush()
    hc = Headcount(meal_id=meal.id, confirmed=confirmed, estimated=estimated)
    db.add(hc)
    db.commit()
    db.refresh(meal)
    return meal


def list_meals(db: Session, limit: int = 50) -> List[Meal]:
    return db.query(Meal).order_by(Meal.meal_date.desc()).limit(limit).all()


# ── Consumption ───────────────────────────────────────────────────────────

def add_consumption(db: Session, meal_id: int, item_name: str, quantity_kg: float) -> Consumption:
    c = Consumption(meal_id=meal_id, item_name=item_name, quantity_kg=quantity_kg)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def get_consumption_history(db: Session, meal_type: str,
                             item_name: Optional[str] = None,
                             days: int = 60) -> List[Consumption]:
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    q = (
        db.query(Consumption)
        .join(Meal)
        .filter(Meal.meal_type == meal_type, Meal.meal_date >= since)
    )
    if item_name:
        q = q.filter(Consumption.item_name == item_name)
    return q.order_by(Meal.meal_date.asc()).all()


# ── Waste ─────────────────────────────────────────────────────────────────

def add_waste(db: Session, meal_id: int, item_name: str, waste_kg: float,
              waste_category: str = "plate_waste", notes: str = "") -> WasteRecord:
    w = WasteRecord(
        meal_id=meal_id, item_name=item_name, waste_kg=waste_kg,
        waste_category=waste_category, notes=notes,
    )
    db.add(w)
    db.commit()
    db.refresh(w)
    return w


def list_waste(db: Session, days: int = 30) -> List[WasteRecord]:
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    return (
        db.query(WasteRecord)
        .join(Meal)
        .filter(Meal.meal_date >= since)
        .order_by(WasteRecord.recorded_at.desc())
        .all()
    )


def get_trends(db: Session, days: int = 7):
    """Return per-day totals for waste and consumption — two aggregation queries."""
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")

    waste_rows = (
        db.query(Meal.meal_date, func.sum(WasteRecord.waste_kg).label("total"))
        .join(WasteRecord, WasteRecord.meal_id == Meal.id)
        .filter(Meal.meal_date >= since)
        .group_by(Meal.meal_date)
        .all()
    )
    cons_rows = (
        db.query(Meal.meal_date, func.sum(Consumption.quantity_kg).label("total"))
        .join(Consumption, Consumption.meal_id == Meal.id)
        .filter(Meal.meal_date >= since)
        .group_by(Meal.meal_date)
        .all()
    )

    waste_by_day: dict = defaultdict(float)
    cons_by_day: dict = defaultdict(float)
    for row in waste_rows:
        waste_by_day[row.meal_date] = float(row.total or 0)
    for row in cons_rows:
        cons_by_day[row.meal_date] = float(row.total or 0)

    all_dates = sorted(set(list(waste_by_day.keys()) + list(cons_by_day.keys())))
    result = []
    for d in all_dates:
        w = round(waste_by_day[d], 2)
        c = round(cons_by_day[d], 2)
        pct = round((w / c * 100) if c > 0 else 0.0, 1)
        result.append({"date": d, "total_waste_kg": w, "total_consumption_kg": c, "waste_pct": pct})
    return result


# ── Recommendations ───────────────────────────────────────────────────────

def create_recommendation(db: Session, recommendation: str, rationale: str = "",
                           meal_id: Optional[int] = None) -> Recommendation:
    r = Recommendation(recommendation=recommendation, rationale=rationale, meal_id=meal_id)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def list_recommendations(db: Session, status: Optional[str] = None) -> List[Recommendation]:
    q = db.query(Recommendation).order_by(Recommendation.created_at.desc())
    if status:
        q = q.filter(Recommendation.status == status)
    return q.all()


def review_recommendation(db: Session, rec_id: int, status: str, reviewed_by: str) -> Optional[Recommendation]:
    r = db.query(Recommendation).filter(Recommendation.id == rec_id).first()
    if not r:
        return None
    r.status = status
    r.reviewed_by = reviewed_by
    r.reviewed_at = datetime.utcnow()
    db.commit()
    db.refresh(r)
    return r
