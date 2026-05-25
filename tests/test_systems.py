"""
test_systems.py
Pure-Python unit tests for systems added in pushes 24–27.

Covers:
  utils/config.py       — load, get, apply, sanitise
  utils/i18n.py         — translate, set_lang, fallback
  utils/animation.py    — _classify name regex
  utils/svg_export.py   — SVG primitive output, full file write

Run with:
    python -m pytest tests/test_systems.py -v
or:
    python tests/test_systems.py
"""

import sys, os, tempfile, json, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Minimal mathutils stub (same as test_utils.py)
import types
if "mathutils" not in sys.modules or not hasattr(sys.modules.get("mathutils", None), "Vector"):
    _mu = types.ModuleType("mathutils")
    class _Vec:
        def __init__(self, v):
            self.x = v[0]; self.y = v[1]
            self.z = v[2] if len(v) > 2 else 0.0
        def __add__(self, o): return _Vec((self.x+o.x, self.y+o.y, self.z+o.z))
        def __iter__(self): yield self.x; yield self.y; yield self.z
    _mu.Vector = _Vec
    sys.modules["mathutils"] = _mu


# ============================================================================
# config.py tests
# ============================================================================

from utils.config import get, apply_to_props, write_default_config, load_config, _CONFIG


class FakeProps:
    building_width  = 6.0
    building_height = 4.0
    dome_size       = 2.5
    dome_segments   = 16
    minaret_count   = 2
    minaret_height  = 7.0
    minaret_radius  = 0.4
    arch_count      = 1
    arch_height     = 3.0
    arch_width      = 1.6
    courtyard_size  = 5.0
    building_depth  = 6.0
    girih_enabled   = False
    girih_cell_size = 0.45
    weathering_intensity = 0.0
    anim_frames     = 120
    random_seed     = 42
    active_preset   = "Timurid"
    active_lod      = "MID"
    ui_language     = "EN"


class TestConfig(unittest.TestCase):

    def setUp(self):
        """Inject a known config dict directly into module cache."""
        import utils.config as cfg_mod
        cfg_mod._CONFIG = {
            "building_width":   9.0,
            "minaret_count":    4,
            "default_preset":   "Safavid",
            "girih_enabled":    True,
        }
        cfg_mod._LOADED = True

    def test_get_existing_key(self):
        self.assertEqual(get("default_preset"), "Safavid")

    def test_get_missing_key_default(self):
        self.assertIsNone(get("nonexistent"))
        self.assertEqual(get("nonexistent", "fallback"), "fallback")

    def test_apply_float(self):
        p = FakeProps()
        apply_to_props(p)
        self.assertAlmostEqual(p.building_width, 9.0)

    def test_apply_int(self):
        p = FakeProps()
        apply_to_props(p)
        self.assertEqual(p.minaret_count, 4)

    def test_apply_bool(self):
        p = FakeProps()
        apply_to_props(p)
        self.assertEqual(p.girih_enabled, True)

    def test_apply_string(self):
        p = FakeProps()
        apply_to_props(p)
        self.assertEqual(p.active_preset, "Safavid")

    def test_write_and_load(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                        delete=False) as f:
            tmp_path = f.name
        try:
            write_default_config(tmp_path)
            with open(tmp_path) as f:
                data = json.load(f)
            self.assertIn("building_width", data)
            self.assertIn("default_preset", data)
        finally:
            os.unlink(tmp_path)


# ============================================================================
# i18n.py tests
# ============================================================================

from utils.i18n import t, set_lang, current_lang, available_langs


class TestI18n(unittest.TestCase):

    def tearDown(self):
        set_lang("EN")  # reset after each test

    def test_english_passthrough(self):
        set_lang("EN")
        self.assertEqual(t("Generate Building"), "Generate Building")

    def test_uzbek_translation(self):
        set_lang("UZ")
        self.assertEqual(t("Generate Building"), "Bino Yaratish")

    def test_russian_translation(self):
        set_lang("RU")
        self.assertEqual(t("Generate Building"), "Создать Здание")

    def test_missing_key_fallback(self):
        set_lang("UZ")
        self.assertEqual(t("SomeUnknownKey"), "SomeUnknownKey")

    def test_set_invalid_lang_ignored(self):
        set_lang("FR")
        self.assertEqual(current_lang(), "EN")

    def test_available_langs_count(self):
        langs = available_langs()
        self.assertEqual(len(langs), 3)
        codes = [l[0] for l in langs]
        self.assertIn("EN", codes)
        self.assertIn("UZ", codes)
        self.assertIn("RU", codes)


