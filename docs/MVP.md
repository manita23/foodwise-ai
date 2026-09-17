# FoodWise AI — Minimum Viable Product

The MVP is the smallest working slice that proves the value proposition:
forecast demand → surface potential waste → let the admin ask why →
track the outcome.

## MVP scope

| # | Feature | Included? | Notes |
|---|---|---|---|
| 1 | Record historical meal consumption | ✅ | CSV import + manual entry form |
| 2 | Demand forecast for next meal window | ✅ | Granite TTM via watsonx.ai |
| 3 | Surplus estimate (forecast − headcount) | ✅ | Computed in backend |
| 4 | Simple dashboard (today + 7-day trend) | ✅ | React, 2 charts |
| 5 | Q&A with Granite (kitchen questions) | ✅ | Chat API + basic RAG |
| 6 | Policy RAG with 2–3 seed documents | ✅ | Food safety + catering policy |
| 7 | Recommendation approval queue | ✅ | Approve / reject buttons |
| 8 | Multi-facility / multi-kitchen | ❌ | Phase 2 |
| 9 | Allergen tracking | ❌ | Phase 2 |
| 10 | Redistribution partner integration | ❌ | Phase 3 |
| 11 | Mobile app | ❌ | Phase 3 |
| 12 | Fine-tuned Granite model | ❌ | Phase 3 (needs data volume) |

## MVP build order

### Phase 0 — Skeleton (no AI)
- [ ] FastAPI project with `/health` route
- [ ] PostgreSQL schema + seed data
- [ ] React app with hard-coded dashboard layout
- [ ] `.env` config plumbing

### Phase 1 — Forecasting
- [ ] Historical data import (CSV → PostgreSQL)
- [ ] `ForecastingService` calling Granite TTM API
- [ ] `/api/v1/forecast` route
- [ ] Dashboard "Next meal demand" card (real data)

### Phase 2 — Waste recording + trends
- [ ] Waste entry form (frontend)
- [ ] `/api/v1/waste` POST + GET routes
- [ ] 7-day waste trend chart on dashboard

### Phase 3 — Q&A + RAG
- [ ] Document ingestion pipeline (2–3 PDF docs)
- [ ] Chroma vector store (local)
- [ ] `RAGService` + `AIService` wired to Granite chat
- [ ] Q&A page on frontend (question box → streamed answer)

### Phase 4 — Recommendations + oversight
- [ ] Recommendation schema in DB
- [ ] AI service writes `pending` recommendations
- [ ] Approval Queue page (list, approve, reject)
- [ ] Dashboard alert badge for pending items

## Success criteria for MVP

1. A kitchen admin can import a week of historical data and receive a
   next-meal demand forecast in under 10 seconds.
2. The admin can type "Is it safe to serve rice that has been in the
   bain-marie for 4 hours?" and receive a Granite answer grounded in
   the uploaded food-safety policy document.
3. Every AI recommendation appears in the Approval Queue and cannot
   be acted on without a human sign-off.
4. The system runs locally (laptop) with only an active watsonx.ai
   API key and a local PostgreSQL instance.
