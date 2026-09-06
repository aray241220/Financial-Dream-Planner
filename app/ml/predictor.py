"""Serve predictions from the persisted salary pipeline.

The joblib artifact is read once (memoized with lru_cache) and reused for every
call; nothing here ever fits a model.
"""
from __future__ import annotations

from functools import lru_cache

import joblib
import pandas as pd

from app import config


@lru_cache(maxsize=1)
def get_model():
    """Load the fitted pipeline from disk on first use, then keep it cached."""
    if not config.MODEL_PATH.exists():
        raise FileNotFoundError(
            f"No trained model at {config.MODEL_PATH}. "
            "Build one first with `python -m app.ml.train`."
        )
    return joblib.load(config.MODEL_PATH)


def predict_future_salary(age: int, city: str, current_salary: float) -> float:
    """Return the model's 5-year future monthly-salary estimate for one profile."""
    one_row = pd.DataFrame(
        [{"Age": age, "City": city, "Current Salary": current_salary}],
        columns=config.FEATURE_COLUMNS,
    )
    return float(get_model().predict(one_row)[0])


def get_feature_categories() -> dict[str, list[str]]:
    """Map each categorical feature to the values the fitted encoder learned."""
    fitted = get_model().named_steps["preprocess"].named_transformers_["cat"]
    return {
        column: sorted(values.tolist())
        for column, values in zip(config.CATEGORICAL_FEATURES, fitted.categories_)
    }