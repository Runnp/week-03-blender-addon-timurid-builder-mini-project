"""
randomizer.py
Controlled randomization of Registan building parameters.

"Controlled" means variation stays architecturally plausible:
  - Proportions respect real Timurid ratios (dome ~40–55% of wall height, etc.)
  - Minarets always taller than the building
  - Arch width always < building width / arch_count
  - Values clamped to the same min/max as the UI sliders

Two modes:
  FULL     — randomize everything within style constraints
  TWEAK    — nudge current values by ±tweak_pct percent (default 15%)
"""

import random
import math
from typing import Any


# ---------------------------------------------------------------------------
# Style constraint tables
# Each entry: (min, max, snap)
# snap = round to nearest N (0 = no snap)
# ---------------------------------------------------------------------------

_CONSTRAINTS = {
    # key                  min    max    snap
    "building_width":     (3.0,  14.0,  0.5),
    "building_depth":     (3.0,  14.0,  0.5),
    "building_height":    (2.5,  10.0,  0.5),
    "dome_size":          (1.0,   6.0,  0.25),
    "dome_segments":      (10,    32,   2),
    "minaret_count":      (0,     4,    1),
    "minaret_height":     (4.0,  14.0,  0.5),
    "minaret_radius":     (0.25,  0.8,  0.05),
    "minaret_segments":   (8,    20,    2),
    "arch_count":         (1,     4,    1),
    "arch_height":        (1.5,   6.0,  0.25),
    "arch_width":         (0.8,   3.0,  0.1),
    "courtyard_size":     (3.0,  12.0,  0.5),
    "muqarnas_tiers":     (1,     5,    1),
}

# Architectural ratio constraints applied AFTER random draw
# These enforce proportional realism
_RATIO_RULES = [
    # dome_size should be 35–65% of building_height
    ("dome_size",      "building_height", 0.35, 0.65),
    # minaret_height must be > building_height + dome_size * 1.1
    # (handled procedurally below)
    # arch_height < building_height * 0.9
    ("arch_height",    "building_height", 0.30, 0.88),
    # arch_width < building_width / arch_count * 0.65
    # (handled procedurally below)
]


def randomize_full(props, seed: int | None = None) -> dict[str, Any]:
    """
    Fully randomize all numeric properties while respecting architectural ratios.
    Returns the dict of values that were applied (useful for logging/undo info).
    """
    rng = random.Random(seed)
    values = {}

    # Draw each property independently within its constraint range
    for key, (lo, hi, snap) in _CONSTRAINTS.items():
        if isinstance(lo, int):
            v = rng.randint(int(lo), int(hi))
        else:
            v = rng.uniform(lo, hi)
            if snap:
                v = round(v / snap) * snap
        values[key] = v

    # Enforce ratio rules
    _apply_ratio_rules(values)

    # Write to props
    _apply_values(props, values)
    return values


def randomize_tweak(props, tweak_pct: float = 0.15, seed: int | None = None) -> dict[str, Any]:
    """
    Nudge every current value by ±tweak_pct (default 15%), clamped to constraints.
    Great for exploring nearby variations of a preset.
    """
    rng = random.Random(seed)
    values = {}

    for key, (lo, hi, snap) in _CONSTRAINTS.items():
        current = getattr(props, key, None)
        if current is None:
            continue
        span = (hi - lo) * tweak_pct
        delta = rng.uniform(-span, span)
        v = current + delta
        v = max(lo, min(hi, v))
        if isinstance(lo, int):
            v = int(round(v))
        elif snap:
            v = round(v / snap) * snap
        values[key] = v

    _apply_ratio_rules(values)
    _apply_values(props, values)
    return values


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _apply_ratio_rules(v: dict):
    """Mutate v in-place to satisfy architectural proportions."""

    # Dome size = 35–65% of wall height
    if "dome_size" in v and "building_height" in v:
        lo_r, hi_r = 0.35, 0.65
        v["dome_size"] = max(
            v["building_height"] * lo_r,
            min(v["dome_size"], v["building_height"] * hi_r)
        )

    # Arch height < 88% of building height
    if "arch_height" in v and "building_height" in v:
        v["arch_height"] = min(v["arch_height"], v["building_height"] * 0.88)
        v["arch_height"] = max(v["arch_height"], 1.2)

    # Arch width < building_width / arch_count * 0.6
    if all(k in v for k in ("arch_width", "building_width", "arch_count")):
        max_w = v["building_width"] / max(v["arch_count"], 1) * 0.6
        v["arch_width"] = min(v["arch_width"], max_w)
        v["arch_width"] = max(v["arch_width"], 0.7)

    # Minaret height > building_height + dome_size (always taller)
    if all(k in v for k in ("minaret_height", "building_height", "dome_size")):
        min_mh = v["building_height"] + v["dome_size"] * 1.05
        v["minaret_height"] = max(v["minaret_height"], min_mh)
        v["minaret_height"] = min(v["minaret_height"], 14.0)


def _apply_values(props, values: dict):
    for key, val in values.items():
        if hasattr(props, key):
            setattr(props, key, type(getattr(props, key))(val))