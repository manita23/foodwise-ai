"""Pydantic request / response schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# ── Meals ─────────────────────────────────────────────────────────────────

class MealCreate(BaseModel):
    meal_date: str
    meal_type: str
    menu_items: Optional[str] = ""
    headcount_confirmed: Optional[int] = 0
    headcount_estimated: Optional[int] = 0


class MealOut(BaseModel):
    id: int
    meal_date: str
    meal_type: str
    menu_items: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Consumption ───────────────────────────────────────────────────────────

class ConsumptionCreate(BaseModel):
    meal_id: int
    item_name: str
    quantity_kg: float


class ConsumptionOut(BaseModel):
    id: int
    meal_id: int
    item_name: str
    quantity_kg: float
    recorded_at: datetime

    model_config = {"from_attributes": True}


# ── Waste ─────────────────────────────────────────────────────────────────

class WasteCreate(BaseModel):
    meal_id: int
    item_name: str
    waste_kg: float
    waste_category: Optional[str] = "plate_waste"
    notes: Optional[str] = ""


class WasteOut(BaseModel):
    id: int
    meal_id: int
    item_name: str
    waste_kg: float
    waste_category: str
    notes: Optional[str]
    recorded_at: datetime

    model_config = {"from_attributes": True}


# ── Forecast ──────────────────────────────────────────────────────────────

class ForecastRequest(BaseModel):
    meal_type: str = "lunch"
    horizon_meals: int = 3          # how many future meals to forecast
    item_name: Optional[str] = None # None = all items


class ForecastPoint(BaseModel):
    label: str
    predicted_kg: float
    surplus_kg: float


class ForecastResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    meal_type: str
    forecast: List[ForecastPoint]
    model_used: str
    mode: str  # "mock" | "real"


# ── Q&A ───────────────────────────────────────────────────────────────────

class QARequest(BaseModel):
    question: str


class QAResponse(BaseModel):
    answer: str
    sources: List[str]
    recommendation_created: bool
    mode: str


# ── Recommendations ───────────────────────────────────────────────────────

class RecommendationOut(BaseModel):
    id: int
    meal_id: Optional[int]
    source: str
    recommendation: str
    rationale: str
    status: str
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewRequest(BaseModel):
    reviewed_by: str = "admin"


# ── Trends ────────────────────────────────────────────────────────────────

class TrendPoint(BaseModel):
    date: str
    total_waste_kg: float
    total_consumption_kg: float
    waste_pct: float


class TrendsResponse(BaseModel):
    days: int
    data: List[TrendPoint]


# ── CSV Import ────────────────────────────────────────────────────────────

class ImportResult(BaseModel):
    rows_imported: int
    meals_created: int
    message: str
