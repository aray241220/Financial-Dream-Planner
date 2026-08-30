"""Load the trained salary pipeline once and predict 5-year future salary.

The pipeline is loaded a single time (cached) and reused for every request; it
is never retrained here.
"""
from __future__ import annotations

from functools import lru_cache

import joblib
import pandas as pd

from app import config


@lru_cache(maxsize=1)
def get_model():
    """Load and cache the trained pipeline (loaded once, reused)."""
    if not config.MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found at {config.MODEL_PATH}. "
            "Train it first with: python -m app.ml.train"
        )
    return joblib.load(config.MODEL_PATH)


def predict_future_salary(age: int, city: str, current_salary: float) -> float:
    """Predict the 5-year future monthly salary for a fresher profile."""
    row = pd.DataFrame(
        [{"Age": age, "City": city, "Current Salary": current_salary}],
        columns=config.FEATURE_COLUMNS,
    )
    return float(get_model().predict(row)[0])


def get_feature_categories() -> dict[str, list[str]]:
    """Known category values per categorical feature, from the fitted encoder."""
    encoder = get_model().named_steps["preprocess"].named_transformers_["cat"]
    return {
        feature: sorted(categories.tolist())
        for feature, categories in zip(config.CATEGORICAL_FEATURES, encoder.categories_)
    }
