"""Data cleaning, feature engineering, training, and model export utilities."""
from __future__ import annotations

import json
import re
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC_FEATURES = ["carpet_area_sqft", "floor_num", "bathroom", "balcony", "car_parking"]
CATEGORICAL_FEATURES = ["location_grouped", "Furnishing", "Transaction", "Ownership", "facing"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TOP_LOCATION_COUNT = 50
DROP_COLUMNS = [
    "Index", "Title", "Description", "Amount(in rupees)", "Price (in rupees)",
    "Carpet Area", "Floor", "Bathroom", "Balcony", "Car Parking", "Society",
    "Super Area", "Dimensions", "Plot Area", "overlooking",
]


def parse_amount(value: object) -> float:
    """Convert listings such as '42 Lac' and '1.40 Cr' to INR; invalid values are NaN."""
    if not isinstance(value, str):
        return np.nan
    text = value.strip().lower().replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)\s*(lac|lakh|cr|crore)?", text)
    if not match:
        return np.nan
    number = float(match.group(1))
    unit = match.group(2)
    if unit in {"lac", "lakh"}:
        return number * 100_000
    if unit in {"cr", "crore"}:
        return number * 10_000_000
    return number if "call" not in text else np.nan


def parse_area_sqft(value: object) -> float:
    """Extract an area and normalize square metres to square feet."""
    if not isinstance(value, str):
        return np.nan
    text = value.strip().lower().replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if not match:
        return np.nan
    area = float(match.group(1))
    return area * 10.764 if "sqm" in text or "sq m" in text else area


def parse_floor(value: object) -> float:
    """Extract the current floor, treating Ground as 0 and Basement as -1."""
    if not isinstance(value, str):
        return np.nan
    text = value.strip().lower()
    if "ground" in text:
        return 0.0
    if "basement" in text:
        return -1.0
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(match.group()) if match else np.nan


def parse_numeric(value: object) -> float:
    """Extract the first numeric value from a messy numeric listing field."""
    if pd.isna(value):
        return np.nan
    match = re.search(r"\d+(?:\.\d+)?", str(value))
    return float(match.group()) if match else np.nan


def clean_data(raw: pd.DataFrame, top_location_count: int = TOP_LOCATION_COUNT) -> pd.DataFrame:
    """Create model-ready columns and remove rows with unusable targets/outlier ratios."""
    data = raw.copy()
    data["price_clean"] = data["Amount(in rupees)"].apply(parse_amount)
    data["carpet_area_sqft"] = data["Carpet Area"].apply(parse_area_sqft)
    data["floor_num"] = data["Floor"].apply(parse_floor)
    for source, target in [("Bathroom", "bathroom"), ("Balcony", "balcony"), ("Car Parking", "car_parking")]:
        data[target] = data[source].apply(parse_numeric)

    data = data.dropna(subset=["price_clean"])
    location = data["location"].fillna("Unknown").astype(str).str.strip()
    top_locations = location.value_counts().head(top_location_count).index
    data["location_grouped"] = location.where(location.isin(top_locations), "other")

    # Price per sqft is only meaningful where carpet area is present and positive.  Rows
    # without it remain so the pipeline's median imputer can still use valid listings.
    ratio = data["price_clean"] / data["carpet_area_sqft"]
    valid_ratio = ratio.replace([np.inf, -np.inf], np.nan).dropna()
    low, high = valid_ratio.quantile([0.01, 0.99])
    keep = ratio.isna() | ratio.between(low, high)
    data = data.loc[keep].copy()
# Super Area is 57.4% missing and overlaps conceptually with Carpet Area.
# We intentionally exclude it from the model because Carpet Area is better defined
# for this dataset and is the feature used by the frontend for prediction.
# Dimensions and Plot Area are entirely empty, while Title, Description, Society,
# and other raw fields are excluded because they are identifiers, free text,
# high-cardinality fields, or raw versions of engineered features.
    return data.drop(columns=DROP_COLUMNS, errors="ignore")


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), NUMERIC_FEATURES),
            ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), CATEGORICAL_FEATURES),
        ]
    )


def evaluate_model(name: str, model: Pipeline, x_train: pd.DataFrame, x_test: pd.DataFrame, y_train: pd.Series, y_test: pd.Series) -> tuple[dict, np.ndarray]:
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    return {
        "model": name,
        "MAE": mean_absolute_error(y_test, predictions),
        "RMSE": mean_squared_error(y_test, predictions) ** 0.5,
        "R2": r2_score(y_test, predictions),
    }, predictions


def train_and_export(data_path: str | Path, output_dir: str | Path) -> dict:
    """Train two pipelines, select the lowest-RMSE model, and export it with metadata."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(data_path)
    data = clean_data(raw)
    x = data[FEATURES]
    y = data["price_clean"]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    candidates = {
        "LinearRegression": Pipeline([("prep", build_preprocessor()), ("reg", LinearRegression())]),
        "RandomForestRegressor": Pipeline([("prep", build_preprocessor()), ("reg", RandomForestRegressor(n_estimators=10, max_features=0.8, min_samples_leaf=2, n_jobs=1, random_state=42))]),
    }
    results, fitted, predictions = [], {}, {}
    for name, model in candidates.items():
        metrics, pred = evaluate_model(name, model, x_train, x_test, y_train, y_test)
        results.append(metrics)
        fitted[name] = model
        predictions[name] = pred
    comparison = pd.DataFrame(results).sort_values("RMSE").reset_index(drop=True)
    best_name = comparison.loc[0, "model"]
    best_model = fitted[best_name]
    joblib.dump(best_model, output / "house_price.pkl")
    locations = sorted(data["location_grouped"].dropna().unique().tolist())
    (output / "locations.json").write_text(json.dumps(locations, indent=2), encoding="utf-8")
    comparison.to_csv(output / "model_metrics.csv", index=False)
    metadata = {
        "dataset_shape": list(raw.shape), "cleaned_rows": int(len(data)), "features": FEATURES,
        "best_model": best_name, "metrics": comparison.to_dict(orient="records"),
        "dropped_columns": DROP_COLUMNS,
        "dropped_columns_reason": (
    "Index is an identifier; Title and Description are free-text fields; "
    "Amount(in rupees) is the raw target text field replaced by price_clean; "
    "Price (in rupees) is a redundant price-per-square-foot field; "
    "raw Carpet Area, Floor, Bathroom, Balcony, and Car Parking fields are "
    "replaced by engineered numeric features; Society is high-cardinality; "
    "Dimensions and Plot Area are entirely empty; overlooking is unused; "
    "and Super Area is 57.4% missing and overlaps with Carpet Area. "
    "Carpet Area is retained as the primary area feature because it is better "
    "defined and is also the area input used by the frontend."
),
    }
    (output / "training_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    reloaded = joblib.load(output / "house_price.pkl")
    reload_prediction = float(reloaded.predict(x_test.iloc[[0]])[0])
    return {"raw": raw, "data": data, "x_test": x_test, "y_test": y_test, "predictions": predictions[best_name], "comparison": comparison, "best_name": best_name, "reload_prediction": reload_prediction, "metadata": metadata}
