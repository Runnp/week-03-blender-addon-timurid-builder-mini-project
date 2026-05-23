"""
test_utils.py
Pure-Python unit tests for utility modules that do NOT require bpy.

Run with:
    python -m pytest tests/test_utils.py -v
or:
    python tests/test_utils.py

Tested modules:
  utils/math_utils.py
  utils/randomizer.py  (constraint logic only, no bpy props)
  utils/history.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Provide a minimal mathutils stub so tests run without Blender
import types
if "mathutils" not in sys.modules or not hasattr(sys.modules["mathutils"], "Vector"):
    _mu = types.ModuleType("mathutils")
    class _Vec:
        def __init__(self, v):
            self.x = v[0]; self.y = v[1]; self.z = v[2] if len(v) > 2 else 0.0
        def __add__(self, other):
            return _Vec((self.x + other.x, self.y + other.y, self.z + other.z))
        def __iter__(self):
            yield self.x; yield self.y; yield self.z
    _mu.Vector = _Vec
    sys.modules["mathutils"] = _mu

import math
import unittest

from utils.math_utils import (
    lerp, circle_points, dome_profile,
    minaret_taper, symmetric_x_positions
)
from utils.history import push, back, forward, clear, status, peek
from utils.randomizer import _apply_ratio_rules


# ---------------------------------------------------------------------------
# math_utils
# ---------------------------------------------------------------------------

class TestLerp(unittest.TestCase):
    def test_endpoints(self):
        self.assertAlmostEqual(lerp(0, 10, 0.0), 0.0)
        self.assertAlmostEqual(lerp(0, 10, 1.0), 10.0)

    def test_midpoint(self):
        self.assertAlmostEqual(lerp(0, 10, 0.5), 5.0)

    def test_negative(self):
        self.assertAlmostEqual(lerp(-5, 5, 0.5), 0.0)


class TestCirclePoints(unittest.TestCase):
    def test_count(self):
        pts = circle_points(8, 1.0)
        self.assertEqual(len(pts), 8)

    def test_radius(self):
        pts = circle_points(16, 3.0)
        for p in pts:
            r = math.sqrt(p.x ** 2 + p.y ** 2)
            self.assertAlmostEqual(r, 3.0, places=5)

    def test_z_param(self):
        pts = circle_points(4, 1.0, z=2.5)
        for p in pts:
            self.assertAlmostEqual(p.z, 2.5)


class TestDomeProfile(unittest.TestCase):
    def test_returns_n_plus_1(self):
        prof = dome_profile(8, 2.0)
        self.assertEqual(len(prof), 9)

    def test_equator_radius(self):
        prof = dome_profile(10, 3.0)
        r, z = prof[0]
        self.assertAlmostEqual(r, 3.0, places=4)

    def test_pole_radius(self):
        prof = dome_profile(10, 3.0)
        r, _ = prof[-1]
        self.assertAlmostEqual(r, 0.0, places=4)


class TestMinaretTaper(unittest.TestCase):
    def test_base(self):
        self.assertAlmostEqual(minaret_taper(1.0, 0.5, 0.0), 1.0)

    def test_top(self):
        self.assertAlmostEqual(minaret_taper(1.0, 0.5, 1.0), 0.5)


class TestSymmetricX(unittest.TestCase):
    def test_single(self):
        self.assertEqual(symmetric_x_positions(1, 4.0), [0.0])

    def test_two(self):
        pos = symmetric_x_positions(2, 4.0)
        self.assertAlmostEqual(pos[0], -2.0)
        self.assertAlmostEqual(pos[1],  2.0)

    def test_four_sorted(self):
        pos = symmetric_x_positions(4, 6.0)
        self.assertEqual(len(pos), 4)
        self.assertTrue(pos[0] < pos[1] < pos[2] < pos[3])


# ---------------------------------------------------------------------------
# history
# ---------------------------------------------------------------------------

class FakeProps:
    building_width  = 6.0
    building_height = 4.0
    arch_width      = 1.6
    arch_height     = 3.0
    dome_size       = 2.5
    dome_segments   = 16
    minaret_height  = 7.0
    minaret_radius  = 0.4
    minaret_segments = 12
    minaret_count   = 2
    arch_count      = 1
    courtyard_size  = 5.0
    building_depth  = 6.0


class TestHistory(unittest.TestCase):
    def setUp(self):
        clear()

    def test_push_and_status(self):
        push({"width": 5.0})
        st = status()
        self.assertEqual(st["total"], 1)
        self.assertEqual(st["cursor"], 0)

    def test_back_returns_none_when_empty(self):
        props = FakeProps()
        result = back(props)
        self.assertIsNone(result)

    def test_back_and_forward(self):
        props = FakeProps()
        push({"width": 4.0, "height": 3.0})
        push({"width": 8.0, "height": 6.0})
        self.assertEqual(status()["cursor"], 1)

        entry = back(props)
        self.assertIsNotNone(entry)
        self.assertEqual(status()["cursor"], 0)
        self.assertAlmostEqual(props.building_width, 4.0)

        entry2 = forward(props)
        self.assertIsNotNone(entry2)
        self.assertEqual(status()["cursor"], 1)
        self.assertAlmostEqual(props.building_width, 8.0)

    def test_push_clears_future(self):
        push({"width": 4.0})
        push({"width": 8.0})
        back(FakeProps())           # cursor at 0
        push({"width": 6.0})       # should drop the width=8 entry
        self.assertEqual(status()["total"], 2)
        self.assertEqual(status()["cursor"], 1)

    def test_peek(self):
        push({"width": 5.0})
        entry = peek()
        self.assertIsNotNone(entry)
        self.assertEqual(entry["width"], 5.0)

    def test_can_flags(self):
        push({"width": 1.0})
        push({"width": 2.0})
        st = status()
        self.assertTrue(st["can_back"])
        self.assertFalse(st["can_forward"])

        back(FakeProps())
        st2 = status()
        self.assertFalse(st2["can_back"])
        self.assertTrue(st2["can_forward"])


# ---------------------------------------------------------------------------
# randomizer ratio rules
# ---------------------------------------------------------------------------

class TestRatioRules(unittest.TestCase):
    def test_dome_clamped_to_building(self):
        v = {"dome_size": 100.0, "building_height": 4.0,
             "arch_height": 3.0, "arch_width": 1.6,
             "arch_count": 1, "building_width": 6.0,
             "minaret_height": 5.0}
        _apply_ratio_rules(v)
        self.assertLessEqual(v["dome_size"], 4.0 * 0.65)

    def test_minaret_taller_than_building(self):
        v = {"minaret_height": 1.0, "building_height": 4.0, "dome_size": 2.5,
             "arch_height": 3.0, "arch_width": 1.6,
             "arch_count": 1, "building_width": 6.0}
        _apply_ratio_rules(v)
        self.assertGreater(v["minaret_height"], v["building_height"])

    def test_arch_width_within_facade(self):
        v = {"arch_width": 99.0, "building_width": 6.0, "arch_count": 1,
             "arch_height": 3.0, "building_height": 4.0,
             "dome_size": 2.0, "minaret_height": 7.0}
        _apply_ratio_rules(v)
        self.assertLess(v["arch_width"], v["building_width"])


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)