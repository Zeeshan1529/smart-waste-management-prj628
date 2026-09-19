from datetime import datetime, timedelta

from app.db import Base, SessionLocal, engine
from app.models import (
    CollectionTask,
    MaterialListing,
    MarketplaceTransaction,
    Recycler,
    WasteBin,
    WasteReport,
)


Base.metadata.create_all(bind=engine)

db = SessionLocal()


# -------------------------------------------------------------------
# WASTE BINS
# -------------------------------------------------------------------

if db.query(WasteBin).count() == 0:
    bins = [
        WasteBin(
            code="BIN-101",
            ward="Ward 12",
            latitude=12.9718,
            longitude=77.5941,
            fill_level=88,
            capacity_kg=120,
        ),
        WasteBin(
            code="BIN-102",
            ward="Ward 12",
            latitude=12.9742,
            longitude=77.6000,
            fill_level=62,
            capacity_kg=100,
        ),
        WasteBin(
            code="BIN-205",
            ward="Ward 18",
            latitude=12.9352,
            longitude=77.6245,
            fill_level=94,
            capacity_kg=150,
        ),
        WasteBin(
            code="BIN-311",
            ward="Ward 27",
            latitude=12.9063,
            longitude=77.5857,
            fill_level=35,
            capacity_kg=100,
        ),
    ]

    db.add_all(bins)


# -------------------------------------------------------------------
# WASTE REPORTS
# -------------------------------------------------------------------

if db.query(WasteReport).count() == 0:
    db.add_all(
        [
            WasteReport(
                location="5th Main Road",
                ward="Ward 12",
                waste_type="Mixed",
                description="Overflowing roadside waste point",
                latitude=12.9720,
                longitude=77.5940,
                status="OPEN",
                created_at=(
                    datetime.utcnow()
                    - timedelta(hours=2)
                ),
            ),
            WasteReport(
                location="Market Road",
                ward="Ward 18",
                waste_type="Organic",
                description="Market waste after peak hours",
                latitude=12.9354,
                longitude=77.6242,
                status="IN_REVIEW",
                created_at=(
                    datetime.utcnow()
                    - timedelta(hours=6)
                ),
            ),
        ]
    )


db.commit()


# Refresh IDs.
bins = (
    db.query(WasteBin)
    .order_by(WasteBin.id.asc())
    .all()
)

reports = (
    db.query(WasteReport)
    .order_by(WasteReport.id.asc())
    .all()
)


# -------------------------------------------------------------------
# COLLECTION TASKS
# -------------------------------------------------------------------

if db.query(CollectionTask).count() == 0 and bins:
    tasks = [
        CollectionTask(
            bin_id=(
                bins[2].id
                if len(bins) >= 3
                else bins[0].id
            ),
            report_id=(
                reports[1].id
                if len(reports) >= 2
                else None
            ),
            priority="CRITICAL",
            status="PLANNED",
            assigned_to="Collection Team A",
            notes=(
                "High-fill bin requires "
                "priority collection."
            ),
            scheduled_at=(
                datetime.utcnow()
                + timedelta(hours=1)
            ),
        ),
        CollectionTask(
            bin_id=bins[0].id,
            report_id=(
                reports[0].id
                if reports
                else None
            ),
            priority="HIGH",
            status="PLANNED",
            assigned_to="Collection Team B",
            notes=(
                "Roadside overflow report "
                "linked to bin."
            ),
            scheduled_at=(
                datetime.utcnow()
                + timedelta(hours=2)
            ),
        ),
    ]

    db.add_all(tasks)


# -------------------------------------------------------------------
# RECYCLERS
# -------------------------------------------------------------------

if db.query(Recycler).count() == 0:
    db.add_all(
        [
            Recycler(
                name="GreenCycle Plastics",
                material_types="plastic",
                ward="Ward 12",
                city="Bengaluru",
                contact_email="plastic@example.org",
            ),
            Recycler(
                name="Bengaluru Glass Recovery",
                material_types="glass",
                ward="Ward 18",
                city="Bengaluru",
                contact_email="glass@example.org",
            ),
            Recycler(
                name="Metro Metal Recovery",
                material_types="metal",
                ward="Ward 27",
                city="Bengaluru",
                contact_email="metal@example.org",
            ),
            Recycler(
                name="PaperLoop Recycling",
                material_types="paper,cardboard",
                ward="Ward 12",
                city="Bengaluru",
                contact_email="paper@example.org",
            ),
        ]
    )


db.commit()


# -------------------------------------------------------------------
# MATERIAL LISTINGS
# -------------------------------------------------------------------

recyclers = (
    db.query(Recycler)
    .order_by(Recycler.id.asc())
    .all()
)

if db.query(MaterialListing).count() == 0:
    db.add_all(
        [
            MaterialListing(
                material_type="plastic",
                recovery_stream="RECYCLABLE",
                quantity_kg=25.0,
                classification_confidence=0.82,
                source_location="Ward 12 collection center",
                status="AVAILABLE",
            ),
            MaterialListing(
                material_type="cardboard",
                recovery_stream="RECYCLABLE",
                quantity_kg=40.0,
                classification_confidence=0.91,
                source_location="Ward 18 market area",
                status="AVAILABLE",
            ),
        ]
    )


db.commit()

# This line intentionally does not create transactions.
# Transactions should be created through the API workflow.


db.close()

print(
    "Seed complete - PRJ_628 Phase 5 "
    "circular-economy data initialized"
)
