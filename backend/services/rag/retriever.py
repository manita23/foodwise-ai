"""
RAG retriever.

mock mode → returns hardcoded context chunks so Q&A works without a
             vector store or embedding API.
real mode → embeds the query via watsonx.ai Embeddings API and
             queries Chroma.
"""
from __future__ import annotations

from typing import List

from backend.config.settings import get_settings

settings = get_settings()

_MOCK_CHUNKS = [
    (
        "[food_safety_guidelines.pdf — Section 4.2 Hot Holding]\n"
        "Cooked rice must be held at or above 63 °C. The maximum safe holding "
        "time for cooked rice in a bain-marie is 2 hours. After this period, "
        "rice must be discarded and must NOT be reheated or re-served."
    ),
    (
        "[catering_policy.pdf — Section 2.1 Waste Reduction Targets]\n"
        "The institution targets a maximum food waste of 5 % of total food "
        "prepared. Kitchens must record daily waste by category. Surplus food "
        "that passes a safety check may be redistributed to approved food banks."
    ),
    (
        "[allergen_procedures.md — Section 1 Labelling Requirements]\n"
        "All dishes containing the 14 major allergens (gluten, crustaceans, "
        "eggs, fish, peanuts, soybeans, milk, nuts, celery, mustard, sesame, "
        "sulphites, lupin, molluscs) must be clearly labelled on the serving "
        "counter. Separate serving utensils must be used for allergen-free portions."
    ),
    (
        "[surplus_redistribution.md — Section 3 Eligibility]\n"
        "Only food that has been held at the correct temperature for less than "
        "2 hours is eligible for redistribution. A supervisor must sign off on "
        "the redistribution form before food leaves the kitchen."
    ),
]


def _mock_retrieve(query: str, top_k: int = 4) -> List[str]:
    """Return all mock chunks (in a real system these are ranked by similarity)."""
    return _MOCK_CHUNKS[:top_k]


def _real_retrieve(query: str, top_k: int = 4) -> List[str]:
    """
    Embed query via watsonx.ai Embeddings API, then query Chroma.
    Requires the ingestion pipeline to have been run first.
    """
    import chromadb
    import httpx

    # Embed the query
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

    embed_url = f"{settings.watsonx_url}/ml/v1/text/embeddings?version=2024-11-14"
    embed_resp = httpx.post(
        embed_url,
        json={
            "model_id": settings.granite_embed_model,
            "project_id": settings.watsonx_project_id,
            "inputs": [{"text": query}],
        },
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        timeout=30,
    )
    embed_resp.raise_for_status()
    query_embedding = embed_resp.json()["results"][0]["embedding"]

    # Query Chroma
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    collection = client.get_or_create_collection("foodwise_rag")
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas"],
    )
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    chunks = []
    for doc, meta in zip(docs, metas):
        source = meta.get("source", "unknown")
        chunks.append(f"[{source}]\n{doc}")
    return chunks


def retrieve(query: str, top_k: int = 4) -> List[str]:
    if settings.ai_mode == "real":
        return _real_retrieve(query, top_k)
    return _mock_retrieve(query, top_k)
