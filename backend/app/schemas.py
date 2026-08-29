from typing import Optional
from pydantic import BaseModel, Field


class BinCreate(BaseModel):
    code: str
    ward: str
    latitude: float
    longitude: float
    fill_level: float = Field(ge=0, le=100)
    capacity_kg: float = Field(gt=0)


class BinOut(BinCreate):
    id: int

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

    class Config:
        from_attributes = True
