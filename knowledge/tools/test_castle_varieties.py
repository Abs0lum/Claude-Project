"""FORCED VARIETY: no two castles in VARIETIES may share a ground-plan signature (plan, quad, keep corner, moat kind)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import castlegen as C  # noqa: E402


class TestVarietyDistinct(unittest.TestCase):
    def test_no_plan_signature_collisions(self):
        self.assertEqual(C.variety_collisions(), [])

    def test_check_catches_a_duplicate(self):
        self.assertTrue(C.variety_collisions([("B", "lord", 1), ("B", "lord", 1)]))

    def test_seeds_unique_per_skin_size(self):
        self.assertEqual(len(set(C.VARIETIES)), len(C.VARIETIES))


if __name__ == "__main__":
    unittest.main()
