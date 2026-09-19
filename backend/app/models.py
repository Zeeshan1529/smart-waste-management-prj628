from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

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


class Recycler(Base):
    __tablename__ = "recyclers"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True, nullable=False)
    material_types = Column(String(255), nullable=False)
    ward = Column(String(100), default="")
    city = Column(String(100), default="Bengaluru")
    contact_email = Column(String(150), default="")
    status = Column(String(30), default="ACTIVE", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MaterialListing(Base):
    __tablename__ = "material_listings"

    id = Column(Integer, primary_key=True)

    source_report_id = Column(
        Integer,
        ForeignKey("waste_reports.id"),
        nullable=True,
    )

    recycler_id = Column(
        Integer,
        ForeignKey("recyclers.id"),
        nullable=True,
    )

    material_type = Column(String(80), nullable=False)
    recovery_stream = Column(String(40), nullable=False)

    quantity_kg = Column(Float, nullable=False)
    classification_confidence = Column(Float, nullable=True)

    source_location = Column(String(255), nullable=False)

    status = Column(
        String(30),
        default="AVAILABLE",
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


class MarketplaceTransaction(Base):
    __tablename__ = "marketplace_transactions"

    id = Column(Integer, primary_key=True)

    listing_id = Column(
        Integer,
        ForeignKey("material_listings.id"),
        nullable=False,
    )

    recycler_id = Column(
        Integer,
        ForeignKey("recyclers.id"),
        nullable=False,
    )

    quantity_kg = Column(Float, nullable=False)

    status = Column(
        String(30),
        default="INITIATED",
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    completed_at = Column(
        DateTime,
        nullable=True,
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(
        String(80),
        unique=True,
        nullable=False,
    )

    email = Column(
        String(150),
        unique=True,
        nullable=False,
    )

    hashed_password = Column(
        String(255),
        nullable=False,
    )

    role = Column(
        String(30),
        nullable=False,
        default="CITIZEN",
    )

    is_active = Column(
        Integer,
        default=1,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    action = Column(
        String(100),
        nullable=False,
    )

    resource = Column(
        String(100),
        nullable=False,
    )

    detail = Column(
        Text,
        default="",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
