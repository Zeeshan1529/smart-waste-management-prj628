from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import AuditLog, CollectionTask, WasteBin, WasteReport
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
from .security import require_roles
from .audit import write_audit


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
    current_user=Depends(require_roles("OPERATOR", "ADMIN")),
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
    db.flush()

    write_audit(
        db,
        current_user,
        "CREATE",
        "waste_bins",
        f"Created bin {row.code}",
    )

    db.commit()
    db.refresh(row)

    return row


@app.patch("/api/bins/{bin_id}/fill", response_model=BinOut)
def update_bin_fill(
    bin_id: int,
    payload: BinFillUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("OPERATOR", "ADMIN")),
):
    row = db.get(WasteBin, bin_id)

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Bin not found",
        )

    row.fill_level = payload.fill_level
    row.updated_at = datetime.utcnow()

    write_audit(
        db,
        current_user,
        "UPDATE_FILL",
        "waste_bins",
        f"Updated {row.code} fill to {row.fill_level}%",
    )

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
    current_user=Depends(require_roles("CITIZEN", "ADMIN")),
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
    current_user=Depends(require_roles("OPERATOR", "ADMIN")),
):
    row = db.get(WasteReport, report_id)

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Waste report not found",
        )

    row.status = payload.status

    write_audit(
        db,
        current_user,
        "UPDATE_STATUS",
        "waste_reports",
        f"Report {row.id} status changed to {row.status}",
    )

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
    current_user=Depends(require_roles("OPERATOR", "ADMIN")),
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
    db.flush()

    write_audit(
        db,
        current_user,
        "CREATE",
        "collection_tasks",
        f"Created collection task {task.id}",
    )

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
    current_user=Depends(require_roles("OPERATOR", "ADMIN")),
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

    write_audit(
        db,
        current_user,
        "UPDATE_STATUS",
        "collection_tasks",
        f"Task {task.id} status changed to {task.status}",
    )

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


from .ml_service import predict_waste_generation
from .schemas import (
    MLPredictionRequest,
    MLPredictionResponse,
)


@app.post(
    "/api/ml/predict",
    response_model=MLPredictionResponse,
)
def predict_waste(
    payload: MLPredictionRequest,
):
    try:
        prediction = predict_waste_generation(
            ward=payload.ward,
            day_of_week=payload.day_of_week,
            month=payload.month,
            fill_level=payload.fill_level,
            capacity_kg=payload.capacity_kg,
            previous_day_kg=payload.previous_day_kg,
            avg_3_day_kg=payload.avg_3_day_kg,
            avg_7_day_kg=payload.avg_7_day_kg,
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )

    return {
        "predicted_waste_kg": prediction,
        "model": "RandomForestRegressor",
    }


from fastapi import File, UploadFile
from .image_classifier import classify_image


@app.post("/api/ml/classify-image")
async def classify_waste_image(
    file: UploadFile = File(...),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Please upload an image file.",
        )

    try:
        contents = await file.read()

        from io import BytesIO
        from PIL import Image

        image = Image.open(
            BytesIO(contents)
        )

        result = classify_image(image)

        return {
            "filename": file.filename,
            **result,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to classify image: {exc}",
        )


# -------------------------------------------------------------------
# CIRCULAR ECONOMY / RECYCLER MARKETPLACE
# -------------------------------------------------------------------

from .models import (
    MaterialListing,
    MarketplaceTransaction,
    Recycler,
)
from .schemas import (
    MaterialListingCreate,
    MaterialListingOut,
    MaterialListingStatusUpdate,
    MarketplaceTransactionCreate,
    MarketplaceTransactionOut,
    MarketplaceTransactionStatusUpdate,
    RecyclerCreate,
    RecyclerOut,
)


@app.get("/api/recyclers", response_model=list[RecyclerOut])
def list_recyclers(db: Session = Depends(get_db)):
    return (
        db.query(Recycler)
        .filter(Recycler.status == "ACTIVE")
        .order_by(Recycler.name.asc())
        .all()
    )


@app.post("/api/recyclers", response_model=RecyclerOut)
def create_recycler(
    payload: RecyclerCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN")),
):
    existing = (
        db.query(Recycler)
        .filter(Recycler.name == payload.name)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Recycler already exists",
        )

    recycler = Recycler(
        **payload.model_dump(),
        status="ACTIVE",
    )

    db.add(recycler)
    db.commit()
    db.refresh(recycler)

    return recycler


@app.get(
    "/api/material-listings",
    response_model=list[MaterialListingOut],
)
def list_material_listings(
    db: Session = Depends(get_db),
):
    return (
        db.query(MaterialListing)
        .order_by(MaterialListing.id.desc())
        .all()
    )


@app.post(
    "/api/material-listings",
    response_model=MaterialListingOut,
)
def create_material_listing(
    payload: MaterialListingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("RECYCLER", "ADMIN")),
):
    if payload.source_report_id is not None:
        report = db.get(
            WasteReport,
            payload.source_report_id,
        )

        if not report:
            raise HTTPException(
                status_code=404,
                detail="Source waste report not found",
            )

    if payload.recovery_stream == "RESIDUAL_WASTE":
        raise HTTPException(
            status_code=400,
            detail=(
                "Residual waste cannot be listed in the "
                "circular-economy marketplace."
            ),
        )

    listing = MaterialListing(
        **payload.model_dump(),
        status="AVAILABLE",
    )

    db.add(listing)
    db.commit()
    db.refresh(listing)

    return listing


