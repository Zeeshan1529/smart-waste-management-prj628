from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import WasteBin, WasteReport
from .schemas import BinCreate, BinOut, WasteReportCreate, WasteReportOut
from .services import collection_priority

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PRJ_628 Smart Waste Management API",
    version="0.1.0",
    description="Prototype backend for predictive circular waste management."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "project": "PRJ_628"}


@app.get("/api/bins", response_model=list[BinOut])
def list_bins(db: Session = Depends(get_db)):
    return db.query(WasteBin).order_by(WasteBin.fill_level.desc()).all()


@app.post("/api/bins", response_model=BinOut)
def create_bin(payload: BinCreate, db: Session = Depends(get_db)):
    if db.query(WasteBin).filter(WasteBin.code == payload.code).first():
        raise HTTPException(status_code=409, detail="Bin code already exists")
    row = WasteBin(**payload.model_dump(), updated_at=datetime.utcnow())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get("/api/bins/{bin_id}/priority")
def bin_priority(bin_id: int, db: Session = Depends(get_db)):
    row = db.get(WasteBin, bin_id)
    if not row:
        raise HTTPException(status_code=404, detail="Bin not found")
    age_hours = max((datetime.utcnow() - row.updated_at).total_seconds() / 3600.0, 0)
    return {
        "bin_id": row.id,
        "code": row.code,
        "priority": collection_priority(row.fill_level, age_hours),
        "fill_level": row.fill_level,
        "age_hours": round(age_hours, 2),
    }


@app.get("/api/reports", response_model=list[WasteReportOut])
def list_reports(db: Session = Depends(get_db)):
    return db.query(WasteReport).order_by(WasteReport.id.desc()).all()


@app.post("/api/reports", response_model=WasteReportOut)
def create_report(payload: WasteReportCreate, db: Session = Depends(get_db)):
    row = WasteReport(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
