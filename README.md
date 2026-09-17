# FoodWise AI

A small FastAPI + React (Vite) project for food forecasting and recommendations.

## Quick start (local)

1. Start backend (Python):

```powershell
# from project root
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

2. Start frontend (Node.js):

- Recommended: install Node.js (LTS) from https://nodejs.org and use system `npm`.
- Portable alternative: this repo may contain a `node-v*` folder. You can run npm via `./node-vXX/bin/npm` on Unix or `..\\node-vXX\\npm.cmd` on Windows.

```powershell
cd frontend
npm install
npm run dev
```

Open the frontend at http://localhost:5173 and the backend docs at http://localhost:8000/docs.

## Deployment

- Frontend: Deploy the `frontend` folder to Vercel or Netlify. Build command: `npm run build`, output directory: `dist`.
- Backend: Deploy the `backend` folder to Render, Railway, or any container platform. Start command example:

```
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Set environment variables (API keys, DB URLs) in the hosting provider — do not commit `.env` to git.

## Notes

- Do NOT commit the portable Node folder (`node-v*`) or `node_modules/`. They are in `.gitignore`.
- If you want, I can create the GitHub repo and push these changes for you, or provide the exact `git` commands to run locally.# FoodWise AI

> AI-powered food waste prediction and decision-support system for
> college hostels, cafeterias, restaurants, and institutional kitchens.

## What it does

| Capability | How |
|---|---|
| Demand forecasting | IBM Granite TTM time-series models via watsonx.ai Forecast API |
| Surplus estimation | Forecast minus confirmed headcount |
| Q&A / recommendations | IBM Granite chat models via watsonx.ai Chat API |
| Policy-grounded answers | RAG over food-safety / institutional-policy documents |
| Dashboard | React single-page application |
| Oversight | All AI recommendations require human approval before action |

## Repository layout

```
foodwise-ai/
├── frontend/          # React dashboard (kitchen admins)
│   ├── public/
│   └── src/
│       ├── components/   # Reusable UI widgets
│       ├── pages/        # Dashboard, Forecast, Q&A, Settings
│       ├── hooks/        # Data-fetching hooks
│       └── services/     # HTTP client wrappers
│
├── backend/           # Python FastAPI application server
│   ├── api/
│   │   ├── routes/       # /forecast, /qa, /waste, /recommendations
│   │   └── middleware/   # Auth, logging, CORS
│   ├── services/
│   │   ├── forecasting/  # Granite TTM wrapper
│   │   ├── ai/           # Granite chat / generation wrapper
│   │   ├── rag/          # Retrieval and context assembly
│   │   └── data/         # DB access layer (repository pattern)
│   ├── models/           # Pydantic request / response schemas
│   └── config/           # Settings, environment variables
│
├── data/
│   ├── historical/       # CSV / JSON exports for local dev & testing
│   └── seeds/            # Seed scripts for the relational database
│
├── rag/
│   ├── documents/        # Source PDFs / Markdown policy docs
│   ├── ingestion/        # Chunking + embedding pipeline scripts
│   └── vector_store/     # Local Chroma DB for development
│
├── agent/             # Bob agent configuration & prompt templates
│
├── scripts/           # One-off utilities (db-migrate, ingest-docs, …)
│
└── docs/              # Architecture diagrams, ADRs, runbooks
```

## Architecture overview

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full
layer-by-layer breakdown and data-flow description.

## Minimum Viable Product

See [`docs/MVP.md`](docs/MVP.md).

## Technology stack

| Layer | Technology | IBM service |
|---|---|---|
| Frontend | React + Vite + TailwindCSS | — |
| Backend API | Python 3.11, FastAPI | — |
| Database | PostgreSQL (local / IBM Cloud Databases for PostgreSQL) | IBM Cloud Databases for PostgreSQL |
| Time-series forecasting | Granite TTM (`ibm/granite-ttm-512-96-r2`) | watsonx.ai Forecast API |
| Generative AI / Q&A | Granite 3.3 8b Instruct | watsonx.ai Chat API |
| Embeddings | `granite-embedding-278m-multilingual` | watsonx.ai Embeddings API |
| Vector store (dev) | Chroma (local) | — |
| Vector store (prod) | Elasticsearch / watsonx Discovery | IBM Cloud Databases for Elasticsearch |
| RAG orchestration | LangChain | — |
| Human oversight | Approval queue in the dashboard | — |

## Environment variables

Copy `.env.example` to `.env` and fill in the values.

```
WATSONX_API_KEY=
WATSONX_PROJECT_ID=
WATSONX_URL=https://us-south.ml.cloud.ibm.com
DATABASE_URL=postgresql://user:pass@localhost:5432/foodwise
```
