# AI-Powered Financial Goal Planner & Salary Growth Predictor

A fully local, beginner-friendly academic project that predicts a fresher's
market salary with machine learning and builds an inflation-adjusted savings
plan for three life goals — **Marriage, Car, and Home** — served through a
FastAPI dashboard.

> **Disclaimer:** This is an **educational financial-planning simulation**. All
> predictions and assumptions (6% inflation, 8% salary growth, 12% investment
> return) are illustrative and do **not** guarantee any real financial outcome.

No RAG, no paid APIs, no cloud — everything runs on your machine.

---

## Features

- **Salary prediction** — scikit-learn model estimates **5-year future** monthly
  salary from `Age, City, Current Salary`.
- **Goal cost projection** — current city costs inflated at a fixed 6%/year.
- **Required SIP** — monthly investment per goal via an annuity-due formula.
- **Feasibility** — Achievable / Challenging / Highly Challenging.
- **Dashboard** — clean HTML/CSS/JS form with live result cards.

## Tech stack

Python, FastAPI, pandas, NumPy, scikit-learn, Joblib, and vanilla
HTML/CSS/JavaScript.

## Project structure

```
Assignment/
  app/
    main.py            FastAPI app: POST /plan, GET /meta, GET /health, static
    schemas.py         Pydantic request/response models + validation
    config.py          constants (paths, inflation, return, thresholds)
    ml/
      train.py         preprocess, split, train, evaluate, select, save
      predictor.py     load joblib pipeline once, predict salary
    core/
      inflation.py     future cost (6%)
      investment.py    required SIP + saving capacity
      feasibility.py   Achievable / Challenging / Highly Challenging
      planner.py       orchestrates the full plan (+ cost lookup)
    static/            index.html, style.css, script.js
  data/
    salary_data.csv            provided source (Age, City, Education, Job_Role, Monthly_Salary)
    salary_growth.csv          training set (Age, City, Current Salary, Future Salary)
    generate_salary_growth.py  builds salary_growth.csv (synthetic Future Salary)
    city_goal_costs.csv        City, Area_Type, Marriage/Car/Home_Cost_Current
  models/              salary_model.joblib (generated)
  tests/               unit + API tests
  requirements.txt
  README.md
```

## Prerequisites

- Python 3.11+ (developed on 3.14)
- pip

## Installation

```powershell
pip install -r requirements.txt
```

## 1) Train the model

The model is saved to `models/salary_model.joblib`. It is trained once and
loaded on demand — never retrained per request.

> The training file `data/salary_growth.csv` is included. It carries a
> **synthetic** `Future Salary` target (5-year horizon, growth varied by
> city/age with seeded noise). To regenerate it:
>
> ```powershell
> python data/generate_salary_growth.py
> ```

```powershell
python -m app.ml.train
```

Expected output (deterministic, fixed `random_state=42`):

```
LinearRegression  MAE=     3806.94  R2=  0.986
DecisionTree      MAE=     7650.00  R2=  0.917
Selected: LinearRegression (lower MAE, R2 tie-breaker)
Saved pipeline -> ...\models\salary_model.joblib
```

## 2) Run the app

```powershell
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 for the dashboard, or http://127.0.0.1:8000/docs for
the interactive API.

## API

### `POST /plan`

Request:

```json
{
  "name": "Riya",
  "age": 26,
  "city": "Bangalore",
  "area_type": "Central",
  "monthly_salary": 45000,
  "marriage_years": 3,
  "car_years": 5,
  "home_years": 10,
  "saving_percentage": 30
}
```

Response (abridged):

```json
{
  "name": "Riya",
  "current_monthly_salary": 45000.0,
  "predicted_future_salary": 84145.95,
  "salary_horizon_years": 5,
  "monthly_saving_capacity": 13500.0,
  "goals": {
    "Marriage": { "years": 3, "current_cost": 890000.0, "future_cost": 1060004.24, "required_monthly_sip": 24363.63, "projected_salary_at_horizon": 65509.6 },
    "Car":      { "years": 5, "current_cost": 1260000.0, "future_cost": 1686164.23, "required_monthly_sip": 20441.73, "projected_salary_at_horizon": 84145.95 },
    "Home":     { "years": 10, "current_cost": 9400000.0, "future_cost": 16833968.35, "required_monthly_sip": 72454.31, "projected_salary_at_horizon": 157345.35 }
  },
  "combined_required_monthly_sip": 117259.68,
  "surplus_or_shortfall": -103759.68,
  "feasibility": "Highly Challenging",
  "summary": "Riya, your plan is highly challenging: ...",
  "disclaimer": "This is an educational financial-planning simulation. ..."
}
```

### `GET /meta`

Returns valid dropdown options (cities, educations, job roles, area types,
goals) for the form.

### `GET /health`

Returns `{ "status": "ok", "model_ready": true }`.

## How it works

- **ML target:** the model predicts **5-year Future Salary**. Features are
  `Age, City, Current Salary`; `City` is one-hot encoded inside an sklearn
  `Pipeline`. Two models are trained (Linear Regression, Decision Tree) and the
  one with the **lower MAE** is selected (higher R² breaks ties). The training
  `Future Salary` column is **synthetic** (see `data/generate_salary_growth.py`).
- **Per-goal salary:** the implied 5-year CAGR (`current → predicted future`)
  projects salary at each goal's own horizon (informational).
- **Future cost:** `Current Cost × (1.06)^years`.
- **Required SIP (annuity-due):** `P = (FV × i) / (((1 + i)^n − 1) × (1 + i))`,
  where `i = 0.12 / 12` and `n = years × 12`.
- **Saving capacity:** `Current Salary × Saving%`.
- **Feasibility:** surplus ≥ 0 → Achievable; shortfall ≤ 25% of capacity →
  Challenging; otherwise Highly Challenging.

## Tests

```powershell
python -m pytest -q
```

24 tests cover inflation, investment (incl. an annuity-due round-trip),
feasibility band edges, and the API (happy path + validation errors).

## Troubleshooting

- **`uvicorn ... is not recognized`** — the Scripts folder isn't on PATH; run it
  as a module: `python -m uvicorn app.main:app --reload`.
- **`Model not found ...`** — run `python -m app.ml.train` first.
- **`ModuleNotFoundError`** — run `pip install -r requirements.txt`.
- **Run commands from the project root** (the `Assignment/` folder) so
  `python -m app.ml.train` and `python -m uvicorn app.main:app` resolve the
  `app` package.
- **Port already in use** — run uvicorn with a different `--port`.
