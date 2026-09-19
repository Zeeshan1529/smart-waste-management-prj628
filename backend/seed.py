from datetime import datetime, timedelta
from app.db import Base, engine, SessionLocal
from app.models import WasteBin, WasteReport

Base.metadata.create_all(bind=engine)
db = SessionLocal()

if db.query(WasteBin).count() == 0:
    bins = [
        WasteBin(code="BIN-101", ward="Ward 12", latitude=12.9718, longitude=77.5941, fill_level=88, capacity_kg=120),
        WasteBin(code="BIN-102", ward="Ward 12", latitude=12.9742, longitude=77.6000, fill_level=62, capacity_kg=100),
        WasteBin(code="BIN-205", ward="Ward 18", latitude=12.9352, longitude=77.6245, fill_level=94, capacity_kg=150),
        WasteBin(code="BIN-311", ward="Ward 27", latitude=12.9063, longitude=77.5857, fill_level=35, capacity_kg=100),
    ]
    db.add_all(bins)

if db.query(WasteReport).count() == 0:
    db.add_all([
        WasteReport(location="5th Main Road", ward="Ward 12", waste_type="Mixed", description="Overflowing roadside waste point", latitude=12.9720, longitude=77.5940, status="OPEN", created_at=datetime.utcnow()-timedelta(hours=2)),
        WasteReport(location="Market Road", ward="Ward 18", waste_type="Organic", description="Market waste after peak hours", latitude=12.9354, longitude=77.6242, status="IN_REVIEW", created_at=datetime.utcnow()-timedelta(hours=6)),
    ])

db.commit()
db.close()
print("Seed complete - MySQL database initialized with sample PRJ_628 data")
