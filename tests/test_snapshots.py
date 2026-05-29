"""
test_snapshots.py
Unit tests for the snapshot serialisation helpers that don't need bpy.

Tests _props_to_dict / _dict_to_props / _sanitize directly.
Run with:  python tests/test_snapshots.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from utils.snapshots import _props_to_dict, _dict_to_props, _sanitize


class FakeBlRna:
    """Minimal stand-in for props.bl_rna.properties."""
    class Prop:
        def __init__(self, identifier):
            self.identifier = identifier

    def __init__(self, identifiers):
        self.properties = [self.Prop(i) for i in identifiers]


class FakeProps:
    building_width  = 6.0
    building_height = 4.0
    dome_size       = 2.5
    dome_enabled    = True
    arch_count      = 1
    active_preset   = "Timurid"

    def __init__(self):
        self.bl_rna = FakeBlRna([
            "rna_type",           # should be skipped
            "building_width",
            "building_height",
            "dome_size",
            "dome_enabled",
            "arch_count",
            "active_preset",
        ])


class TestPropsToDict(unittest.TestCase):
    def test_skips_rna_type(self):
        props = FakeProps()
        d = _props_to_dict(props)
        self.assertNotIn("rna_type", d)

    def test_captures_all_others(self):
        props = FakeProps()
        d = _props_to_dict(props)
        self.assertIn("building_width", d)
        self.assertIn("dome_enabled", d)
        self.assertIn("active_preset", d)

    def test_values_correct(self):
        props = FakeProps()
        d = _props_to_dict(props)
        self.assertAlmostEqual(d["building_width"], 6.0)
        self.assertEqual(d["dome_enabled"], True)
        self.assertEqual(d["active_preset"], "Timurid")


class TestDictToProps(unittest.TestCase):
    def test_restores_float(self):
        props = FakeProps()
        _dict_to_props(props, {"building_width": 10.0})
        self.assertAlmostEqual(props.building_width, 10.0)

    def test_restores_bool(self):
        props = FakeProps()
        _dict_to_props(props, {"dome_enabled": False})
        self.assertEqual(props.dome_enabled, False)

    def test_restores_int(self):
        props = FakeProps()
        _dict_to_props(props, {"arch_count": 3})
        self.assertEqual(props.arch_count, 3)

    def test_ignores_unknown_keys(self):
        props = FakeProps()
        # Should not raise
        _dict_to_props(props, {"nonexistent_key": 999})

    def test_roundtrip(self):
        props = FakeProps()
        d = _props_to_dict(props)
        props.building_width = 0.0
        _dict_to_props(props, d)
        self.assertAlmostEqual(props.building_width, 6.0)


class TestSanitize(unittest.TestCase):
    def test_keeps_alphanumeric(self):
        self.assertEqual(_sanitize("myBuild_01"), "myBuild_01")

    def test_replaces_slashes(self):
        result = _sanitize("my/build")
        self.assertNotIn("/", result)

    def test_empty_becomes_unnamed(self):
        self.assertEqual(_sanitize(""), "unnamed")
        self.assertEqual(_sanitize("   "), "unnamed")

    def test_spaces_kept(self):
        result = _sanitize("my build")
        self.assertIn(" ", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)