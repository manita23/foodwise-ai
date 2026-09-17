-- FoodWise AI — core PostgreSQL schema
-- Run with: psql $DATABASE_URL -f schema.sql

-- ── Meal schedule ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS meals (
    id          SERIAL PRIMARY KEY,
    meal_date   DATE        NOT NULL,
    meal_type   VARCHAR(20) NOT NULL CHECK (meal_type IN ('breakfast','lunch','dinner','snack')),
    menu_items  TEXT[],
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- ── Headcount ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS headcount (
    id          SERIAL PRIMARY KEY,
    meal_id     INT         NOT NULL REFERENCES meals(id) ON DELETE CASCADE,
    confirmed   INT         NOT NULL DEFAULT 0,
    estimated   INT         NOT NULL DEFAULT 0,
    source      VARCHAR(30) DEFAULT 'manual', -- 'manual' | 'system' | 'import'
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- ── Consumption records ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS consumption (
    id              SERIAL PRIMARY KEY,
    meal_id         INT            NOT NULL REFERENCES meals(id) ON DELETE CASCADE,
    item_name       VARCHAR(120)   NOT NULL,
    quantity_kg     NUMERIC(8, 3)  NOT NULL,
    recorded_at     TIMESTAMPTZ    DEFAULT now()
);

-- ── Waste records ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS waste_records (
    id              SERIAL PRIMARY KEY,
    meal_id         INT            NOT NULL REFERENCES meals(id) ON DELETE CASCADE,
    item_name       VARCHAR(120)   NOT NULL,
    waste_kg        NUMERIC(8, 3)  NOT NULL,
    waste_category  VARCHAR(30)    DEFAULT 'plate_waste',
    -- 'plate_waste' | 'preparation_waste' | 'storage_loss' | 'spoilage'
    notes           TEXT,
    recorded_at     TIMESTAMPTZ    DEFAULT now()
);

-- ── AI recommendations ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS recommendations (
    id              SERIAL PRIMARY KEY,
    meal_id         INT            REFERENCES meals(id),
    source          VARCHAR(20)    DEFAULT 'ai', -- 'ai' | 'system'
    recommendation  TEXT           NOT NULL,
    rationale       TEXT,
    status          VARCHAR(20)    DEFAULT 'pending'
                                   CHECK (status IN ('pending','approved','rejected')),
    reviewed_by     VARCHAR(120),  -- username of approving admin
    reviewed_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ    DEFAULT now()
);

-- ── RAG document metadata ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS policy_documents (
    id              SERIAL PRIMARY KEY,
    filename        VARCHAR(255)   NOT NULL UNIQUE,
    display_name    VARCHAR(255)   NOT NULL,
    doc_type        VARCHAR(60),   -- 'food_safety' | 'catering_policy' | 'sop' | 'guideline'
    ingested_at     TIMESTAMPTZ,
    chunk_count     INT            DEFAULT 0
);

-- ── Indexes ───────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_consumption_meal      ON consumption(meal_id);
CREATE INDEX IF NOT EXISTS idx_waste_meal            ON waste_records(meal_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_status ON recommendations(status);
CREATE INDEX IF NOT EXISTS idx_meals_date            ON meals(meal_date);
