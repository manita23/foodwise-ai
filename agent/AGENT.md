# FoodWise AI — Bob agent configuration
#
# This directory holds prompt templates and agent configuration used
# when IBM Bob assists with developing and maintaining this project.

## Agent responsibilities

The Bob agent for FoodWise AI assists with:

1. **Code generation** — Implementing service stubs described in
   `docs/SERVICE_STUBS.md` following the patterns in `docs/ARCHITECTURE.md`.

2. **Schema migrations** — Generating SQL migration scripts consistent
   with `data/seeds/schema.sql`.

3. **RAG ingestion** — Writing the document chunking and embedding
   pipeline in `rag/ingestion/ingest.py`.

4. **Test generation** — Writing pytest unit tests for backend services
   and integration tests for API routes.

5. **Documentation** — Updating `docs/` when new components are added.

## Constraints for the agent

- Do NOT call IBM services or APIs that are not listed in `README.md`.
- Do NOT bypass the human approval step for recommendations.
- All watsonx.ai calls must use the model IDs in `.env.example`.
- Secrets must come from environment variables, never hardcoded.
- Follow the repository layout defined in `README.md` exactly.
