"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config.settings import get_settings
from backend.models.database import create_tables
from backend.api.routes import forecast, qa, waste, recommendations, meals

STATIC_DIR = Path(__file__).parent / "static"

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    _seed_demo_data()
    yield


app = FastAPI(
    title="FoodWise AI",
    description="AI-powered food waste prediction and decision-support for institutional kitchens.",
    version="0.1.0",
    lifespan=lifespan,
)

# Compression — shrinks JSON responses (charts, waste lists) by ~70 %
app.add_middleware(GZipMiddleware, minimum_size=500)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _seed_demo_data():
    """Insert a week of demo data if the DB is empty."""
    from backend.models.database import SessionLocal
    from backend.services.data import repository
    import math, random

    db = SessionLocal()
    try:
        if repository.list_meals(db, limit=1):
            return  # already seeded

        meal_types = ["breakfast", "lunch", "dinner"]
        items = {
            "breakfast": [("idli", 0.18), ("sambar", 0.09)],
            "lunch":     [("rice", 0.22), ("dal", 0.11), ("vegetable_curry", 0.09)],
            "dinner":    [("chapati", 0.15), ("paneer_curry", 0.10)],
        }
        from datetime import date, timedelta
        today = date.today()

        for day_offset in range(30, 0, -1):
            d = (today - timedelta(days=day_offset)).isoformat()
            hc = int(180 + 40 * math.sin(day_offset * 0.3) + random.randint(-10, 10))

            for mt in meal_types:
                meal = repository.create_meal(
                    db, meal_date=d, meal_type=mt,
                    confirmed=hc, estimated=hc,
                )
                for item, kg_per_head in items[mt]:
                    qty = round(hc * kg_per_head * (1 + random.uniform(-0.05, 0.12)), 2)
                    repository.add_consumption(db, meal.id, item, qty)
                    waste_kg = round(qty * random.uniform(0.03, 0.12), 2)
                    repository.add_waste(db, meal.id, item, waste_kg, "plate_waste")

    finally:
        db.close()


# Routes
app.include_router(forecast.router, prefix="/api/v1")
app.include_router(qa.router, prefix="/api/v1")
app.include_router(waste.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(meals.router, prefix="/api/v1")

# Serve static files and the React-less frontend
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/health")
def health():
    return {"status": "ok", "ai_mode": settings.ai_mode}


@app.get("/", include_in_schema=False)
def serve_ui():
    return FileResponse(STATIC_DIR / "index.html")
