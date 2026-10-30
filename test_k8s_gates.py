"""Tests for job.py against hand-built fixtures. Apache-2.0.

Every expected number below was worked out by hand from the fixtures (see the
comments), not by running job.py.
"""
import unittest

import job

# Shaped like kubernetes/website feature-gates/CSIMigration.md (trailing spaces kept).
CSI_TEXT = """---
# Removed from Kubernetes
title: CSIMigration
content_type: feature_gate

_build:
  list: never
  render: false

stages:
  - stage: alpha
    defaultValue: false
    fromVersion: "1.14"
    toVersion: "1.16"
  - stage: beta
    defaultValue: true
    fromVersion: "1.17"
    toVersion: "1.24"
  - stage: stable
    defaultValue: true
    fromVersion: "1.25"
    toVersion: "1.26"

removed: true
---
Enables shims and translation logic to route volume
operations from in-tree plugins to corresponding pre-installed CSI plugins
"""

# Shaped like feature-gates/HPAScaleToZero.md: still active, no removed flag.
HPA_TEXT = """---
title: HPAScaleToZero
content_type: feature_gate
_build:
  list: never
  render: false

stages:
  - stage: alpha
    defaultValue: false
    fromVersion: "1.16"
    toVersion: "1.36"
  - stage: beta
    defaultValue: true
    fromVersion: "1.37"
---
Enables setting `minReplicas` to 0 for `HorizontalPodAutoscaler`.
"""


def G(name, stages, removed=False):
    keys = ("stage", "defaultValue", "fromVersion", "toVersion")
    return {"name": name, "removed": removed, "stages": [dict(zip(keys, s)) for s in stages]}


FIXTURE = [
    # alpha 10, beta 11, stable 12: H1 fast (12 - 10 = 2); H2 old, stable 1 release after beta.
    G("A", [("alpha", "false", "1.10", "1.10"), ("beta", "true", "1.11", "1.11"),
            ("stable", "true", "1.12", "1.14")], True),
    # alpha 12, beta 16 (on), stable 26: H1 graduated, not fast; H2 old, 10 releases; H3 old.
    G("B", [("alpha", "false", "1.12", "1.15"), ("beta", "true", "1.16", "1.25"),
            ("stable", "true", "1.26", "1.27")], True),
    # alpha 15, removed without beta: H1 row, not graduated; abandoned.
    G("C", [("alpha", "false", "1.15", "1.20")], True),
    # enters at beta 20 (off), stable 23: H2 new, 3 releases; H3 old (20 is in 14-23), off.
    G("D", [("beta", "false", "1.20", "1.22"), ("stable", "true", "1.23", None)]),
    # beta 26 (off), still beta: H2 new, not stable; H3 new, off; H4 age 37 - 26 = 11.
    G("E", [("alpha", "false", "1.24", "1.25"), ("beta", "false", "1.26", None)]),
    # enters at beta 18 (on), still beta: H2 old, not stable; H3 old, on; H4 age 19.
    G("F", [("beta", "true", "1.18", None)]),
    # alpha 30, beta 31 (on), stable 33: H2 new, 2 releases; H3 new, on.
    G("G", [("alpha", "false", "1.30", "1.30"), ("beta", "true", "1.31", "1.32"),
            ("stable", "true", "1.33", None)]),
    # beta 37 (off): sets V = 37; H4 age 0; in no H2/H3 window.
    G("H", [("alpha", "false", "1.35", "1.36"), ("beta", "false", "1.37", None)]),
    # alpha 17, then deprecated and removed: H1 row, not graduated; abandoned.
    G("I", [("alpha", "false", "1.17", "1.19"), ("deprecated", "false", "1.20", "1.21")], True),
]


class TestParse(unittest.TestCase):
    def test_csi(self):
        self.assertEqual(job.parse_gate(CSI_TEXT), {
            "name": "CSIMigration", "removed": True, "stages": [
                {"stage": "alpha", "defaultValue": "false", "fromVersion": "1.14",
                 "toVersion": "1.16"},
                {"stage": "beta", "defaultValue": "true", "fromVersion": "1.17",
                 "toVersion": "1.24"},
                {"stage": "stable", "defaultValue": "true", "fromVersion": "1.25",
                 "toVersion": "1.26"}]})

    def test_hpa(self):
        g = job.parse_gate(HPA_TEXT)
        self.assertEqual(g["name"], "HPAScaleToZero")
        self.assertFalse(g["removed"])
        self.assertEqual([s["stage"] for s in g["stages"]], ["alpha", "beta"])
        self.assertNotIn("toVersion", g["stages"][1])
        f = job.facts(g)
        self.assertEqual(f["first"], {"alpha": 16, "beta": 37})
        self.assertEqual(f["default"], {"alpha": False, "beta": True})
        self.assertEqual((f["entry"], f["current"], f["last"]), ("alpha", "beta", 37))

    def test_ver(self):
        self.assertEqual(job.ver("1.14"), 14)
        self.assertEqual(job.ver('"1.9"'), 9)
        self.assertIsNone(job.ver("2.0"))
        self.assertIsNone(job.ver(None))

    def test_facts_d(self):
        f = job.facts(FIXTURE[3])
        self.assertEqual(f["first"], {"beta": 20, "stable": 23})
        self.assertEqual(f["default"], {"beta": False, "stable": True})
        self.assertEqual((f["entry"], f["current"], f["last"]), ("beta", "stable", 23))


