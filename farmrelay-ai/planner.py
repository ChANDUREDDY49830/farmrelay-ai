"""Transparent, dependency-free planning tools for the FarmRelay AI demo.

All durations and the fertilizer figure are illustrative prototype assumptions,
not agronomic recommendations. No live weather or external AI service is called.
"""
from datetime import datetime, timezone, timedelta

ALLOWED_TASKS = {
    "Inspect crops", "Irrigation check", "Weed control", "Apply fertilizer",
    "Repair equipment", "Harvest ready crops",
}
RAIN_OPTIONS = {"none", "possible", "likely"}


def _number(data, key, label, minimum, maximum):
    try:
        value = float(data.get(key))
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be a number.")
    if not minimum <= value <= maximum:
        raise ValueError(f"{label} must be between {minimum} and {maximum}.")
    return value


def _clock(minutes_after_midnight):
    day_offset, minute_of_day = divmod(minutes_after_midnight, 24 * 60)
    clock = (datetime(2000, 1, 1, 0, 0) + timedelta(minutes=minute_of_day)).strftime("%H:%M")
    return clock if day_offset == 0 else f"Day +{day_offset} {clock}"


def build_plan(data):
    """Build a deterministic draft with a traceable sequence of planning checks."""
    if not isinstance(data, dict):
        raise ValueError("Request must be a JSON object.")

    acres = _number(data, "acres", "Farm size (acres)", 0.1, 10000)
    workers_value = _number(data, "workers", "Workers", 1, 1000)
    if not workers_value.is_integer():
        raise ValueError("Workers must be a whole number.")
    workers = int(workers_value)
    fertilizer = _number(data, "fertilizer_kg", "Fertilizer stock (kg)", 0, 1000000)
    rain = data.get("rain_forecast", "uncertain")
    if rain not in RAIN_OPTIONS:
        raise ValueError("Rain scenario must be none, possible, or likely.")

    crop = str(data.get("crop", "Mixed crops")).strip()[:80] or "Mixed crops"
    location = str(data.get("location", "My farm")).strip()[:80] or "My farm"
    requested = data.get("tasks", ["Inspect crops", "Irrigation check", "Weed control"])
    if not isinstance(requested, list):
        raise ValueError("Tasks must be a list.")
    if len(requested) > 30:
        raise ValueError("Choose no more than 30 tasks.")
    tasks = list(dict.fromkeys(str(task) for task in requested if str(task) in ALLOWED_TASKS))
    unknown_tasks = [str(task) for task in requested if str(task) not in ALLOWED_TASKS]
    if not tasks:
        tasks = ["Inspect crops"]

    warnings = []
    explanations = []
    checks = []
    schedule_specs = []

    checks.append({"name": "Input validation", "status": "passed", "detail": "Farm size, worker count, stock, weather scenario, and task list are within accepted limits."})
    checks.append({"name": "Weather scenario", "status": "demo-only", "detail": f"Using the user-selected '{rain}' scenario; this is not a live forecast."})
    if unknown_tasks:
        warnings.append("Some unrecognized tasks were ignored: " + ", ".join(unknown_tasks[:5]) + ("…" if len(unknown_tasks) > 5 else "."))

    # Task duration and crew estimates are illustrative, not operational guarantees.
    if "Inspect crops" in tasks:
        schedule_specs.append(("Inspect crops", max(20, round(acres * 10 / workers)), "High", "Start with a field check before committing labor or inputs.", 1))
    if "Harvest ready crops" in tasks:
        schedule_specs.append(("Harvest ready crops", max(30, round(acres * 45 / workers)), "High", "Prioritize only crops confirmed ready; verify maturity in the field.", 2))
    if "Repair equipment" in tasks:
        schedule_specs.append(("Repair equipment", 45, "Medium", "Check tools before labor-intensive work begins.", 1))
    if "Irrigation check" in tasks:
        if rain == "likely":
            schedule_specs.append(("Check soil moisture; defer irrigation decision", 20, "High", "Rain is marked likely; inspect soil moisture before deciding whether to irrigate.", 1))
        else:
            schedule_specs.append(("Irrigation check", 20, "Medium", "Check soil moisture and local conditions before watering.", 1))
    if "Apply fertilizer" in tasks:
        estimated_need = round(acres * 25, 1)  # demo-only assumption, not a recommendation
        if fertilizer < estimated_need:
            warnings.append(f"Fertilizer stock ({fertilizer:g} kg) is below the demo planning estimate ({estimated_need:g} kg for {acres:g} acres). Verify crop-specific requirements; no application is authorized.")
            schedule_specs.append(("Verify fertilizer requirement and stock", 20, "High", "Inventory check found a potential shortfall; do not apply based on this prototype estimate." , 1))
        elif rain == "likely":
            warnings.append("Rain is marked likely. Check the product label, local forecast, and qualified agronomy guidance before any fertilizer application.")
            schedule_specs.append(("Review fertilizer timing; do not auto-apply", 20, "High", "Weather and product-specific requirements need human review.", 1))
        else:
            schedule_specs.append(("Review fertilizer plan", 20, "Medium", f"Stock is above the demo estimate of {estimated_need:g} kg; verify the product label and crop-specific recommendation.", 1))
    else:
        estimated_need = round(acres * 25, 1)

    if "Weed control" in tasks:
        if rain == "likely":
            warnings.append("Rain is marked likely. Check product-label weather restrictions before any weed-control treatment.")
            reason = "Review weather and product-label restrictions before deciding whether to treat."
        else:
            reason = "Inspect the affected area and select an appropriate control method."
        schedule_specs.append(("Weed control assessment", 30, "Medium", reason, 1))

    # Sequence the shared crew so the prototype does not schedule overlapping work.
    cursor = 8 * 60
    schedule = []
    for task, duration_minutes, priority, reason, crew_needed in schedule_specs:
        start = cursor
        end = start + duration_minutes
        schedule.append({
            "time": _clock(start), "end_time": _clock(end), "task": task,
            "duration": f"{duration_minutes} min", "duration_minutes": duration_minutes,
            "priority": priority, "reason": reason,
            "workers_required_estimate": crew_needed,
            "staffing_status": "sufficient" if workers >= crew_needed else "review",
        })
        if workers < crew_needed:
            warnings.append(f"'{task}' has a demo crew estimate of {crew_needed} workers, but only {workers} are available. Reassign, postpone, or review before approval.")
        cursor = end

    checks.append({"name": "Inventory check", "status": "review" if any("Fertilizer stock" in w for w in warnings) else "passed", "detail": f"Available fertilizer: {fertilizer:g} kg; illustrative planning estimate: {estimated_need:g} kg. This estimate is not agronomic advice."})
    staffing_review = any(item[4] > workers for item in schedule_specs)
    checks.append({"name": "Staffing check", "status": "review" if staffing_review else "passed", "detail": f"{workers} worker(s) available; tasks are placed sequentially to avoid planned overlap. Crew sizes are rough demo estimates."})
    checks.append({"name": "Human approval gate", "status": "required", "detail": "This plan is a draft. No task is executed and no external service is triggered."})

    if rain == "possible":
        explanations.append("Rain is uncertain in this demo scenario. Re-check a current local forecast before weather-sensitive work.")
    elif rain == "likely":
        explanations.append("The rain setting is user-entered demo data, not a live weather forecast.")
    else:
        explanations.append("The no-rain setting is user-entered demo data, not a live weather forecast.")
    explanations.extend([
        "Task durations and crew requirements are illustrative scheduling assumptions, not field-performance guarantees.",
        "The fertilizer quantity is a demo-only arithmetic estimate; use crop-, soil-, and product-specific guidance before application.",
        "This transparent prototype uses deterministic rules. It does not call a generative AI model, live weather API, or farm equipment.",
    ])

    return {
        "project": "FarmRelay AI", "location": location, "crop": crop,
        "summary": f"Created a draft plan for {acres:g} acres with {workers} worker(s).",
        "schedule": schedule, "warnings": list(dict.fromkeys(warnings)),
        "explanations": explanations, "checks": checks,
        "inventory": {"fertilizer_kg_available": fertilizer, "planning_estimate_kg": estimated_need, "estimate_type": "illustrative-demo-only"},
        "workflow": ["Validate inputs", "Interpret selected scenario", "Check inventory", "Estimate staffing", "Sequence tasks", "Request human approval"],
        "approval_required": True, "status": "draft",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
