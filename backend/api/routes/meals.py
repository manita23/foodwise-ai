"""
GET  /api/v1/meals
POST /api/v1/meals
POST /api/v1/meals/import  — bulk CSV import
"""
import csv
import io
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from backend.models.database import get_db
from backend.models.schemas import MealCreate, MealOut, ConsumptionCreate, ConsumptionOut, ImportResult
from backend.services.data import repository

router = APIRouter(prefix="/meals", tags=["meals"])


@router.get("", response_model=List[MealOut])
def list_meals(db: Session = Depends(get_db)):
    return repository.list_meals(db)


@router.post("", response_model=MealOut, status_code=201)
def create_meal(body: MealCreate, db: Session = Depends(get_db)):
    return repository.create_meal(
        db,
        meal_date=body.meal_date,
        meal_type=body.meal_type,
        menu_items=body.menu_items or "",
        confirmed=body.headcount_confirmed or 0,
        estimated=body.headcount_estimated or 0,
    )


@router.post("/import", response_model=ImportResult)
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Accept a CSV with columns:
      date, meal_type, item_name, consumption_kg, headcount
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted")

    content = await file.read()
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    meal_cache: dict = {}   # (date, meal_type) → meal_id
    rows_imported = 0
    meals_created = 0

    for row in reader:
        key = (row["date"].strip(), row["meal_type"].strip())
        if key not in meal_cache:
            meal = repository.create_meal(
                db,
                meal_date=key[0],
                meal_type=key[1],
                confirmed=int(float(row.get("headcount", 0))),
                estimated=int(float(row.get("headcount", 0))),
            )
            meal_cache[key] = meal.id
            meals_created += 1

        repository.add_consumption(
            db,
            meal_id=meal_cache[key],
            item_name=row["item_name"].strip(),
            quantity_kg=float(row["consumption_kg"]),
        )
        rows_imported += 1

    return ImportResult(
        rows_imported=rows_imported,
        meals_created=meals_created,
        message=f"Imported {rows_imported} consumption rows across {meals_created} meals.",
    )


@router.post("/consumption", response_model=ConsumptionOut, status_code=201)
def add_consumption(body: ConsumptionCreate, db: Session = Depends(get_db)):
    return repository.add_consumption(db, body.meal_id, body.item_name, body.quantity_kg)
