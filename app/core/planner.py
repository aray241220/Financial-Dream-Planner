"""Orchestrate the full financial plan: salary -> costs -> SIP -> feasibility.

The model predicts 5-year future salary; the implied CAGR projects salary at each
goal's horizon (informational). Saving capacity is based on the user's current
salary.
"""
from __future__ import annotations

from functools import lru_cache

import pandas as pd

from app import config
from app.core import feasibility, inflation, investment
from app.ml.predictor import predict_future_salary


@lru_cache(maxsize=1)
def _load_costs() -> pd.DataFrame:
    df = pd.read_csv(config.CITY_GOAL_COSTS_CSV)
    df.columns = df.columns.str.strip()
    return df


def get_goal_costs(city: str, area_type: str = config.DEFAULT_AREA_TYPE) -> dict[str, float]:
    """Current one-time cost per goal for a city + area type (read from CSV)."""
    costs = _load_costs()
    match = costs[(costs["City"] == city) & (costs["Area_Type"] == area_type)]
    if match.empty:
        raise ValueError(f"No cost data for city={city!r}, area_type={area_type!r}.")
    row = match.iloc[0]
    return {goal: float(row[col]) for goal, col in config.GOAL_COST_COLUMNS.items()}


def get_cities() -> list[str]:
    """Cities available in the cost data."""
    return sorted(_load_costs()["City"].unique().tolist())


def get_area_types() -> list[str]:
    """Area types available in the cost data."""
    return sorted(_load_costs()["Area_Type"].unique().tolist())


def _salary_at(current_salary: float, annual_growth: float, years: float) -> float:
    """Current salary grown at `annual_growth` for `years`."""
    return current_salary * (1 + annual_growth) ** years


def build_plan(
    *,
    name: str,
    age: int,
    city: str,
    monthly_salary: float,
    marriage_years: float,
    car_years: float,
    home_years: float,
    saving_percentage: float,
    area_type: str = config.DEFAULT_AREA_TYPE,
) -> dict:
    """Produce the complete financial plan for the given profile."""
    predicted_future_salary = predict_future_salary(age, city, monthly_salary)
    horizon = config.SALARY_HORIZON_YEARS
    implied_cagr = (
        (predicted_future_salary / monthly_salary) ** (1 / horizon) - 1
        if monthly_salary > 0 else 0.0
    )

    current_costs = get_goal_costs(city, area_type)
    timelines = {"Marriage": marriage_years, "Car": car_years, "Home": home_years}

    goals: dict[str, dict] = {}
    combined_required = 0.0
    for goal in config.GOALS:
        years = timelines[goal]
        current_cost = current_costs[goal]
        fut_cost = inflation.future_cost(current_cost, years)
        sip = investment.required_monthly_sip(fut_cost, years)
        combined_required += sip
        goals[goal] = {
            "years": years,
            "current_cost": round(current_cost, 2),
            "future_cost": round(fut_cost, 2),
            "required_monthly_sip": round(sip, 2),
            "projected_salary_at_horizon": round(_salary_at(monthly_salary, implied_cagr, years), 2),
        }

    capacity = investment.monthly_saving_capacity(monthly_salary, saving_percentage)
    surplus = capacity - combined_required
    label = feasibility.classify(capacity, combined_required)

    return {
        "name": name,
        "area_type": area_type,
        "current_monthly_salary": round(float(monthly_salary), 2),
        "predicted_future_salary": round(predicted_future_salary, 2),
        "salary_horizon_years": horizon,
        "saving_percentage": saving_percentage,
        "monthly_saving_capacity": round(capacity, 2),
        "goals": goals,
        "combined_required_monthly_sip": round(combined_required, 2),
        "surplus_or_shortfall": round(surplus, 2),
        "feasibility": label,
        "summary": _summary(name, label, surplus),
        "disclaimer": config.DISCLAIMER,
    }


def _summary(name: str, label: str, surplus: float) -> str:
    if surplus >= 0:
        return (
            f"{name}, your plan looks {label.lower()}: your monthly saving capacity "
            f"covers all three goals with a surplus of Rs {surplus:,.0f}/month."
        )
    return (
        f"{name}, your plan is {label.lower()}: you fall short by "
        f"Rs {abs(surplus):,.0f}/month across the three goals. Consider raising your "
        f"saving %, extending timelines, or adjusting goals."
    )
