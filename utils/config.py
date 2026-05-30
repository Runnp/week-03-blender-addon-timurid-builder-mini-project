"""
config.py
Project-level configuration file system.

On addon register, loads `config.json` from the project root (the directory
containing this file's parent package). If found, values override the
built-in property defaults.

config.json example:
{
  "default_preset":      "Timurid",
  "default_lod":         "MID",
  "default_language":    "UZ",
  "building_width":      8.0,
  "building_height":     5.0,
  "dome_size":           3.0,
  "minaret_count":       4,
  "girih_enabled":       true,
  "weathering_intensity": 0.0,
  "render_samples":      128,
  "output_dir":          "./demo_renders"
}

All keys are optional. Unknown keys are silently ignored.
Config is re-read every time the addon registers (so changes take effect
after a Blender restart or addon reload).

Usage:
    from utils.config import load_config, get, CONFIG_PATH
    cfg = load_config()
    preset = get("default_preset", "Timurid")
"""

import json
import os

# Resolve config path relative to project root
_HERE = os.path.dirname(os.path.abspath(__file__))          # utils/
PROJECT_ROOT = os.path.dirname(_HERE)                        # project root
CONFIG_PATH  = os.path.join(PROJECT_ROOT, "config.json")

# Module-level cache
_CONFIG: dict = {}
_LOADED: bool = False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_config(force: bool = False) -> dict:
    """
    Load (or reload) config.json from PROJECT_ROOT.
    Returns the config dict. Returns {} if file doesn't exist.
    """
    global _CONFIG, _LOADED
    if _LOADED and not force:
        return _CONFIG

    if not os.path.isfile(CONFIG_PATH):
        _CONFIG = {}
        _LOADED = True
        return _CONFIG

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            _CONFIG = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[Registan] config.json load error: {e}")
        _CONFIG = {}

    _LOADED = True
    return _CONFIG


def get(key: str, default=None):
    """Return a config value by key, falling back to *default*."""
    return _CONFIG.get(key, default)


def apply_to_props(props) -> list[str]:
    """
    Write config values onto a RegistanProperties instance.
    Returns list of keys that were applied.
    """
    cfg = load_config()
    applied = []

    # Prop-key mapping: config key → properties attribute
    _MAP = {
        "default_preset":       "active_preset",
        "default_lod":          "active_lod",
        "default_language":     "ui_language",
        "building_width":       "building_width",
        "building_depth":       "building_depth",
        "building_height":      "building_height",
        "dome_size":            "dome_size",
        "dome_segments":        "dome_segments",
        "minaret_count":        "minaret_count",
        "minaret_height":       "minaret_height",
        "minaret_radius":       "minaret_radius",
        "arch_count":           "arch_count",
        "arch_height":          "arch_height",
        "arch_width":           "arch_width",
        "courtyard_size":       "courtyard_size",
        "girih_enabled":        "girih_enabled",
        "girih_cell_size":      "girih_cell_size",
        "weathering_intensity": "weathering_intensity",
        "anim_frames":          "anim_frames",
        "random_seed":          "random_seed",
    }

    for cfg_key, prop_key in _MAP.items():
        if cfg_key not in cfg:
            continue
        if not hasattr(props, prop_key):
            continue
        try:
            current = getattr(props, prop_key)
            val = cfg[cfg_key]
            if isinstance(current, bool):
                setattr(props, prop_key, bool(val))
            elif isinstance(current, int):
                setattr(props, prop_key, int(val))
            elif isinstance(current, float):
                setattr(props, prop_key, float(val))
            elif isinstance(current, str):
                setattr(props, prop_key, str(val))
            applied.append(prop_key)
        except Exception as e:
            print(f"[Registan] config apply error for {cfg_key}: {e}")

    return applied


def write_default_config(path: str = CONFIG_PATH):
    """
    Write a well-commented default config.json to *path*.
    Useful for first-time setup.
    """
    default = {
        "_comment": "Registan Generator — project config. All keys optional.",
        "default_preset":       "Timurid",
        "default_lod":          "MID",
        "default_language":     "EN",
        "building_width":       6.0,
        "building_depth":       6.0,
        "building_height":      4.0,
        "dome_size":            2.5,
        "dome_segments":        16,
        "minaret_count":        2,
        "minaret_height":       7.0,
        "minaret_radius":       0.4,
        "arch_count":           1,
        "arch_height":          3.0,
        "arch_width":           1.6,
        "courtyard_size":       5.0,
        "girih_enabled":        False,
        "girih_cell_size":      0.45,
        "weathering_intensity": 0.0,
        "anim_frames":          120,
        "random_seed":          42,
        "render_samples":       64,
        "output_dir":           "./demo_renders",
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(default, f, indent=2)
    print(f"[Registan] Default config written to {path}")
