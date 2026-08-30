"use strict";

const rupee = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});
const money = (n) => rupee.format(Math.round(n));

const form = document.getElementById("plan-form");
const submitBtn = document.getElementById("submit-btn");
const formError = document.getElementById("form-error");
const results = document.getElementById("results");

const CATEGORY_FIELDS = {
  city: "cities",
  area_type: "area_types",
};

// Populate the dropdowns from /meta.
async function loadMeta() {
  try {
    const res = await fetch("/meta");
    if (!res.ok) throw new Error(`meta ${res.status}`);
    const meta = await res.json();
    for (const [field, key] of Object.entries(CATEGORY_FIELDS)) {
      const select = form.elements[field];
      select.innerHTML = "";
      for (const value of meta[key]) {
        const opt = document.createElement("option");
        opt.value = value;
        opt.textContent = value;
        select.appendChild(opt);
      }
    }
    if (meta.default_area_type) form.elements.area_type.value = meta.default_area_type;
    document.getElementById("disclaimer").textContent = meta.disclaimer || "";
  } catch (err) {
    showError("Could not load form options. Is the server running?");
  }
}

const NUMERIC = [
  "age", "monthly_salary", "saving_percentage",
  "marriage_years", "car_years", "home_years",
];

function collectPayload() {
  const data = Object.fromEntries(new FormData(form).entries());
  for (const key of NUMERIC) data[key] = Number(data[key]);
  return data;
}

function showError(message) {
  formError.textContent = message;
  formError.hidden = false;
}

function clearError() {
  formError.hidden = true;
  formError.textContent = "";
}

// Turn a FastAPI/Pydantic error body into a readable message.
function formatErrorBody(body) {
  if (!body || body.detail == null) return "Something went wrong.";
  if (typeof body.detail === "string") return body.detail;
  if (Array.isArray(body.detail)) {
    return body.detail
      .map((e) => {
        const field = Array.isArray(e.loc) ? e.loc[e.loc.length - 1] : "input";
        return `${field}: ${e.msg}`;
      })
      .join(" | ");
  }
  return "Invalid input.";
}

const FEASIBILITY_CLASS = {
  "Achievable": "ok",
  "Challenging": "warn",
  "Highly Challenging": "bad",
};

function render(plan) {
  // Summary + badge
  const badge = document.getElementById("feasibility-badge");
  badge.textContent = plan.feasibility;
  badge.className = "badge " + (FEASIBILITY_CLASS[plan.feasibility] || "warn");
  document.getElementById("summary-text").textContent = plan.summary;

  // Top stats
  document.getElementById("predicted-salary").textContent = money(plan.predicted_future_salary);
  document.getElementById("capacity").textContent = money(plan.monthly_saving_capacity);
  document.getElementById("combined-sip").textContent = money(plan.combined_required_monthly_sip);

  const surplusEl = document.getElementById("surplus");
  const s = plan.surplus_or_shortfall;
  surplusEl.textContent = (s >= 0 ? "+" : "\u2212") + money(Math.abs(s));
  surplusEl.className = "stat-value " + (s >= 0 ? "positive" : "negative");

  // Goal cards
  const container = document.getElementById("goal-cards");
  container.innerHTML = "";
  for (const [goal, g] of Object.entries(plan.goals)) {
    const card = document.createElement("div");
    card.className = "card goal-card";
    card.innerHTML = `
      <h3>${goal}<span class="years">${g.years} yr</span></h3>
      <div class="goal-row"><span class="k">Current cost</span><span class="v">${money(g.current_cost)}</span></div>
      <div class="goal-row"><span class="k">Future cost (6% infl.)</span><span class="v">${money(g.future_cost)}</span></div>
      <div class="goal-row sip"><span class="k">Monthly SIP needed</span><span class="v">${money(g.required_monthly_sip)}</span></div>
      <div class="goal-row"><span class="k">Projected salary then</span><span class="v">${money(g.projected_salary_at_horizon)}</span></div>
    `;
    container.appendChild(card);
  }

  if (plan.disclaimer) document.getElementById("disclaimer").textContent = plan.disclaimer;
  results.hidden = false;
  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearError();
  submitBtn.disabled = true;
  submitBtn.textContent = "Building...";
  try {
    const res = await fetch("/plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(collectPayload()),
    });
    const body = await res.json();
    if (!res.ok) {
      showError(formatErrorBody(body));
      return;
    }
    render(body);
  } catch (err) {
    showError("Network error while building the plan.");
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Build my plan";
  }
});

loadMeta();
