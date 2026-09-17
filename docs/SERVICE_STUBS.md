# FoodWise AI — service stubs
# This file documents what each Python service module will contain.
# Actual implementation happens in the build phases described in docs/MVP.md.

# ── backend/services/forecasting/granite_ttm.py ────────────────────────────
#
# class GraniteTTMService:
#   """
#   Wraps the watsonx.ai Forecast API.
#
#   API endpoint (zero-shot, no deployment needed):
#     POST {WATSONX_URL}/ml/v1/wx_data/time_series/forecast?version=2024-11-14
#
#   Required headers:
#     Authorization: Bearer <IAM token>
#     Content-Type: application/json
#
#   Minimal request body:
#     {
#       "model_id": "ibm/granite-ttm-512-96-r2",
#       "project_id": "<WATSONX_PROJECT_ID>",
#       "schema": {
#         "timestamp_column": "date",
#         "target_columns": ["consumption_kg"]
#       },
#       "data": [
#         {"date": "2024-01-01T07:00:00", "consumption_kg": 45.2},
#         ...   (min 512 rows for the 512-96-r2 model)
#       ]
#     }
#
#   The model returns 96 forecast points per channel by default.
#   The service trims the result to the requested horizon (e.g. next 3 meals).
#   """
#
#   def forecast(self, time_series: list[dict], horizon: int) -> list[dict]:
#       ...

# ── backend/services/ai/granite_chat.py ────────────────────────────────────
#
# class GraniteChatService:
#   """
#   Wraps the watsonx.ai Chat API.
#
#   API endpoint:
#     POST {WATSONX_URL}/ml/v1/text/chat?version=2024-11-14
#
#   Uses model: ibm/granite-3-3-8b-instruct (supports tool calling + RAG)
#
#   The system prompt:
#     - Instructs the model to ground answers in the provided context.
#     - Instructs the model NEVER to make food-safety decisions
#       autonomously; always surface them as recommendations.
#     - Instructs the model to cite source document titles.
#   """
#
#   def answer(self, question: str, context_chunks: list[str],
#              kitchen_data: dict) -> dict:
#       ...  # returns {"answer": str, "sources": list[str], "recommendation": dict | None}

# ── backend/services/rag/retriever.py ──────────────────────────────────────
#
# class RAGRetriever:
#   """
#   1. Embeds the query via watsonx.ai Embeddings API
#      POST {WATSONX_URL}/ml/v1/text/embeddings?version=2024-11-14
#      model_id: ibm/granite-embedding-278m-multilingual
#
#   2. Queries the vector store (Chroma locally, Elasticsearch in prod)
#      for the top-k most similar chunks.
#
#   3. Optionally re-ranks with watsonx.ai Rerank API
#      POST {WATSONX_URL}/ml/v1/text/rerank?version=2024-11-14
#
#   4. Returns the top chunks as plain text strings.
#   """
#
#   def retrieve(self, query: str, top_k: int = 4) -> list[str]:
#       ...

# ── backend/services/data/consumption_repo.py ──────────────────────────────
#
# class ConsumptionRepository:
#   """Read / write meal consumption records from PostgreSQL."""
#
#   def get_time_series(self, meal_type: str, days: int) -> list[dict]:
#       ...
#
#   def record_waste(self, waste: WasteRecord) -> None:
#       ...

# ── rag/ingestion/ingest.py ─────────────────────────────────────────────────
#
# Stand-alone script run once (or when new policy docs are added).
#
# Steps:
#   1. Load PDF / Markdown files from rag/documents/
#   2. Split into chunks (512 tokens, 64-token overlap) with LangChain
#   3. Embed each chunk using GraniteChatService.embed()
#   4. Upsert into Chroma (or Elasticsearch) with source metadata
#
# Run with:   python scripts/ingest_docs.py