# ============================================================================
# animation._classify tests
# ============================================================================

from utils.animation import _classify


class TestAnimClassify(unittest.TestCase):

    def test_base_building(self):
        self.assertEqual(_classify("Base_Building"), "base")

    def test_dome(self):
        self.assertEqual(_classify("Dome"), "dome")

    def test_minaret(self):
        self.assertEqual(_classify("Minaret_2"), "minaret")

    def test_arch(self):
        self.assertEqual(_classify("Arch_1"), "arch")

    def test_pishtaq_pier(self):
        self.assertEqual(_classify("Pishtaq_Pier_L"), "pishtaq")

    def test_fountain(self):
        self.assertEqual(_classify("Fountain_Basin"), "fountain")
        self.assertEqual(_classify("Fountain_Nozzle"), "fountain")

    def test_courtyard(self):
        self.assertEqual(_classify("Courtyard_Ground"), "courtyard")
        self.assertEqual(_classify("Complex_Plaza"), "courtyard")

    def test_muqarnas(self):
        self.assertEqual(_classify("Muqarnas"), "muqarnas")

    def test_unknown_falls_back_to_base(self):
        self.assertEqual(_classify("RandomObject_XYZ"), "base")


# ============================================================================
# svg_export.py tests
# ============================================================================

from utils.svg_export import export_floor_plan, _rect, _circle, _text


class TestSVGPrimitives(unittest.TestCase):

    def test_rect_contains_coords(self):
        r = _rect(10, 20, 100, 50, fill="#fff", stroke="#000", stroke_w=1)
        self.assertIn('x="10.0"', r)
        self.assertIn('y="20.0"', r)
        self.assertIn('width="100.0"', r)

    def test_rect_dashed(self):
        r = _rect(0, 0, 10, 10, fill="#f00", stroke="#000",
                  stroke_w=1, dash="4,2")
        self.assertIn("stroke-dasharray", r)

    def test_circle_coords(self):
        c = _circle(50, 60, 15, fill="blue", stroke="none", stroke_w=0)
        self.assertIn('cx="50.0"', c)
        self.assertIn('r="15.0"', c)

    def test_text_content(self):
        txt = _text(10, 10, "hello", size=12)
        self.assertIn("hello", txt)
        self.assertIn('font-size="12"', txt)


class TestSVGExport(unittest.TestCase):

    def _base_params(self, **overrides):
        p = {
            "width": 6.0, "depth": 6.0, "height": 4.0,
            "dome_size": 2.5, "arch_width": 1.6, "arch_count": 1,
            "minaret_count": 2, "minaret_radius": 0.4,
            "courtyard_enabled": False, "courtyard_size": 5.0,
            "fountain_enabled": False, "active_preset": "Timurid",
        }
        p.update(overrides)
        return p

    def test_svg_file_created(self):
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            path = f.name
        try:
            export_floor_plan(self._base_params(), path)
            self.assertTrue(os.path.isfile(path))
            with open(path) as f:
                content = f.read()
            self.assertTrue(content.startswith("<svg"))
            self.assertIn("</svg>", content)
        finally:
            os.unlink(path)

    def test_svg_contains_title(self):
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            path = f.name
        try:
            export_floor_plan(self._base_params(), path)
            with open(path) as f:
                content = f.read()
            self.assertIn("REGISTAN", content)
        finally:
            os.unlink(path)

    def test_svg_with_courtyard(self):
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            path = f.name
        try:
            export_floor_plan(
                self._base_params(courtyard_enabled=True,
                                  fountain_enabled=True),
                path
            )
            with open(path) as f:
                content = f.read()
            self.assertIn("hauz", content)
        finally:
            os.unlink(path)


# ============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)