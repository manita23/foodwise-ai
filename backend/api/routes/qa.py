"""POST /api/v1/qa"""
import json
import re

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.models.database import get_db
from backend.models.schemas import QARequest, QAResponse
from backend.services.data import repository
from backend.services.rag.retriever import retrieve
from backend.services.ai.granite_chat import ask
from backend.config.settings import get_settings

router = APIRouter(prefix="/qa", tags=["qa"])
settings = get_settings()

_REC_RE = re.compile(r"RECOMMENDATION:\s*(\{.*?\})", re.DOTALL)


@router.post("", response_model=QAResponse)
def qa(req: QARequest, db: Session = Depends(get_db)):
    # 1. Retrieve RAG context
    context_chunks = retrieve(req.question, top_k=4)

    # 2. Gather lightweight kitchen snapshot
    trends = repository.get_trends(db, days=7)
    kitchen_data = {"7_day_waste_trend": trends[-3:] if trends else []}

    # 3. Ask Granite
    result = ask(
        question=req.question,
        context_chunks=context_chunks,
        kitchen_data=kitchen_data,
    )

    answer: str = result["answer"]
    sources: list = result["sources"]
    rec_created = False

    # 4. If model surfaced a recommendation, persist it (pending approval)
    if result.get("has_recommendation"):
        match = _REC_RE.search(answer)
        rec_text = req.question  # fallback
        rationale = ""
        if match:
            try:
                rec_json = json.loads(match.group(1))
                rec_text = rec_json.get("action", rec_text)
                rationale = rec_json.get("rationale", "")
            except json.JSONDecodeError:
                pass
        repository.create_recommendation(db, recommendation=rec_text, rationale=rationale)
        rec_created = True

    return QAResponse(
        answer=answer,
        sources=sources,
        recommendation_created=rec_created,
        mode=settings.ai_mode,
    )
