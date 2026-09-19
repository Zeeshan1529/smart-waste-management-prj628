from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class BinCreate(BaseModel):
    code: str
    ward: str
    latitude: float
    longitude: float
    fill_level: float = Field(default=0.0, ge=0, le=100)
    capacity_kg: float = Field(default=100.0, gt=0)


class BinFillUpdate(BaseModel):
    fill_level: float = Field(ge=0, le=100)


class BinOut(BinCreate):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True


class WasteReportCreate(BaseModel):
    location: str
    ward: str
    waste_type: str
    description: Optional[str] = ""
    latitude: float
    longitude: float


class WasteReportOut(WasteReportCreate):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReportStatusUpdate(BaseModel):
    status: Literal["OPEN", "IN_REVIEW", "ASSIGNED", "RESOLVED"]


class CollectionTaskCreate(BaseModel):
    bin_id: int
    report_id: Optional[int] = None
    assigned_to: Optional[str] = ""
    notes: Optional[str] = ""
    scheduled_at: Optional[datetime] = None


class CollectionTaskOut(CollectionTaskCreate):
    id: int
    priority: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskStatusUpdate(BaseModel):
    status: Literal[
        "PLANNED",
        "IN_PROGRESS",
        "COMPLETED",
        "CANCELLED",
    ]


class MLPredictionRequest(BaseModel):
    ward: str
    day_of_week: int = Field(ge=0, le=6)
    month: int = Field(ge=1, le=12)
    fill_level: float = Field(ge=0, le=100)
    capacity_kg: float = Field(gt=0)
    previous_day_kg: float = Field(ge=0)
    avg_3_day_kg: float = Field(ge=0)
    avg_7_day_kg: float = Field(ge=0)


class MLPredictionResponse(BaseModel):
    predicted_waste_kg: float
    model: str


class RecyclerCreate(BaseModel):
    name: str
    material_types: str
    ward: str = ""
    city: str = "Bengaluru"
    contact_email: str = ""


class RecyclerOut(RecyclerCreate):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class MaterialListingCreate(BaseModel):
    source_report_id: Optional[int] = None
    material_type: str
    recovery_stream: Literal[
        "RECYCLABLE",
        "RESIDUAL_WASTE",
    ]
    quantity_kg: float = Field(gt=0)
    classification_confidence: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
    )
    source_location: str


class MaterialListingOut(MaterialListingCreate):
    id: int
    recycler_id: Optional[int] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class MaterialListingStatusUpdate(BaseModel):
    status: Literal[
        "AVAILABLE",
        "MATCHED",
        "RECOVERED",
        "CANCELLED",
    ]


class MarketplaceTransactionCreate(BaseModel):
    listing_id: int
    recycler_id: int
    quantity_kg: float = Field(gt=0)


class MarketplaceTransactionOut(MarketplaceTransactionCreate):
    id: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MarketplaceTransactionStatusUpdate(BaseModel):
    status: Literal[
        "INITIATED",
        "IN_TRANSIT",
        "COMPLETED",
        "CANCELLED",
    ]
