import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from farmplan_guard import detect_conflicts


class BooleanWorkerCountTests(unittest.TestCase):
    def test_true_is_not_accepted_as_one_worker(self):
        with self.assertRaises(ValueError):
            detect_conflicts([], workers=True)

    def test_false_is_not_accepted_as_worker_count(self):
        with self.assertRaises(ValueError):
            detect_conflicts([], workers=False)


if __name__ == "__main__":
    unittest.main()
