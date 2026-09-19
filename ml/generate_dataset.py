from pathlib import Path

import numpy as np
import pandas as pd


RANDOM_SEED = 42
rng = np.random.default_rng(RANDOM_SEED)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "data" / "waste_generation.csv"

WARD_CONFIG = {
    "Ward 12": {"base": 82.0, "capacity": 120.0},
    "Ward 18": {"base": 96.0, "capacity": 150.0},
    "Ward 27": {"base": 68.0, "capacity": 100.0},
    "Ward 31": {"base": 108.0, "capacity": 180.0},
    "Ward 42": {"base": 76.0, "capacity": 110.0},
    "Ward 54": {"base": 88.0, "capacity": 140.0},
}

DATES = pd.date_range(
    start="2025-01-01",
    end="2025-08-31",
    freq="D",
)


rows = []

for ward, config in WARD_CONFIG.items():
    base = config["base"]
    capacity = config["capacity"]

    history = []

    for index, date in enumerate(DATES):
        day_of_week = int(date.weekday())
        is_weekend = int(day_of_week >= 5)
        month = int(date.month)

        previous_day = (
            history[-1]
            if history
            else base * 0.95
        )

        avg_3_day = (
            float(np.mean(history[-3:]))
            if history
            else base
        )

        avg_7_day = (
            float(np.mean(history[-7:]))
            if history
            else base
        )

        seasonal_effect = 10.0 * np.sin(
            2.0 * np.pi * index / 365.0
        )

        weekday_effect = {
            0: 2.0,
            1: -4.0,
            2: -2.0,
            3: 2.0,
            4: 8.0,
            5: 14.0,
            6: 10.0,
        }[day_of_week]

        fill_level = np.clip(
            22.0
            + (previous_day / capacity) * 65.0
            + rng.normal(0, 5.0),
            5.0,
            99.0,
        )

        waste_generated = (
            0.40 * base
            + 0.35 * previous_day
            + 0.15 * avg_7_day
            + 0.10 * capacity * (fill_level / 100.0)
            + seasonal_effect
            + weekday_effect
            + rng.normal(0, 6.0)
        )

        waste_generated = max(
            15.0,
            round(float(waste_generated), 2),
        )

        rows.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "ward": ward,
                "day_of_week": day_of_week,
                "is_weekend": is_weekend,
                "month": month,
                "fill_level": round(float(fill_level), 2),
                "capacity_kg": capacity,
                "previous_day_kg": round(
                    float(previous_day),
                    2,
                ),
                "avg_3_day_kg": round(
                    float(avg_3_day),
                    2,
                ),
                "avg_7_day_kg": round(
                    float(avg_7_day),
                    2,
                ),
                "waste_generated_kg": waste_generated,
            }
        )

        history.append(waste_generated)


df = pd.DataFrame(rows)

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

df.to_csv(
    OUTPUT_PATH,
    index=False,
)

print(f"Dataset created: {OUTPUT_PATH}")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print()
print(df.head())
