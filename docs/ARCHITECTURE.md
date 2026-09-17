# FoodWise AI — Architecture

## Layer map

```
┌──────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                        │
│  React SPA (Vite + TailwindCSS)                              │
│  Pages: Dashboard · Forecast · Q&A · Waste Trends · Settings │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTPS / REST JSON
┌────────────────────────▼─────────────────────────────────────┐
│                        BACKEND LAYER                         │
│  Python 3.11 · FastAPI                                       │
│  Routes: /forecast  /qa  /waste  /recommendations            │
│  Middleware: JWT auth · request logging · CORS               │
└──┬────────┬──────────────┬──────────────────┬───────────────-┘
   │        │              │                  │
   ▼        ▼              ▼                  ▼
┌──────┐ ┌──────────┐ ┌─────────┐ ┌────────────────────────┐
│ DATA │ │FORECASTING│ │   RAG   │ │         AI LAYER       │
│LAYER │ │  LAYER   │ │  LAYER  │ │                        │
│      │ │          │ │         │ │  Granite 3.3 8b Instruct│
│Postgr│ │Granite   │ │Chroma / │ │  watsonx.ai Chat API   │
│SQL   │ │TTM via   │ │Elastic- │ │                        │
│      │ │watsonx.ai│ │search   │ │  Context assembled from│
│      │ │Forecast  │ │+ Granite│ │  DB query results +    │
│      │ │API       │ │embed.   │ │  RAG retrieved chunks  │
└──────┘ └──────────┘ └─────────┘ └────────────────────────┘
```

---

## Component descriptions

### 1. Frontend Layer

**Technology:** React 18, Vite, TailwindCSS  
**Responsibility:** Provide a simple, role-gated dashboard for
kitchen administrators.

Key pages:

| Page | Purpose |
|---|---|
| Dashboard | Today's headcount, predicted demand, waste gauge |
| Forecast | Historical vs predicted consumption charts |
| Waste Trends | Time-series charts of recorded waste by meal type |
| Q&A | Free-text question box backed by Granite + RAG |
| Approval Queue | List of pending AI recommendations awaiting sign-off |
| Settings | Meal schedule, headcount thresholds, policy documents |

All AI-generated recommendations are surfaced in the **Approval Queue**
page. A kitchen administrator must explicitly approve or reject each
recommendation before any action is taken (human-oversight requirement).

---

### 2. Backend Layer

**Technology:** Python 3.11, FastAPI  
**Responsibility:** Orchestrate all service calls; expose a clean REST
API to the frontend; enforce business rules.

Key routes:

| Route | Method | Purpose |
|---|---|---|
| `/api/v1/forecast` | POST | Run a demand forecast for a given meal window |
| `/api/v1/waste` | GET/POST | Read or record waste observations |
| `/api/v1/qa` | POST | Submit a free-text question; returns Granite answer |
| `/api/v1/recommendations` | GET | List pending AI recommendations |
| `/api/v1/recommendations/{id}/approve` | POST | Human approves a recommendation |
| `/api/v1/recommendations/{id}/reject` | POST | Human rejects a recommendation |
| `/api/v1/trends` | GET | Aggregated waste trend data for charts |

---

### 3. Data Layer

**Technology:** PostgreSQL  
**Development:** local PostgreSQL instance  
**Production path:** IBM Cloud Databases for PostgreSQL

Core tables:

| Table | Contents |
|---|---|
| `meals` | Meal schedule (date, type, menu items) |
| `headcount` | Confirmed or estimated diner counts per meal |
| `consumption` | Actual food consumed (kg per item) |
| `waste_records` | Recorded waste (kg, category, date, meal_id) |
| `recommendations` | AI-generated suggestions + approval status |
| `policy_documents` | Metadata for RAG source documents |

---

### 4. Forecasting Layer

**Technology:** IBM Granite TTM (Tiny Time Mixers) via the
**watsonx.ai Forecast API** (`POST /ml/v1/wx_data/time_series/forecast`)

Available models (zero-shot, no fine-tuning required):

