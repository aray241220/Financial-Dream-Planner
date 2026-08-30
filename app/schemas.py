"""Pydantic request/response models for the /plan API with friendly validation.

Category fields (city, area_type) are validated against the values the cost data
actually knows, so users get a clear list of valid options instead of an opaque
failure.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app import config
from app.core import planner


@lru_cache(maxsize=1)
def _allowed() -> dict[str, list[str]]:
    """Valid category values per field (from the cost data)."""
    return {"City": planner.get_cities(), "Area_Type": planner.get_area_types()}


def _check(value: str, key: str, label: str) -> str:
    allowed = _allowed()[key]
    if value not in allowed:
        raise ValueError(f"Unknown {label} '{value}'. Choose one of: {', '.join(allowed)}.")
    return value


class PlanRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=18, le=65)
    city: str
    area_type: str = config.DEFAULT_AREA_TYPE
    monthly_salary: float = Field(gt=0, le=100_000_000)
    marriage_years: int = Field(ge=1, le=50)
    car_years: int = Field(ge=1, le=50)
    home_years: int = Field(ge=1, le=50)
    saving_percentage: float = Field(ge=0, le=100)

    @field_validator("city")
    @classmethod
    def _v_city(cls, v: str) -> str:
        return _check(v, "City", "city")

    @field_validator("area_type")
    @classmethod
    def _v_area_type(cls, v: str) -> str:
        return _check(v, "Area_Type", "area type")


class GoalBreakdown(BaseModel):
    years: int
    current_cost: float
    future_cost: float
    required_monthly_sip: float
    projected_salary_at_horizon: float


class PlanResponse(BaseModel):
    name: str
    area_type: str
    current_monthly_salary: float
    predicted_future_salary: float
    salary_horizon_years: int
    saving_percentage: float
    monthly_saving_capacity: float
    goals: dict[str, GoalBreakdown]
    combined_required_monthly_sip: float
    surplus_or_shortfall: float
    feasibility: str
    summary: str
    disclaimer: str
