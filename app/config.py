"""Central configuration: file paths, ML settings and documented assumptions.

Educational simulation only. The assumptions below (6% inflation, 12% investment
return) and the synthetic salary dataset are illustrative and do NOT guarantee
any real financial outcome.
"""
from pathlib import Path

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent  # project root (Assignment/)
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
STATIC_DIR = BASE_DIR / "app" / "static"

SALARY_GROWTH_CSV = DATA_DIR / "salary_growth.csv"
CITY_GOAL_COSTS_CSV = DATA_DIR / "city_goal_costs.csv"
MODEL_PATH = MODELS_DIR / "salary_model.joblib"

# --- ML settings ---
RANDOM_STATE = 42
TEST_SIZE = 0.2
SALARY_HORIZON_YEARS = 5           # the dataset's Future Salary is a 5-year figure
TARGET_COLUMN = "Future Salary"
NUMERIC_FEATURES = ["Age", "Current Salary"]
CATEGORICAL_FEATURES = ["City"]
FEATURE_COLUMNS = ["Age", "City", "Current Salary"]

# --- Financial assumptions (documented; NOT guarantees) ---
INFLATION_RATE = 0.06          # fixed 6% annual, used for goal-cost inflation
ANNUAL_RETURN_RATE = 0.12      # assumed 12% annual investment return
MONTHLY_RETURN_RATE = ANNUAL_RETURN_RATE / 12

# --- Goal cost lookup (city_goal_costs.csv) ---
DEFAULT_AREA_TYPE = "Central"
GOALS = ("Marriage", "Car", "Home")
GOAL_COST_COLUMNS = {
    "Marriage": "Marriage_Cost_Current",
    "Car": "Car_Cost_Current",
    "Home": "Home_Cost_Current",
}

# --- Feasibility thresholds ---
# Surplus >= 0 -> Achievable; shortfall within this fraction of capacity ->
# Challenging; larger shortfall -> Highly Challenging.
CHALLENGING_SHORTFALL_RATIO = 0.25

# --- Disclaimer (surface wherever results are shown) ---
DISCLAIMER = (
    "This is an educational financial-planning simulation. Salary growth is "
    "predicted by a model trained on a synthetic dataset; inflation (6%) and "
    "investment return (12%) are fixed assumptions. All figures are illustrative "
    "and do NOT guarantee any real financial outcome."
)
