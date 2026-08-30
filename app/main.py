"""FastAPI app: POST /plan, GET /meta (form options), and static dashboard."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from app import config
from app.core import planner
from app.schemas import PlanRequest, PlanResponse

app = FastAPI(
    title="AI Financial Goal Planner & Salary Growth Predictor",
    description="Educational financial-planning simulation. " + config.DISCLAIMER,
    version="1.0.0",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model_ready": config.MODEL_PATH.exists()}


@app.get("/meta")
def meta() -> dict:
    """Valid form options for the dashboard dropdowns."""
    return {
        "cities": planner.get_cities(),
        "area_types": planner.get_area_types(),
        "goals": list(config.GOALS),
        "default_area_type": config.DEFAULT_AREA_TYPE,
        "salary_horizon_years": config.SALARY_HORIZON_YEARS,
        "disclaimer": config.DISCLAIMER,
    }


@app.post("/plan", response_model=PlanResponse)
def create_plan(req: PlanRequest) -> PlanResponse:
    try:
        plan = planner.build_plan(**req.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return PlanResponse(**plan)


# Serve the dashboard (index.html, style.css, script.js). Registered last so the
# API routes above take precedence.
app.mount("/", StaticFiles(directory=config.STATIC_DIR, html=True), name="static")
