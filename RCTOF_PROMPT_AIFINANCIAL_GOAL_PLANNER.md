RCTOF PROMPT — AI FINANCIAL GOAL PLANNER
R — ROLE
Act as a senior Python, Machine Learning, FastAPI and frontend developer. Build a complete, beginner-friendly, locally runnable academic project called “AI-Powered Financial Goal Planner & Salary Growth Predictor.”
C — CONTEXT
Build a local application for fresher students that predicts future salary using ML and creates a financial plan for Marriage, Car and Home goals. No RAG, paid API or cloud service is required. Experience must NOT be used as a feature because every user is a fresher.
T — TASK
Build the complete project with:
1. User Inputs
- Name
- Age
- City
- Current/Expected Monthly Salary
- Marriage timeline
- Car timeline
- Home timeline
- Salary saving/investment percentage
2. Dataset
Create/use:
- "salary_growth.csv": Age, City, Current Salary, Future Salary
- "city_goal_costs.csv": City, current Marriage, Car and Home costs
3. ML
- Preprocess categorical City properly.
- Train/test split with fixed random state.
- Train Linear Regression and Decision Tree Regressor.
- Evaluate both using MAE and R².
- Select the better model using a documented rule: lower MAE first, higher R² as tie-breaker.
- Save the selected preprocessing + model pipeline using Joblib.
- Load the saved model in the application; do not retrain on every request.
4. Salary Prediction
Predict future salary from Age, City and Current Salary. Clearly document the model's prediction period and how multiple goal timelines are handled. Do not falsely claim the model predicts arbitrary years unless the methodology supports it.
5. Future Goal Costs
Read current costs from "city_goal_costs.csv".
Use fixed 6% annual inflation:
"Future Cost = Current Cost × (1.06)^Years"
Show current cost, future cost and timeline separately for Marriage, Car and Home.
6. Investment Calculation
Calculate:
"Monthly Saving Capacity = Salary × Saving Percentage"
Calculate approximate monthly investment required for each goal using a mathematically correct SIP/future-value formula.
Document the assumed annual investment return, monthly rate, number of months and contribution timing. Clearly label the return as a project assumption, not a guarantee.
Show:
- Marriage investment requirement
- Car investment requirement
- Home investment requirement
- Combined requirement
Use predicted salary in planning where appropriate without double-counting.
7. Feasibility
Calculate:
"Surplus/Shortfall = Available Capacity − Required Investment"
Classify the plan as:
- Achievable
- Challenging
- Highly Challenging
Use and document clear thresholds. Allow users to change saving percentage and goal timelines and instantly recalculate.
8. Application
Use:
- Python
- FastAPI
- pandas
- NumPy
- scikit-learn
- Joblib
- HTML/CSS/JavaScript
Create a clean dashboard with input form, salary prediction, goal cards, investment requirements, savings capacity, surplus/shortfall, feasibility and final plan summary.
Provide a FastAPI endpoint such as:
"POST /plan"
with Pydantic validation and useful error messages. Keep ML prediction and financial calculations in separate reusable modules.
9. Optional Agentic AI
Agentic AI is optional. If implemented, use deterministic local tools for:
- Salary Prediction
- Future Cost
- Investment Calculation
- Feasibility
- Final Plan
The agent must never invent financial calculations. A rule-based orchestrator or local Ollama model may be used.
O — OUTPUT
Generate the complete runnable project, not pseudocode.
Include:
- Complete folder structure
- All source-code files with full code
- Both CSV datasets with suitable sample data
- Training/preprocessing/evaluation code
- Saved-model generation
- FastAPI backend
- Frontend
- Financial calculation modules
- Feasibility module
- Unit/API tests
- "requirements.txt"
- "README.md"
- "PROJECT_REPORT.md"
- DFD/architecture diagram
- API request/response examples
- Installation, training and execution commands
- Troubleshooting
- Final requirement checklist
Ensure every import, filename, CSV column and API/frontend connection is consistent and the project runs locally from scratch.
F — FINAL RULES
Do not use RAG, paid APIs, experience as a feature, hard-coded city costs, fake ML accuracy or guaranteed financial claims.
Clearly document all assumptions, especially:
- 6% inflation
- investment return
- model prediction horizon
- feasibility thresholds
Include the disclaimer that this is an educational financial-planning simulation and assumptions do not guarantee future financial outcomes.