"""
Granite Chat service.

mock mode → returns a canned, context-aware response.
real mode → calls the watsonx.ai Chat API (granite-3-3-8b-instruct).
"""
from __future__ import annotations

from typing import List, Optional

import httpx

from backend.config.settings import get_settings

settings = get_settings()

_CHAT_URL = (
    f"{settings.watsonx_url}/ml/v1/text/chat"
    "?version=2024-11-14"
)

_SYSTEM_PROMPT = """You are FoodWise AI, a decision-support assistant for \
institutional kitchens. Your job is to help kitchen administrators reduce \
food waste and manage food safety.

Rules:
1. Ground every answer in the provided context documents.
2. When answering a food-safety question, cite the relevant policy document.
3. NEVER make a food-safety decision autonomously. Always state that the \
final decision rests with the kitchen administrator.
4. If your answer implies a concrete operational change (e.g. reduce \
preparation quantity, discard food, alter storage), end your response with \
a JSON block starting with RECOMMENDATION: followed by a single JSON object \
with keys "action" and "rationale".
5. Be concise and practical."""


def _mock_answer(question: str, context_chunks: List[str]) -> dict:
    """Return a deterministic mock answer."""
    q_lower = question.lower()

    if any(w in q_lower for w in ["rice", "bain-marie", "hours", "safe", "discard"]):
        answer = (
            "According to the uploaded food safety guidelines, cooked rice kept "
            "in a bain-marie above 63 °C is safe for up to 2 hours. After 4 hours "
            "it must be discarded — it cannot be reheated and served again.\n\n"
            "**The final decision rests with the kitchen administrator.**\n\n"
            "RECOMMENDATION: {\"action\": \"Discard rice that has been in the "
            "bain-marie for more than 2 hours\", \"rationale\": \"Food safety "
            "policy prohibits holding cooked rice above the 2-hour limit.\"}"
        )
        sources = ["food_safety_guidelines.pdf — Section 4.2 Hot Holding"]
    elif any(w in q_lower for w in ["surplus", "leftover", "reduce", "less", "waste"]):
        answer = (
            "Based on the last 7 days of consumption data, lunch rice is "
            "consistently over-prepared by approximately 8 %. I recommend reducing "
            "tomorrow's rice preparation by 5 kg as a conservative first step.\n\n"
            "RECOMMENDATION: {\"action\": \"Reduce rice preparation for tomorrow's "
            "lunch by 5 kg\", \"rationale\": \"7-day trend shows 8 % consistent "
            "surplus; a 5 kg reduction is a safe starting adjustment.\"}"
        )
        sources = ["catering_policy.pdf — Section 2.1 Waste Reduction Targets"]
    elif any(w in q_lower for w in ["allergen", "nut", "gluten", "dairy"]):
        answer = (
            "Under the institutional allergen handling procedure, all menu items "
            "containing the 14 major allergens must be clearly labelled on the "
            "serving counter. Staff must use separate utensils for allergen-free "
            "portions. Please consult the Allergen Register before service.\n\n"
            "**The final decision rests with the kitchen administrator.**"
        )
        sources = ["allergen_procedures.md — Section 1 Labelling Requirements"]
    else:
        answer = (
            "I can help with food-waste reduction, demand forecasting insights, "
            "food safety questions, and institutional catering policy. "
            "Could you be more specific about what you need?\n\n"
            "Examples:\n"
            '- "Is it safe to serve rice held for 4 hours?"\n'
            '- "How can I reduce lunch waste this week?"\n'
            '- "What are our allergen labelling requirements?"'
        )
        sources = []

    has_recommendation = "RECOMMENDATION:" in answer
    return {"answer": answer, "sources": sources, "has_recommendation": has_recommendation}


def _real_answer(question: str, context_chunks: List[str], kitchen_data: dict) -> dict:
    """Call the watsonx.ai Chat API."""
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

    context_text = "\n\n".join(context_chunks) if context_chunks else "No policy documents loaded."
    kitchen_text = str(kitchen_data) if kitchen_data else "No kitchen data available."

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"CONTEXT DOCUMENTS:\n{context_text}\n\n"
                f"CURRENT KITCHEN DATA:\n{kitchen_text}\n\n"
                f"QUESTION: {question}"
            ),
        },
    ]

    resp = httpx.post(
        _CHAT_URL,
        json={
            "model_id": settings.granite_chat_model,
            "project_id": settings.watsonx_project_id,
            "messages": messages,
            "parameters": {"max_new_tokens": 512, "temperature": 0.3},
        },
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    answer = data["choices"][0]["message"]["content"]
    has_recommendation = "RECOMMENDATION:" in answer
    return {"answer": answer, "sources": [], "has_recommendation": has_recommendation}


def ask(
    question: str,
    context_chunks: Optional[List[str]] = None,
    kitchen_data: Optional[dict] = None,
) -> dict:
    if settings.ai_mode == "real":
        return _real_answer(question, context_chunks or [], kitchen_data or {})
    return _mock_answer(question, context_chunks or [])
