from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

from .db import Base


class WasteBin(Base):
    __tablename__ = "waste_bins"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    ward = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    fill_level = Column(Float, default=0.0)
    capacity_kg = Column(Float, default=100.0)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class WasteReport(Base):
    __tablename__ = "waste_reports"

    id = Column(Integer, primary_key=True)
    location = Column(String(255), nullable=False)
    ward = Column(String(100), nullable=False)
    waste_type = Column(String(80), nullable=False)
    description = Column(Text, default="")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String(30), default="OPEN")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class CollectionTask(Base):
    __tablename__ = "collection_tasks"

    id = Column(Integer, primary_key=True)

    bin_id = Column(
        Integer,
        ForeignKey("waste_bins.id"),
        nullable=False,
    )

    report_id = Column(
        Integer,
        ForeignKey("waste_reports.id"),
        nullable=True,
    )

    priority = Column(String(20), default="MEDIUM", nullable=False)
    status = Column(String(30), default="PLANNED", nullable=False)

    assigned_to = Column(String(100), default="")
    notes = Column(Text, default="")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    scheduled_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
