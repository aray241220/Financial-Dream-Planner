"""Fit two regressors on the salary-growth data, compare them, keep the winner.

Target: 5-year Future Salary. Inputs: Age, City, Current Salary.
Winner rule: smallest MAE; a larger R2 breaks ties. The chosen pipeline is
persisted with joblib so the API can load it once and reuse it.

Run:  python -m app.ml.train
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeRegressor

from app import config


@dataclass(frozen=True)
class Scored:
    """A fitted pipeline together with its held-out scores."""

    name: str
    mae: float
    r2: float
    pipeline: Pipeline


def read_training_frame() -> pd.DataFrame:
    """Read salary_growth.csv and discard any stray blank columns."""
    frame = pd.read_csv(config.SALARY_GROWTH_CSV)
    frame = frame.loc[:, ~frame.columns.str.startswith("Unnamed")]
    frame.columns = frame.columns.str.strip()
    return frame


def assemble_pipeline(regressor) -> Pipeline:
    """One-hot encode the categorical column(s); pass numerics straight through."""
    prep = ColumnTransformer(
        [("cat", OneHotEncoder(handle_unknown="ignore"), config.CATEGORICAL_FEATURES)],
        remainder="passthrough",
    )
    return Pipeline([("preprocess", prep), ("model", regressor)])


def candidate_models() -> Iterator[tuple[str, object]]:
    """Yield the regressors under comparison as (label, fresh estimator)."""
    yield "LinearRegression", LinearRegression()
    yield "DecisionTree", DecisionTreeRegressor(random_state=config.RANDOM_STATE)


def run() -> Scored:
    """Train, score, pick, and persist the better model; return the winner."""
    frame = read_training_frame()
    inputs = frame[config.FEATURE_COLUMNS]
    target = frame[config.TARGET_COLUMN]

    x_train, x_test, y_train, y_test = train_test_split(
        inputs, target, test_size=config.TEST_SIZE, random_state=config.RANDOM_STATE
    )

    scored: list[Scored] = []
    for label, regressor in candidate_models():
        pipe = assemble_pipeline(regressor).fit(x_train, y_train)
        predictions = pipe.predict(x_test)
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        scored.append(Scored(label, mae, r2, pipe))
        print(f"  {label:<16} MAE {mae:>12,.2f}   R2 {r2:>6.3f}")

    # Rank by MAE (ascending); the -R2 term lets a higher R2 win a tie.
    winner = min(scored, key=lambda s: (s.mae, -s.r2))
    print(f"\n  -> keeping {winner.name}  (lowest MAE, R2 as tie-break)")

    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(winner.pipeline, config.MODEL_PATH)
    print(f"  saved model -> {config.MODEL_PATH}")
    return winner


if __name__ == "__main__":
    run()