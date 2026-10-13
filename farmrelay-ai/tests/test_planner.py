import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from planner import build_plan


class PlannerTests(unittest.TestCase):
    def sample(self, **overrides):
        data = {
            "location": "Demo Farm", "crop": "Tomato", "acres": 2,
            "workers": 2, "fertilizer_kg": 20, "rain_forecast": "likely",
            "tasks": ["Inspect crops", "Irrigation check", "Apply fertilizer", "Weed control"]
        }
        data.update(overrides)
        return data

    def test_plan_flags_fertilizer_shortfall(self):
        result = build_plan(self.sample(fertilizer_kg=1))
        self.assertTrue(any("below the demo planning estimate" in warning for warning in result["warnings"]))

    def test_likely_rain_changes_irrigation_task(self):
        result = build_plan(self.sample())
        names = [task["task"] for task in result["schedule"]]
        self.assertIn("Check soil moisture; defer irrigation decision", names)

    def test_plan_requires_human_approval(self):
        result = build_plan(self.sample())
        self.assertTrue(result["approval_required"])
        self.assertEqual(result["status"], "draft")

    def test_invalid_rain_value_rejected(self):
        with self.assertRaises(ValueError):
            build_plan(self.sample(rain_forecast="monsoon definitely"))

    def test_invalid_acres_rejected(self):
        with self.assertRaises(ValueError):
            build_plan(self.sample(acres=0))

    def test_unknown_tasks_do_not_crash(self):
        result = build_plan(self.sample(tasks=["make coffee"]))
        self.assertGreaterEqual(len(result["schedule"]), 1)

    def test_schedule_is_sequential_and_has_end_times(self):
        result = build_plan(self.sample(rain_forecast="none"))
        schedule = result["schedule"]
        self.assertTrue(all(item.get("end_time") for item in schedule))
        for previous, current in zip(schedule, schedule[1:]):
            self.assertEqual(previous["end_time"], current["time"])

    def test_fractional_worker_count_rejected(self):
        with self.assertRaisesRegex(ValueError, "whole number"):
            build_plan(self.sample(workers=1.5))

    def test_duplicate_tasks_are_deduplicated(self):
        result = build_plan(self.sample(tasks=["Inspect crops", "Inspect crops"]))
        names = [item["task"] for item in result["schedule"]]
        self.assertEqual(names.count("Inspect crops"), 1)

    def test_decision_trace_includes_human_approval_gate(self):
        result = build_plan(self.sample())
        self.assertTrue(any(item["name"] == "Human approval gate" for item in result["checks"]))
        self.assertTrue(result["approval_required"])

    def test_harvest_with_one_worker_flags_staffing_review(self):
        result = build_plan(self.sample(workers=1, tasks=["Harvest ready crops"]))
        self.assertTrue(any("demo crew estimate" in warning for warning in result["warnings"]))

    def test_too_many_tasks_rejected(self):
        with self.assertRaisesRegex(ValueError, "no more than 30"):
            build_plan(self.sample(tasks=["Inspect crops"] * 31))


if __name__ == "__main__":
    unittest.main()
