"""
presets.py
Named architectural style presets for the Registan Generator.

Each preset is a dict of property values that maps 1-to-1 with
the keys in RegistanProperties. Applying a preset sets all
slider values in one click.

Styles inspired by:
  TIMURID   — Gur-e-Amir, Bibi-Khanym (Samarkand, 14th–15th c.)
  BUKHARAN  — Kalon Minaret, Mir-i-Arab madrasa (Bukhara, 12th–16th c.)
  SAFAVID   — Imam Mosque Isfahan proportions adapted to Central Asian form
  MINIMAL   — Simple study model, good for learning geometry
"""

from typing import Any


PRESETS: dict[str, dict[str, Any]] = {

    "Timurid": {
        "building_width": 8.0,
        "building_height": 5.0,
        "building_depth": 7.0,
        "dome_enabled": True,
        "dome_size": 3.2,
        "dome_segments": 24,
        "minaret_enabled": True,
        "minaret_count": 4,
        "minaret_height": 9.0,
        "minaret_radius": 0.42,
        "minaret_segments": 14,
        "arch_enabled": True,
        "arch_count": 1,
        "arch_height": 4.2,
        "arch_width": 2.4,
        "muqarnas_enabled": True,
        "muqarnas_tiers": 3,
        "courtyard_enabled": True,
        "courtyard_size": 7.0,
        "use_symmetry": True,
    },

    "Bukharan": {
        "building_width": 6.5,
        "building_height": 4.0,
        "building_depth": 6.0,
        "dome_enabled": True,
        "dome_size": 2.2,
        "dome_segments": 18,
        "minaret_enabled": True,
        "minaret_count": 2,
        "minaret_height": 11.0,   
        "minaret_radius": 0.32,
        "minaret_segments": 16,
        "arch_enabled": True,
        "arch_count": 3,
        "arch_height": 3.0,
        "arch_width": 1.4,
        "muqarnas_enabled": False,
        "muqarnas_tiers": 2,
        "courtyard_enabled": False,
        "courtyard_size": 5.0,
        "use_symmetry": True,
    },

    "Safavid": {
        "building_width": 10.0,
        "building_height": 6.0,
        "building_depth": 9.0,
        "dome_enabled": True,
        "dome_size": 4.0,
        "dome_segments": 32,
        "minaret_enabled": True,
        "minaret_count": 2,
        "minaret_height": 8.5,
        "minaret_radius": 0.5,
        "minaret_segments": 16,
        "arch_enabled": True,
        "arch_count": 1,
        "arch_height": 5.5,
        "arch_width": 3.2,
        "muqarnas_enabled": True,
        "muqarnas_tiers": 5,
        "courtyard_enabled": True,
        "courtyard_size": 12.0,
        "use_symmetry": True,
    },

    "Minimal": {
        "building_width": 5.0,
        "building_height": 3.0,
        "building_depth": 5.0,
        "dome_enabled": True,
        "dome_size": 1.8,
        "dome_segments": 12,
        "minaret_enabled": False,
        "minaret_count": 2,
        "minaret_height": 5.0,
        "minaret_radius": 0.35,
        "minaret_segments": 10,
        "arch_enabled": True,
        "arch_count": 1,
        "arch_height": 2.2,
        "arch_width": 1.2,
        "muqarnas_enabled": False,
        "muqarnas_tiers": 2,
        "courtyard_enabled": False,
        "courtyard_size": 4.0,
        "use_symmetry": True,
    },
}

PRESET_NAMES = list(PRESETS.keys())


def apply_preset(props, preset_name: str) -> bool:
    """
    Write preset values onto a RegistanProperties instance.
    Returns True on success, False if preset_name is unknown.
    """
    data = PRESETS.get(preset_name)
    if data is None:
        return False
    for key, value in data.items():
        if hasattr(props, key):
            setattr(props, key, value)
    return True
