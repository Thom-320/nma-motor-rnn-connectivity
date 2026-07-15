import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ResultIntegrityTests(unittest.TestCase):
    def _rows(self, relative_path):
        with (ROOT / relative_path).open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    def _assert_unique_checkpoints(self, rows):
        keys = {
            (row["seed"], row["p_value"], row["checkpoint_trial"])
            for row in rows
        }
        self.assertEqual(len(keys), len(rows))

    def test_primary_result_shape_and_unique_keys(self):
        checkpoints = self._rows("results/primary/checkpoints.csv")
        conditions = self._rows("results/primary/conditions.csv")
        self.assertEqual(len(checkpoints), 416)
        self.assertEqual(len(conditions), 32)
        self._assert_unique_checkpoints(checkpoints)

    def test_q1_result_shape(self):
        trials = self._rows("results/q1/trial_history.csv")
        checkpoints = self._rows("results/q1/checkpoints.csv")
        conditions = self._rows("results/q1/condition.csv")
        self.assertEqual(len(trials), 50)
        self.assertEqual(len(checkpoints), 11)
        self.assertEqual(len(conditions), 1)
        self.assertEqual([int(row["trial"]) for row in trials], list(range(1, 51)))

    def test_pilot_result_shape_and_unique_keys(self):
        checkpoints = self._rows("results/pilot/checkpoints.csv")
        conditions = self._rows("results/pilot/conditions.csv")
        self.assertEqual(len(checkpoints), 108)
        self.assertEqual(len(conditions), 12)
        self._assert_unique_checkpoints(checkpoints)


if __name__ == "__main__":
    unittest.main()
