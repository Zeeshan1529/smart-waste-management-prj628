from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import CollectionTask, WasteBin, WasteReport
from .schemas import (
    BinCreate,
    BinFillUpdate,
    BinOut,
    CollectionTaskCreate,
    CollectionTaskOut,
    ReportStatusUpdate,
    TaskStatusUpdate,
    WasteReportCreate,
    WasteReportOut,
)
from .services import collection_priority, priority_score


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PRJ_628 Smart Waste Management API",
    version="0.2.0",
    description=(
        "Core backend for predictive and circular waste management."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "project": "PRJ_628",
        "version": "0.2.0",
    }


# -------------------------------------------------------------------
# SMART BIN MONITORING
# -------------------------------------------------------------------

@app.get("/api/bins", response_model=list[BinOut])
def list_bins(db: Session = Depends(get_db)):
    return (
        db.query(WasteBin)
        .order_by(WasteBin.fill_level.desc())
        .all()
    )


@app.post("/api/bins", response_model=BinOut)
def create_bin(
    payload: BinCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(WasteBin)
        .filter(WasteBin.code == payload.code)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Bin code already exists",
        )

    row = WasteBin(
        **payload.model_dump(),
        updated_at=datetime.utcnow(),
    )

    db.add(row)
    db.commit()
    db.refresh(row)

    return row


@app.patch("/api/bins/{bin_id}/fill", response_model=BinOut)
def update_bin_fill(
    bin_id: int,
    payload: BinFillUpdate,
    db: Session = Depends(get_db),
):
    row = db.get(WasteBin, bin_id)

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Bin not found",
        )

    row.fill_level = payload.fill_level
    row.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(row)

    return row


@app.get("/api/bins/priorities")
def bin_priorities(db: Session = Depends(get_db)):
    bins = (
        db.query(WasteBin)
        .order_by(WasteBin.fill_level.desc())
        .all()
    )

    results = []

    for row in bins:
        age_hours = max(
            (datetime.utcnow() - row.updated_at)
            .total_seconds() / 3600.0,
            0,
        )

        score = priority_score(
            row.fill_level,
            age_hours,
        )

        results.append(
            {
                "bin_id": row.id,
                "code": row.code,
                "ward": row.ward,
                "fill_level": row.fill_level,
                "priority_score": score,
                "priority": collection_priority(
                    row.fill_level,
                    age_hours,
                ),
                "age_hours": round(age_hours, 2),
            }
        )

    return results


@app.get("/api/bins/{bin_id}/priority")
def bin_priority(
    bin_id: int,
    db: Session = Depends(get_db),
):
    row = db.get(WasteBin, bin_id)

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Bin not found",
        )

    age_hours = max(
        (datetime.utcnow() - row.updated_at)
        .total_seconds() / 3600.0,
        0,
    )

    return {
        "bin_id": row.id,
        "code": row.code,
        "ward": row.ward,
        "priority_score": priority_score(
            row.fill_level,
            age_hours,
        ),
        "priority": collection_priority(
            row.fill_level,
            age_hours,
        ),
        "fill_level": row.fill_level,
        "age_hours": round(age_hours, 2),
    }


# -------------------------------------------------------------------
# WASTE REPORTS
# -------------------------------------------------------------------

@app.get("/api/reports", response_model=list[WasteReportOut])
def list_reports(db: Session = Depends(get_db)):
    return (
        db.query(WasteReport)
        .order_by(WasteReport.id.desc())
        .all()
    )


@app.post("/api/reports", response_model=WasteReportOut)
def create_report(
    payload: WasteReportCreate,
    db: Session = Depends(get_db),
):
    row = WasteReport(**payload.model_dump())

    db.add(row)
    db.commit()
    db.refresh(row)

    return row


@app.patch("/api/reports/{report_id}/status", response_model=WasteReportOut)
def update_report_status(
    report_id: int,
    payload: ReportStatusUpdate,
    db: Session = Depends(get_db),
):
    row = db.get(WasteReport, report_id)

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Waste report not found",
        )

    row.status = payload.status

    db.commit()
    db.refresh(row)

    return row


# -------------------------------------------------------------------
# COLLECTION TASKS
# -------------------------------------------------------------------

@app.get(
    "/api/collection-tasks",
    response_model=list[CollectionTaskOut],
)
def list_collection_tasks(db: Session = Depends(get_db)):
    return (
        db.query(CollectionTask)
        .order_by(CollectionTask.id.desc())
        .all()
    )


