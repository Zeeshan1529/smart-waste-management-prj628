from pathlib import Path
import json

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "waste_generation.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
)

MODEL_PATH = (
    MODEL_DIR
    / "waste_generation_model.joblib"
)

METRICS_PATH = (
    MODEL_DIR
    / "metrics.json"
)

FEATURE_IMPORTANCE_PATH = (
    MODEL_DIR
    / "feature_importance.csv"
)


FEATURES = [
    "ward",
    "day_of_week",
    "is_weekend",
    "month",
    "fill_level",
    "capacity_kg",
    "previous_day_kg",
    "avg_3_day_kg",
    "avg_7_day_kg",
]

TARGET = "waste_generated_kg"


df = pd.read_csv(DATA_PATH)

df["date"] = pd.to_datetime(df["date"])

df = df.sort_values("date").reset_index(drop=True)

X = df[FEATURES]
y = df[TARGET]


# Chronological split:
# earlier records -> training
# later records   -> testing
split_index = int(len(df) * 0.80)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]


categorical_features = ["ward"]

numeric_features = [
    feature
    for feature in FEATURES
    if feature not in categorical_features
]


preprocessor = ColumnTransformer(
    transformers=[
        (
            "ward",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False,
            ),
            categorical_features,
        ),
        (
            "numeric",
            "passthrough",
            numeric_features,
        ),
    ]
)


model = Pipeline(
    steps=[
        (
            "preprocess",
            preprocessor,
        ),
        (
            "model",
            RandomForestRegressor(
                n_estimators=250,
                random_state=42,
                min_samples_leaf=2,
                n_jobs=-1,
            ),
        ),
    ]
)


model.fit(
    X_train,
    y_train,
)


predictions = model.predict(X_test)


mae = mean_absolute_error(
    y_test,
    predictions,
)

rmse = mean_squared_error(
    y_test,
    predictions,
) ** 0.5

r2 = r2_score(
    y_test,
    predictions,
)


MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

joblib.dump(
    model,
    MODEL_PATH,
)


metrics = {
    "model": "RandomForestRegressor",
    "dataset": "simulated operational waste-generation data",
    "total_rows": int(len(df)),
    "training_rows": int(len(X_train)),
    "testing_rows": int(len(X_test)),
    "mae_kg": round(float(mae), 3),
    "rmse_kg": round(float(rmse), 3),
    "r2": round(float(r2), 4),
}

with open(
    METRICS_PATH,
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        metrics,
        file,
        indent=2,
    )


preprocess = model.named_steps["preprocess"]
regressor = model.named_steps["model"]

feature_names = preprocess.get_feature_names_out()

importance_df = (
    pd.DataFrame(
        {
            "feature": feature_names,
            "importance": regressor.feature_importances_,
        }
    )
    .sort_values(
        "importance",
        ascending=False,
    )
    .reset_index(drop=True)
)

importance_df.to_csv(
    FEATURE_IMPORTANCE_PATH,
    index=False,
)


print("Training complete.")
print()
print(f"Model: {MODEL_PATH}")
print(f"Metrics: {METRICS_PATH}")
print()
print("Evaluation metrics:")
print(f"MAE  : {mae:.3f} kg")
print(f"RMSE : {rmse:.3f} kg")
print(f"R²   : {r2:.4f}")
print()
print("Top features:")
print(importance_df.head(10).to_string(index=False))
