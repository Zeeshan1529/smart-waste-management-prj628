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
    status: Literal["PLANNED", "IN_PROGRESS", "COMPLETED", "CANCELLED"]