class TestPredictions(unittest.TestCase):
    def setUp(self):
        self.m, self.F = job.compute(FIXTURE)

    def test_counts(self):
        self.assertEqual((self.m["n_gates"], self.m["n_with_stages"], self.m["n_removed"]),
                         (9, 9, 4))
        self.assertEqual(self.m["V"], 37)

    def test_h1(self):
        # alpha 10-18: A, B, C, I; graduated A, B; fast A.
        h = self.m["H1"]
        self.assertEqual((h["n"], h["graduated"], h["fast"]), (4, 2, 1))
        self.assertAlmostEqual(h["share_of_all"], 0.25)
        self.assertAlmostEqual(h["share_of_graduated"], 0.5)

    def test_h2(self):
        # old beta 10-18: A, B, F (A within 4); new beta 20-32: D, E, G (D, G within 4).
        h = self.m["H2"]
        self.assertEqual((h["old"]["n"], h["old"]["stable_within_4"]), (3, 1))
        self.assertEqual((h["new"]["n"], h["new"]["stable_within_4"]), (3, 2))
        self.assertAlmostEqual(h["old"]["share"], 1 / 3)
        self.assertAlmostEqual(h["new"]["share"], 2 / 3)
        self.assertTrue(h["full_follow_up"])

    def test_h3(self):
        # old beta 14-23: B on, F on, D off; new beta 24-33: E off, G on.
        h = self.m["H3"]
        self.assertEqual((h["old"]["n"], h["old"]["default_off"]), (3, 1))
        self.assertEqual((h["new"]["n"], h["new"]["default_off"]), (2, 1))
        self.assertAlmostEqual(h["new"]["share"], 0.5)

    def test_h4(self):
        # current beta: E (11), F (19), H (0); 8+ releases: E, F.
        h = self.m["H4"]
        self.assertEqual((h["n_current_beta"], h["beta_8_plus_releases"]), (3, 2))
        self.assertAlmostEqual(h["share"], 2 / 3)

    def test_grades(self):
        self.assertEqual(job.grade(self.m),
                         {"H1": "FAILED", "H2": "HELD", "H3": "HELD", "H4": "HELD"})

    def test_grade_nulls(self):
        m, F = job.compute([])
        self.assertEqual(F, [])
        self.assertIsNone(m["V"])
        self.assertEqual(set(job.grade(m).values()), {"NULL"})


class TestDescriptives(unittest.TestCase):
    def setUp(self):
        self.d = job.compute(FIXTURE)[0]["descriptives"]

    def test_stage_hists(self):
        self.assertEqual(self.d["entry_stage_hist"], {"alpha": 7, "beta": 2})
        self.assertEqual(self.d["current_stage_hist"], {"beta": 3, "removed": 4, "stable": 2})
        self.assertEqual(self.d["non_monotonic"], [])
        self.assertEqual(self.d["abandoned_without_stable"], 2)

    def test_durations(self):
        # beta -> stable: A 1, B 10, D 3, G 2. alpha -> stable: A 2, B 14, G 3.
        self.assertEqual(self.d["beta_to_stable_hist"], {"1": 1, "10": 1, "2": 1, "3": 1})
        self.assertEqual(self.d["alpha_to_stable_hist"], {"14": 1, "2": 1, "3": 1})

    def test_by_version(self):
        # beta releases with 4 releases of follow-up (<= 33): A 11, B 16, F 18, D 20, E 26, G 31.
        self.assertEqual(self.d["stable_within_4_by_beta_from"],
                         {"11": [1, 1], "16": [1, 0], "18": [1, 0], "20": [1, 1],
                          "26": [1, 0], "31": [1, 1]})
        self.assertEqual(self.d["beta_default_off_by_beta_from"]["37"], [1, 1])

    def test_oldest(self):
        self.assertEqual(self.d["oldest_current_beta"],
                         [["F", 18, True], ["E", 26, False], ["H", 37, False]])
        self.assertEqual(self.d["oldest_current_alpha"], [])


if __name__ == "__main__":
    unittest.main()
