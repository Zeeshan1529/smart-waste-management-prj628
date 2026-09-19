from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "waste_generation_model.joblib"
)


@lru_cache(maxsize=1)
def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"ML model not found at {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def predict_waste_generation(
    ward: str,
    day_of_week: int,
    month: int,
    fill_level: float,
    capacity_kg: float,
    previous_day_kg: float,
    avg_3_day_kg: float,
    avg_7_day_kg: float,
):
    model = load_model()

    is_weekend = int(day_of_week >= 5)

    input_data = pd.DataFrame(
        [
            {
                "ward": ward,
                "day_of_week": day_of_week,
                "is_weekend": is_weekend,
                "month": month,
                "fill_level": fill_level,
                "capacity_kg": capacity_kg,
                "previous_day_kg": previous_day_kg,
                "avg_3_day_kg": avg_3_day_kg,
                "avg_7_day_kg": avg_7_day_kg,
            }
        ]
    )

    prediction = float(
        model.predict(input_data)[0]
    )

    return max(
        0.0,
        round(prediction, 2),
    )