@app.post(
    "/api/collection-tasks",
    response_model=CollectionTaskOut,
)
def create_collection_task(
    payload: CollectionTaskCreate,
    db: Session = Depends(get_db),
):
    bin_row = db.get(WasteBin, payload.bin_id)

    if not bin_row:
        raise HTTPException(
            status_code=404,
            detail="Bin not found",
        )

    report_row = None

    if payload.report_id is not None:
        report_row = db.get(
            WasteReport,
            payload.report_id,
        )

        if not report_row:
            raise HTTPException(
                status_code=404,
                detail="Waste report not found",
            )

    age_hours = max(
        (datetime.utcnow() - bin_row.updated_at)
        .total_seconds() / 3600.0,
        0,
    )

    task = CollectionTask(
        bin_id=payload.bin_id,
        report_id=payload.report_id,
        assigned_to=payload.assigned_to or "",
        notes=payload.notes or "",
        scheduled_at=payload.scheduled_at,
        priority=collection_priority(
            bin_row.fill_level,
            age_hours,
        ),
        status="PLANNED",
    )

    db.add(task)

    if report_row and report_row.status in {
        "OPEN",
        "IN_REVIEW",
    }:
        report_row.status = "ASSIGNED"

    db.commit()
    db.refresh(task)

    return task


@app.patch(
    "/api/collection-tasks/{task_id}/status",
    response_model=CollectionTaskOut,
)
def update_collection_task_status(
    task_id: int,
    payload: TaskStatusUpdate,
    db: Session = Depends(get_db),
):
    task = db.get(CollectionTask, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Collection task not found",
        )

    task.status = payload.status

    if payload.status == "COMPLETED":
        task.completed_at = datetime.utcnow()

        # Simulated collection event:
        # once collected, the bin is emptied and the sensor timestamp refreshes.
        bin_row = db.get(WasteBin, task.bin_id)

        if bin_row:
            bin_row.fill_level = 0.0
            bin_row.updated_at = datetime.utcnow()

        if task.report_id is not None:
            report_row = db.get(
                WasteReport,
                task.report_id,
            )

            if report_row:
                report_row.status = "RESOLVED"

    elif payload.status != "COMPLETED":
        task.completed_at = None

    db.commit()
    db.refresh(task)

    return task


# -------------------------------------------------------------------
# ANALYTICS
# -------------------------------------------------------------------

@app.get("/api/analytics/overview")
def analytics_overview(db: Session = Depends(get_db)):
    bins = db.query(WasteBin).all()

    total_bins = len(bins)

    average_fill_level = (
        round(
            sum(float(row.fill_level or 0) for row in bins)
            / total_bins,
            1,
        )
        if total_bins
        else 0.0
    )

    estimated_waste_kg = round(
        sum(
            (float(row.fill_level or 0) / 100.0)
            * float(row.capacity_kg or 0)
            for row in bins
        ),
        2,
    )

    critical_bins = 0
    high_priority_bins = 0

    for row in bins:
        age_hours = max(
            (datetime.utcnow() - row.updated_at)
            .total_seconds() / 3600.0,
            0,
        )

        priority = collection_priority(
            row.fill_level,
            age_hours,
        )

        if priority == "CRITICAL":
            critical_bins += 1
        elif priority == "HIGH":
            high_priority_bins += 1

    open_reports = (
        db.query(func.count(WasteReport.id))
        .filter(WasteReport.status == "OPEN")
        .scalar()
    )

    in_review_reports = (
        db.query(func.count(WasteReport.id))
        .filter(WasteReport.status == "IN_REVIEW")
        .scalar()
    )

    planned_tasks = (
        db.query(func.count(CollectionTask.id))
        .filter(CollectionTask.status == "PLANNED")
        .scalar()
    )

    in_progress_tasks = (
        db.query(func.count(CollectionTask.id))
        .filter(CollectionTask.status == "IN_PROGRESS")
        .scalar()
    )

    completed_tasks = (
        db.query(func.count(CollectionTask.id))
        .filter(CollectionTask.status == "COMPLETED")
        .scalar()
    )

    return {
        "total_bins": total_bins,
        "critical_bins": critical_bins,
        "high_priority_bins": high_priority_bins,
        "average_fill_level": average_fill_level,
        "estimated_waste_kg": estimated_waste_kg,
        "open_reports": int(open_reports or 0),
        "in_review_reports": int(in_review_reports or 0),
        "planned_tasks": int(planned_tasks or 0),
        "in_progress_tasks": int(in_progress_tasks or 0),
        "completed_tasks": int(completed_tasks or 0),
    }