| Model ID | Min data points per channel |
|---|---|
| `ibm/granite-ttm-512-96-r2` | 512 |
| `ibm/granite-ttm-1024-96-r2` | 1 024 |
| `ibm/granite-ttm-1536-96-r2` | 1 536 |

The forecasting service:
1. Queries the data layer for historical consumption time series.
2. Calls the Granite TTM model through the watsonx.ai Forecast API.
3. Returns a 96-point forecast (configurable horizon).
4. Stores the result and computes the **predicted surplus** as
   `forecast − confirmed_headcount × portion_weight`.

Forecast results drive the Dashboard's demand display and feed into the
recommendation generator.

---

### 5. RAG Layer

**Technology:** LangChain, Chroma (dev) / Elasticsearch (prod),
Granite embedding model (`granite-embedding-278m-multilingual`)
via the **watsonx.ai Embeddings API**

Pipeline:

```
Ingestion (offline):
  PDF/Markdown policy docs
       │
       ▼
  Text extraction → chunking (512 tokens, 64 overlap)
       │
       ▼
  Granite embedding (watsonx.ai /ml/v1/text/embeddings)
       │
       ▼
  Upsert into Chroma / Elasticsearch vector index

Retrieval (online, per Q&A request):
  User question
       │
       ▼
  Embed question → vector search (top-k = 4 chunks)
       │
       ▼
  Rerank with watsonx.ai Rerank API (optional, improves precision)
       │
       ▼
  Return context chunks → AI layer
```

Source documents stored in `rag/documents/`:
- Food safety guidelines (FSSAI / local equivalent)
- Institutional catering policy
- Allergen handling procedures
- Surplus redistribution SOPs

---

### 6. AI Layer (Granite + RAG answer generation)

**Technology:** IBM Granite 3.3 8b Instruct  
**API:** watsonx.ai Chat API (`POST /ml/v1/text/chat`)

The AI layer receives:
- The user's question
- Retrieved RAG context chunks (from the RAG layer)
- Structured kitchen data (current forecast, recorded waste)

It produces:
- A grounded natural-language answer
- Optionally, a structured `recommendation` object that is written
  to the `recommendations` table with status `pending`.

The system prompt instructs the model to:
- Ground every answer in the provided context.
- Cite the policy document chunk when answering safety questions.
- Never make food-safety decisions autonomously — always surface
  them as pending recommendations for human approval.

---

## Information flow

### Demand forecast flow

```
Admin triggers forecast
       │
Frontend POST /api/v1/forecast
       │
Backend pulls historical consumption from PostgreSQL
       │
ForecastingService calls watsonx.ai Forecast API (Granite TTM)
       │
Forecast stored; surplus computed
       │
Response returned to frontend → Dashboard updated
```

### Q&A flow

```
Admin types question
       │
Frontend POST /api/v1/qa
       │
Backend embeds question via watsonx.ai Embeddings API
       │
RAGService queries vector store → top-k chunks retrieved
       │
AIService assembles prompt: system + context + question + kitchen data
       │
AIService calls watsonx.ai Chat API (Granite 3.3 8b Instruct)
       │
If answer contains a recommendation → write to recommendations table
       │
Response (answer + sources) returned to frontend
       │
If recommendation created → appears in Approval Queue
       │
Admin approves / rejects → status updated in DB
```

---

## Human oversight points

Every AI output that could affect food preparation quantities, storage,
or redistribution is written as a `pending` recommendation.  
No system action is taken automatically. The kitchen administrator is
the final decision-maker.

| Trigger | Oversight mechanism |
|---|---|
| Granite recommends reducing tomorrow's preparation | Approval Queue — admin clicks Approve |
| Forecast predicts significant surplus | Dashboard alert — admin decides on redistribution |
| Q&A answer suggests a safety-critical action | Answer flagged; recommendation surfaced for sign-off |

---

## Security notes

- watsonx.ai API key stored in environment variable; never in source code.
- All API routes protected by JWT issued at login.
- Role-based access: `admin` (full), `viewer` (read-only dashboard).
- Approval queue write-access restricted to `admin` role.
