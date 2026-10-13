import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from farmplan_guard import detect_conflicts, validate_schedule


class GuardTests(unittest.TestCase):
    def test_detects_duplicate_start_time_conflict(self):
        schedule = [
            {"time": "09:00", "task": "Irrigate", "duration": "20 min", "priority": "High"},
            {"time": "09:00", "task": "Inspect field", "duration": "30 min", "priority": "Medium"},
        ]
        self.assertEqual(len(detect_conflicts(schedule, workers=1)), 1)

    def test_no_conflict_with_enough_workers(self):
        schedule = [
            {"time": "09:00", "task": "Irrigate"},
            {"time": "09:00", "task": "Inspect field"},
        ]
        self.assertEqual(detect_conflicts(schedule, workers=2), [])

    def test_invalid_priority_is_reported(self):
        schedule = [{"time": "09:00", "task": "Work", "duration": "10 min", "priority": "Urgent"}]
        self.assertTrue(any("invalid priority" in error for error in validate_schedule(schedule)))

    def test_missing_fields_are_reported(self):
        self.assertGreaterEqual(len(validate_schedule([{"task": "Work"}])), 3)

    def test_workers_must_be_positive(self):
        with self.assertRaises(ValueError):
            detect_conflicts([], workers=0)


if __name__ == "__main__":
    unittest.main()
