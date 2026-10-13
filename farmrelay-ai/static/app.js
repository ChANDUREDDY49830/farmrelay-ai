const form = document.querySelector("#planner-form");
const output = document.querySelector("#plan-output");
const empty = document.querySelector("#empty-state");
const submitButton = form.querySelector('button[type="submit"]');

function formDataToPayload() {
  const fd = new FormData(form);
  return {
    location: fd.get("location"),
    crop: fd.get("crop"),
    acres: Number(fd.get("acres")),
    workers: Number(fd.get("workers")),
    fertilizer_kg: Number(fd.get("fertilizer_kg")),
    rain_forecast: fd.get("rain_forecast"),
    tasks: fd.getAll("tasks")
  };
}
function el(tag, cls, text) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text !== undefined) node.textContent = text;
  return node;
}
function renderPlan(plan) {
  output.replaceChildren();
  const summary = el("div", "summary-card");
  const status = el("div", "status-row");
  status.append(el("span", "draft-tag", "DRAFT · REVIEW REQUIRED"), el("span", "chip", `${plan.schedule.length} planned steps`));
  summary.append(status, el("p", "", `${plan.summary} ${plan.location} · ${plan.crop}.`));
  output.append(summary);

  const timeline = el("div", "timeline");
  plan.schedule.forEach(item => {
    const task = el("div", "task");
    task.append(el("div", "time", item.time));
    const rail = el("div", "rail"); rail.append(el("div", "rail-dot"));
    const content = el("div", "task-card");
    content.append(el("h4", "", item.task));
    const meta = el("div", "task-meta");
    meta.append(el("span", `chip ${item.priority === "High" ? "high" : ""}`, `${item.priority} priority`), el("span", "chip", item.duration));
    content.append(meta, el("p", "", item.reason));
    task.append(rail, content); timeline.append(task);
  });
  output.append(timeline);

  if (plan.warnings.length) {
    const warning = el("div", "warning-box"); warning.append(el("h4", "", `⚠ ${plan.warnings.length} item(s) need attention`));
    const list = el("ul");
    plan.warnings.forEach(w => list.append(el("li", "", w)));
    warning.append(list); output.append(warning);
  }
  const explain = el("div", "explain-box"); explain.append(el("h4", "", "Why this plan looks this way"));
  plan.explanations.forEach(reason => explain.append(el("p", "", `• ${reason}`)));
  output.append(explain);

  if (Array.isArray(plan.checks) && plan.checks.length) {
    const checksBox = el("div", "checks-box");
    checksBox.append(el("h4", "", "Planning checks & decision trail"));
    const checksList = el("div", "checks-list");
    plan.checks.forEach(check => {
      const row = el("div", "check-row");
      const state = String(check.status || "info").toUpperCase().replaceAll("-", " ");
      row.append(el("span", `check-state state-${check.status}`, state));
      const detail = el("div", "check-detail");
      detail.append(el("strong", "", check.name), el("p", "", check.detail));
      row.append(detail);
      checksList.append(row);
    });
    checksBox.append(checksList);
    output.append(checksBox);
  }

  const actions = el("div", "action-row");
  const approve = el("button", "primary", "✓ Approve draft");
  const revise = el("button", "secondary", "Revise inputs");
  const exportPlan = el("button", "secondary", "Export JSON");
  approve.type = revise.type = exportPlan.type = "button";
  actions.append(approve, revise, exportPlan); output.append(actions);
  exportPlan.addEventListener("click", () => {
    const blob = new Blob([JSON.stringify(plan, null, 2)], {type: "application/json"});
    const url = URL.createObjectURL(blob);
    const link = el("a");
    link.href = url;
    link.download = "farmrelay-plan.json";
    document.body.append(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  });
  approve.addEventListener("click", () => {
    const key = "farmrelay-approved-plan";
    try {
      localStorage.setItem(key, JSON.stringify({...plan, status: "approved-in-demo"}));
      const note = el("div", "approved", "✓ Plan approved in this demo and saved in this browser. No farm equipment or external service was triggered.");
      approve.disabled = true; approve.textContent = "✓ Approved";
      const draftTag = output.querySelector(".draft-tag");
      if (draftTag) draftTag.textContent = "APPROVED IN THIS DEMO";
      output.append(note);
    } catch {
      alert("Browser storage is unavailable. The plan remains visible, but could not be saved.");
    }
  });
  revise.addEventListener("click", () => {
    form.scrollIntoView({behavior: "smooth", block: "start"});
    form.querySelector('input[name="location"]').focus();
  });
  empty.hidden = true; output.hidden = false;
}
async function generatePlan() {
  submitButton.disabled = true;
  submitButton.firstChild.textContent = "Planning… ";
  try {
    const response = await fetch("/api/plan", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify(formDataToPayload())
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not generate plan.");
    renderPlan(data);
  } catch (err) {
    alert(`${err.message}\n\nMake sure the local server is running, then try again.`);
  } finally {
    submitButton.disabled = false;
    submitButton.firstChild.textContent = "✦";
  }
}
form.addEventListener("submit", async event => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  await generatePlan();
});
document.querySelector("#load-example").addEventListener("click", () => {
  form.elements.location.value = "Green Valley Farm";
  form.elements.crop.value = "Tomato";
  form.elements.acres.value = "2";
  form.elements.workers.value = "2";
  form.elements.fertilizer_kg.value = "20";
  form.elements.rain_forecast.value = "likely";
  form.querySelectorAll('input[name="tasks"]').forEach(input => {
    input.checked = ["Inspect crops", "Irrigation check", "Apply fertilizer", "Weed control"].includes(input.value);
  });
  generatePlan();
});
