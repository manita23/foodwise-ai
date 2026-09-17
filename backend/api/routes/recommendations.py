"""
GET  /api/v1/recommendations
POST /api/v1/recommendations/{id}/approve
POST /api/v1/recommendations/{id}/reject
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.models.database import get_db
from backend.models.schemas import RecommendationOut, ReviewRequest
from backend.services.data import repository

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=List[RecommendationOut])
def list_recommendations(
    status: Optional[str] = Query(None, pattern="^(pending|approved|rejected)$"),
    db: Session = Depends(get_db),
):
    return repository.list_recommendations(db, status=status)


@router.post("/{rec_id}/approve", response_model=RecommendationOut)
def approve(rec_id: int, body: ReviewRequest, db: Session = Depends(get_db)):
    rec = repository.review_recommendation(db, rec_id, "approved", body.reviewed_by)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return rec


@router.post("/{rec_id}/reject", response_model=RecommendationOut)
def reject(rec_id: int, body: ReviewRequest, db: Session = Depends(get_db)):
    rec = repository.review_recommendation(db, rec_id, "rejected", body.reviewed_by)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return rec
