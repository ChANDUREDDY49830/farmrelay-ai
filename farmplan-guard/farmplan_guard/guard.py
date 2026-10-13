"""Dependency-free validators for machine-generated task schedules."""
from collections import defaultdict


def validate_schedule(schedule):
    """Return a list of validation errors for a simple list of task dictionaries."""
    errors = []
    if not isinstance(schedule, list):
        return ["schedule must be a list"]
    seen = set()
    for index, item in enumerate(schedule):
        if not isinstance(item, dict):
            errors.append(f"item {index} must be an object")
            continue
        for key in ("time", "task", "duration", "priority"):
            if not item.get(key):
                errors.append(f"item {index} is missing {key}")
        time = item.get("time")
        if time in seen:
            errors.append(f"duplicate start time: {time}")
        if time:
            seen.add(time)
        if item.get("priority") and item["priority"] not in {"Low", "Medium", "High"}:
            errors.append(f"item {index} has invalid priority")
    return errors


def detect_conflicts(schedule, workers):
    """Flag start-time buckets containing more tasks than available workers.

    This basic check groups tasks by exact start time. It does not infer task
    duration or detect overlapping intervals with different start times.
    """
    # bool is a subclass of int in Python, but True is not a meaningful worker count.
    if isinstance(workers, bool) or not isinstance(workers, int) or workers < 1:
        raise ValueError("workers must be a positive integer")
    if not isinstance(schedule, list):
        raise ValueError("schedule must be a list")
    by_time = defaultdict(list)
    for item in schedule:
        if not isinstance(item, dict) or not item.get("time") or not item.get("task"):
            continue
        by_time[str(item["time"])].append(str(item["task"]))
    conflicts = []
    for time, tasks in sorted(by_time.items()):
        if len(tasks) > workers:
            conflicts.append({
                "time": time,
                "tasks": tasks,
                "workers_available": workers,
                "workers_needed_at_least": len(tasks)
            })
    return conflicts