@app.post(
    "/api/material-listings/{listing_id}/match",
    response_model=MaterialListingOut,
)
def match_material_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("RECYCLER", "ADMIN")),
):
    listing = db.get(
        MaterialListing,
        listing_id,
    )

    if not listing:
        raise HTTPException(
            status_code=404,
            detail="Material listing not found",
        )

    if listing.status not in {
        "AVAILABLE",
        "MATCHED",
    }:
        raise HTTPException(
            status_code=400,
            detail="Listing is not available for matching",
        )

    material = listing.material_type.strip().lower()

    recyclers = (
        db.query(Recycler)
        .filter(Recycler.status == "ACTIVE")
        .order_by(Recycler.id.asc())
        .all()
    )

    matched_recycler = None

    for recycler in recyclers:
        accepted_materials = {
            item.strip().lower()
            for item in recycler.material_types.split(",")
            if item.strip()
        }

        if material in accepted_materials:
            matched_recycler = recycler
            break

    if matched_recycler is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No active recycler currently accepts "
                f"{listing.material_type}"
            ),
        )

    listing.recycler_id = matched_recycler.id
    listing.status = "MATCHED"

    db.commit()
    db.refresh(listing)

    return listing


@app.patch(
    "/api/material-listings/{listing_id}/status",
    response_model=MaterialListingOut,
)
def update_material_listing_status(
    listing_id: int,
    payload: MaterialListingStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("RECYCLER", "ADMIN")),
):
    listing = db.get(
        MaterialListing,
        listing_id,
    )

    if not listing:
        raise HTTPException(
            status_code=404,
            detail="Material listing not found",
        )

    listing.status = payload.status

    db.commit()
    db.refresh(listing)

    return listing


@app.get(
    "/api/marketplace/transactions",
    response_model=list[MarketplaceTransactionOut],
)
def list_transactions(
    db: Session = Depends(get_db),
):
    return (
        db.query(MarketplaceTransaction)
        .order_by(
            MarketplaceTransaction.id.desc()
        )
        .all()
    )


@app.post(
    "/api/marketplace/transactions",
    response_model=MarketplaceTransactionOut,
)
def create_transaction(
    payload: MarketplaceTransactionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("RECYCLER", "ADMIN")),
):
    listing = db.get(
        MaterialListing,
        payload.listing_id,
    )

    if not listing:
        raise HTTPException(
            status_code=404,
            detail="Material listing not found",
        )

    recycler = db.get(
        Recycler,
        payload.recycler_id,
    )

    if not recycler or recycler.status != "ACTIVE":
        raise HTTPException(
            status_code=404,
            detail="Active recycler not found",
        )

    if listing.status not in {
        "AVAILABLE",
        "MATCHED",
    }:
        raise HTTPException(
            status_code=400,
            detail="Listing cannot be transacted",
        )

    if payload.quantity_kg > listing.quantity_kg:
        raise HTTPException(
            status_code=400,
            detail="Transaction quantity exceeds listing quantity",
        )

    accepted_materials = {
        item.strip().lower()
        for item in recycler.material_types.split(",")
        if item.strip()
    }

    if listing.material_type.strip().lower() not in accepted_materials:
        raise HTTPException(
            status_code=400,
            detail=(
                "Recycler does not accept this material type"
            ),
        )

    transaction = MarketplaceTransaction(
        listing_id=payload.listing_id,
        recycler_id=payload.recycler_id,
        quantity_kg=payload.quantity_kg,
        status="INITIATED",
    )

    listing.recycler_id = payload.recycler_id
    listing.status = "MATCHED"

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


@app.patch(
    "/api/marketplace/transactions/{transaction_id}/status",
    response_model=MarketplaceTransactionOut,
)
def update_transaction_status(
    transaction_id: int,
    payload: MarketplaceTransactionStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("RECYCLER", "ADMIN")),
):
    transaction = db.get(
        MarketplaceTransaction,
        transaction_id,
    )

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Marketplace transaction not found",
        )

    transaction.status = payload.status

    if payload.status == "COMPLETED":
        transaction.completed_at = datetime.utcnow()

        listing = db.get(
            MaterialListing,
            transaction.listing_id,
        )

        if listing:
            listing.status = "RECOVERED"

    elif payload.status != "COMPLETED":
        transaction.completed_at = None

    db.commit()
    db.refresh(transaction)

    return transaction


from .route_service import optimize_route
from .schemas import (
    RouteOptimizeRequest,
    RouteOptimizeResponse,
)


@app.post(
    "/api/routes/optimize",
    response_model=RouteOptimizeResponse,
)
def optimize_collection_route(
    payload: RouteOptimizeRequest,
    db: Session = Depends(get_db),
):
    bins = []

    if payload.bin_ids:
        for bin_id in payload.bin_ids:
            row = db.get(WasteBin, bin_id)

            if not row:
                raise HTTPException(
                    status_code=404,
                    detail=f"Bin {bin_id} not found",
                )

            bins.append(row)

    else:
        # When no bins are supplied explicitly,
        # automatically select bins needing attention.
        bins = (
            db.query(WasteBin)
            .filter(WasteBin.fill_level >= 70)
            .order_by(WasteBin.fill_level.desc())
            .all()
        )

    if not bins:
        return {
            "route": [],
            "total_distance_km": 0.0,
            "number_of_stops": 0,
        }

    for row in bins:
        age_hours = max(
            (
                datetime.utcnow()
                - row.updated_at
            ).total_seconds()
            / 3600.0,
            0,
        )

        row._route_priority = collection_priority(
            row.fill_level,
            age_hours,
        )

    return optimize_route(
        bins=bins,
        start_latitude=payload.start_latitude,
        start_longitude=payload.start_longitude,
    )


# -------------------------------------------------------------------
# AUTHENTICATION
# -------------------------------------------------------------------

from .auth_routes import router as auth_router

app.include_router(auth_router)
