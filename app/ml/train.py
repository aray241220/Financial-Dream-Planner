"""Train, evaluate and select the salary-prediction model, then save it.

Predicts 5-year Future Salary from Age, City, Current Salary.
Selection rule: lower MAE wins; higher R2 breaks ties.
Run:  python -m app.ml.train
"""
from __future__ import annotations

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


def load_salary_data() -> pd.DataFrame:
    """Load salary_growth.csv (Age, City, Current Salary, Future Salary)."""
    df = pd.read_csv(config.SALARY_GROWTH_CSV)
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    df.columns = df.columns.str.strip()
    return df


def build_pipeline(regressor) -> Pipeline:
    """Wrap preprocessing + regressor so categoricals are one-hot encoded."""
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), config.CATEGORICAL_FEATURES),
        ],
        remainder="passthrough",  # keeps numeric Age
    )
    return Pipeline([("preprocess", preprocessor), ("model", regressor)])


def evaluate(pipeline: Pipeline, X_test, y_test) -> tuple[float, float]:
    preds = pipeline.predict(X_test)
    return mean_absolute_error(y_test, preds), r2_score(y_test, preds)


def select_better(results: dict) -> str:
    """Lower MAE wins; higher R2 breaks ties."""
    return min(results, key=lambda name: (results[name]["mae"], -results[name]["r2"]))


def train_and_select() -> tuple[str, float, float]:
    df = load_salary_data()
    X = df[config.FEATURE_COLUMNS]
    y = df[config.TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.TEST_SIZE, random_state=config.RANDOM_STATE
    )

    candidates = {
        "LinearRegression": LinearRegression(),
        "DecisionTree": DecisionTreeRegressor(random_state=config.RANDOM_STATE),
    }

    results: dict[str, dict] = {}
    for name, regressor in candidates.items():
        pipeline = build_pipeline(regressor)
        pipeline.fit(X_train, y_train)
        mae, r2 = evaluate(pipeline, X_test, y_test)
        results[name] = {"pipeline": pipeline, "mae": mae, "r2": r2}
        print(f"{name:16s}  MAE={mae:12.2f}  R2={r2:7.3f}")

    best_name = select_better(results)
    best = results[best_name]
    print(f"\nSelected: {best_name} (lower MAE, R2 tie-breaker)")

    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best["pipeline"], config.MODEL_PATH)
    print(f"Saved pipeline -> {config.MODEL_PATH}")

    return best_name, best["mae"], best["r2"]


if __name__ == "__main__":
    train_and_select()
