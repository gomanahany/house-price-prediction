from pathlib import Path

import joblib
from sklearn.pipeline import Pipeline


def load_model(path: Path) -> Pipeline:
    if not path.exists():
        raise FileNotFoundError(f"Model file was not found: {path}")
    return joblib.load(path)
