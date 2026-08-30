import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

client = TestClient(app)

VALID_PAYLOAD = {
    "name": "Riya",
    "age": 26,
    "city": "Bangalore",
    "area_type": "Central",
    "monthly_salary": 45000,
    "marriage_years": 3,
    "car_years": 5,
    "home_years": 10,
    "saving_percentage": 30,
}


def test_health_ok():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_meta_lists_options():
    body = client.get("/meta").json()
    assert len(body["cities"]) == 10
    assert "Bangalore" in body["cities"]
    assert body["default_area_type"] == "Central"
    assert body["salary_horizon_years"] == 5
    assert body["disclaimer"]


def test_plan_happy_path():
    res = client.post("/plan", json=VALID_PAYLOAD)
    assert res.status_code == 200
    body = res.json()
    assert body["predicted_future_salary"] > body["current_monthly_salary"]
    assert body["salary_horizon_years"] == 5
    assert set(body["goals"]) == {"Marriage", "Car", "Home"}
    assert body["feasibility"] in {"Achievable", "Challenging", "Highly Challenging"}
    assert body["disclaimer"]


def test_plan_combined_sip_is_sum_of_goals():
    body = client.post("/plan", json=VALID_PAYLOAD).json()
    total = sum(g["required_monthly_sip"] for g in body["goals"].values())
    assert body["combined_required_monthly_sip"] == pytest.approx(total, rel=1e-6)


def test_plan_rejects_unknown_city():
    res = client.post("/plan", json={**VALID_PAYLOAD, "city": "Gotham"})
    assert res.status_code == 422
    assert "Unknown city" in res.text


def test_plan_rejects_out_of_range_saving_percentage():
    res = client.post("/plan", json={**VALID_PAYLOAD, "saving_percentage": 150})
    assert res.status_code == 422


def test_plan_rejects_underage():
    res = client.post("/plan", json={**VALID_PAYLOAD, "age": 10})
    assert res.status_code == 422


def test_plan_rejects_zero_timeline():
    res = client.post("/plan", json={**VALID_PAYLOAD, "home_years": 0})
    assert res.status_code == 422


def test_plan_rejects_missing_field():
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "city"}
    res = client.post("/plan", json=payload)
    assert res.status_code == 422
