"""GET /api/v1/waste  POST /api/v1/waste  GET /api/v1/waste/trends"""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.models.database import get_db
from backend.models.schemas import WasteCreate, WasteOut, TrendsResponse, TrendPoint
from backend.services.data import repository

router = APIRouter(prefix="/waste", tags=["waste"])


@router.get("", response_model=List[WasteOut])
def list_waste(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    return repository.list_waste(db, days=days)


@router.post("", response_model=WasteOut, status_code=201)
def record_waste(body: WasteCreate, db: Session = Depends(get_db)):
    return repository.add_waste(
        db,
        meal_id=body.meal_id,
        item_name=body.item_name,
        waste_kg=body.waste_kg,
        waste_category=body.waste_category or "plate_waste",
        notes=body.notes or "",
    )


@router.get("/trends", response_model=TrendsResponse)
def waste_trends(days: int = Query(7, ge=1, le=90), db: Session = Depends(get_db)):
    raw = repository.get_trends(db, days=days)
    points = [TrendPoint(**r) for r in raw]
    return TrendsResponse(days=days, data=points)
