"""SQLAlchemy models + database engine setup (SQLite for local dev)."""
from datetime import datetime

from sqlalchemy import (
    create_engine, Column, Index, Integer, String, Float,
    DateTime, Text, ForeignKey,
)
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

from backend.config.settings import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class Meal(Base):
    __tablename__ = "meals"
    id = Column(Integer, primary_key=True, index=True)
    meal_date = Column(String(10), nullable=False, index=True)   # YYYY-MM-DD
    meal_type = Column(String(20), nullable=False, index=True)   # breakfast/lunch/dinner/snack
    menu_items = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (Index("ix_meals_date_type", "meal_date", "meal_type"),)

    headcounts = relationship("Headcount", back_populates="meal", cascade="all, delete")
    consumptions = relationship("Consumption", back_populates="meal", cascade="all, delete")
    waste_records = relationship("WasteRecord", back_populates="meal", cascade="all, delete")
    recommendations = relationship("Recommendation", back_populates="meal")


class Headcount(Base):
    __tablename__ = "headcount"
    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id"), nullable=False)
    confirmed = Column(Integer, default=0)
    estimated = Column(Integer, default=0)
    source = Column(String(30), default="manual")
    created_at = Column(DateTime, default=datetime.utcnow)
    meal = relationship("Meal", back_populates="headcounts")


class Consumption(Base):
    __tablename__ = "consumption"
    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id"), nullable=False, index=True)
    item_name = Column(String(120), nullable=False)
    quantity_kg = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    meal = relationship("Meal", back_populates="consumptions")


class WasteRecord(Base):
    __tablename__ = "waste_records"
    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id"), nullable=False, index=True)
    item_name = Column(String(120), nullable=False)
    waste_kg = Column(Float, nullable=False)
    waste_category = Column(String(30), default="plate_waste")
    notes = Column(Text, default="")
    recorded_at = Column(DateTime, default=datetime.utcnow)
    meal = relationship("Meal", back_populates="waste_records")


class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id"), nullable=True)
    source = Column(String(20), default="ai")
    recommendation = Column(Text, nullable=False)
    rationale = Column(Text, default="")
    status = Column(String(20), default="pending", index=True)  # pending/approved/rejected
    reviewed_by = Column(String(120), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    meal = relationship("Meal", back_populates="recommendations")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
