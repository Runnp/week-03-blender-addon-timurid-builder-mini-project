"""
presets.py
Named architectural style presets for the Registan Generator.

Each preset is a COMPLETE dict — every property key is specified so
loading a preset fully resets the scene to a known clean state.
No leftover values from a previous session bleed through.

Proportions are historically grounded:
  - Dome radius ≈ 35–55% of wall height
  - Minarets always taller than building_height + dome_size
  - Arch height < 90% of wall height
  - Minaret radius / height ratio matches real structures

Styles:
  Timurid   — Gur-e-Amir / Bibi-Khanym, Samarkand (14th–15th c.)
  Bukharan  — Kalon Minaret / Mir-i-Arab, Bukhara (12th–16th c.)
  Safavid   — Shah Mosque proportions adapted to Central Asian context
  Karakhanid — Early pre-Timurid brick architecture (11th–12th c.)
  Minimal   — Clean study model, good for learning the generators
"""

from typing import Any


PRESETS: dict[str, dict[str, Any]] = {

    # -----------------------------------------------------------------------
    # TIMURID — Gur-e-Amir, Bibi-Khanym, Shah-i-Zinda
    # Wide body, tall drum, deep-blue ribbed dome, 4 slender minarets,
    # single grand iwan, muqarnas vault, open courtyard with fountain
    # -----------------------------------------------------------------------
    "Timurid": {
        # Building
        "building_width":         8.0,
        "building_height":        5.0,
        "building_depth":         7.0,
        # Dome — radius ~44% of wall height, good drum proportion
        "dome_enabled":           True,
        "dome_size":              2.2,
        "dome_segments":          24,
        # Minarets — 4 corner, slender, clearly taller than building + dome
        "minaret_enabled":        True,
        "minaret_count":          4,
        "minaret_height":         12.0,
        "minaret_radius":         0.38,
        "minaret_segments":       14,
        "balcony_enabled":        True,
        # Arch — single grand iwan
        "arch_enabled":           True,
        "arch_count":             1,
        "arch_height":            4.0,
        "arch_width":             2.6,
        # Muqarnas vault above iwan
        "muqarnas_enabled":       True,
        "muqarnas_tiers":         3,
        # Pishtaq portal framing the iwan
        "pishtaq_enabled":        True,
        "pishtaq_height_factor":  1.4,
        "pishtaq_width_factor":   2.6,
        "pishtaq_crown_steps":    6,
        # Iwan hall
        "iwan_enabled":           True,
        "iwan_depth_factor":      1.8,
        "iwan_side_niches":       True,
        "iwan_niche_count":       2,
        # Courtyard with fountain
        "courtyard_enabled":      True,
        "courtyard_size":         8.0,
        "fountain_enabled":       True,
        "fountain_spouts":        True,
        # Girih tile relief on facade
        "girih_enabled":          True,
        "girih_cell_size":        0.40,
        "girih_extrude":          0.030,
        "girih_dome_band":        True,
        # Arcade on side walls
        "arcade_enabled":         False,
        "arcade_bays":            0,
        "arcade_height_factor":   0.68,
        "arcade_back":            False,
        "arcade_roundel":         True,
        # Style
        "use_symmetry":           True,
        "weathering_intensity":   0.0,
        "active_lod":             "MID",
    },

    # -----------------------------------------------------------------------
    # BUKHARAN — Kalon Minaret, Mir-i-Arab Madrasa
    # Compact body, very tall slender minarets, low dome,
    # triple arcade facade, no courtyard
    # -----------------------------------------------------------------------
    "Bukharan": {
        "building_width":         7.0,
        "building_height":        4.5,
        "building_depth":         6.0,
        # Dome — smaller, flatter than Timurid
        "dome_enabled":           True,
        "dome_size":              1.8,
        "dome_segments":          18,
        # Minarets — Bukharan signature: very tall and very thin
        "minaret_enabled":        True,
        "minaret_count":          2,
        "minaret_height":         14.0,
        "minaret_radius":         0.30,
        "minaret_segments":       16,
        "balcony_enabled":        True,
        # Arch — three openings across the facade (triple arcade)
        "arch_enabled":           True,
        "arch_count":             3,
        "arch_height":            3.2,
        "arch_width":             1.5,
        "muqarnas_enabled":       False,
        "muqarnas_tiers":         2,
        "pishtaq_enabled":        False,
        "pishtaq_height_factor":  1.3,
        "pishtaq_width_factor":   2.4,
        "pishtaq_crown_steps":    5,
        "iwan_enabled":           False,
        "iwan_depth_factor":      1.6,
        "iwan_side_niches":       True,
        "iwan_niche_count":       2,
        # No courtyard — Bukharan madrasas have internal courtyards
        "courtyard_enabled":      False,
        "courtyard_size":         5.0,
        "fountain_enabled":       False,
        "fountain_spouts":        True,
        # Girih off — Bukharan style uses more terracotta brickwork
        "girih_enabled":          False,
        "girih_cell_size":        0.45,
        "girih_extrude":          0.030,
        "girih_dome_band":        False,
        # Blind arcade on side walls — characteristic of Bukharan style
        "arcade_enabled":         True,
        "arcade_bays":            0,
        "arcade_height_factor":   0.65,
        "arcade_back":            False,
        "arcade_roundel":         True,
        "use_symmetry":           True,
        "weathering_intensity":   0.0,
        "active_lod":             "MID",
    },

    # -----------------------------------------------------------------------
    # SAFAVID — Shah Mosque Isfahan proportions, Central Asian adaptation
    # Grand scale, massive dome, deep iwan with 5-tier muqarnas,
    # large courtyard, all features enabled
    # -----------------------------------------------------------------------
    "Safavid": {
        "building_width":         11.0,
        "building_height":        7.0,
        "building_depth":         10.0,
        # Dome — large, prominent, Isfahan-style silhouette
        "dome_enabled":           True,
        "dome_size":              3.5,
        "dome_segments":          32,
        # Minarets — 2 flanking the iwan, tall and elegant
        "minaret_enabled":        True,
        "minaret_count":          2,
        "minaret_height":         16.0,
        "minaret_radius":         0.45,
        "minaret_segments":       16,
        "balcony_enabled":        True,
        # Single grand iwan with deep muqarnas
        "arch_enabled":           True,
        "arch_count":             1,
        "arch_height":            6.0,
        "arch_width":             3.5,
        "muqarnas_enabled":       True,
        "muqarnas_tiers":         5,
        "pishtaq_enabled":        True,
        "pishtaq_height_factor":  1.5,
        "pishtaq_width_factor":   3.0,
        "pishtaq_crown_steps":    8,
        "iwan_enabled":           True,
        "iwan_depth_factor":      2.0,
        "iwan_side_niches":       True,
        "iwan_niche_count":       3,
        # Large open courtyard with fountain
        "courtyard_enabled":      True,
        "courtyard_size":         14.0,
        "fountain_enabled":       True,
        "fountain_spouts":        True,
        # Full girih relief
        "girih_enabled":          True,
        "girih_cell_size":        0.35,
        "girih_extrude":          0.035,
        "girih_dome_band":        True,
        "arcade_enabled":         True,
        "arcade_bays":            0,
        "arcade_height_factor":   0.70,
        "arcade_back":            False,
        "arcade_roundel":         True,
        "use_symmetry":           True,
        "weathering_intensity":   0.0,
        "active_lod":             "MID",
    },

    # -----------------------------------------------------------------------
    # KARAKHANID — Early Central Asian brick architecture
    # Compact, austere, tall minaret, minimal ornament,
    # typical of 11th–12th century Fergana Valley mosques
    # -----------------------------------------------------------------------
    "Karakhanid": {
        "building_width":         6.0,
        "building_height":        4.0,
        "building_depth":         6.0,
        # Low, restrained dome
        "dome_enabled":           True,
        "dome_size":              1.6,
        "dome_segments":          14,
        # Single tall minaret — Karakhanid signature
        "minaret_enabled":        True,
        "minaret_count":          1,
        "minaret_height":         13.0,
        "minaret_radius":         0.55,
        "minaret_segments":       12,
        "balcony_enabled":        False,
        # Simple single arch, no muqarnas, no pishtaq
        "arch_enabled":           True,
        "arch_count":             1,
        "arch_height":            3.0,
        "arch_width":             2.0,
        "muqarnas_enabled":       False,
        "muqarnas_tiers":         2,
        "pishtaq_enabled":        False,
        "pishtaq_height_factor":  1.2,
        "pishtaq_width_factor":   2.2,
        "pishtaq_crown_steps":    4,
        "iwan_enabled":           False,
        "iwan_depth_factor":      1.5,
        "iwan_side_niches":       False,
        "iwan_niche_count":       1,
        "courtyard_enabled":      False,
        "courtyard_size":         5.0,
        "fountain_enabled":       False,
        "fountain_spouts":        False,
        # No girih — earlier period, plainer brick surface
        "girih_enabled":          False,
        "girih_cell_size":        0.45,
        "girih_extrude":          0.030,
        "girih_dome_band":        False,
        # Blind arcade — the main decorative element in Karakhanid style
        "arcade_enabled":         True,
        "arcade_bays":            0,
        "arcade_height_factor":   0.60,
        "arcade_back":            True,
        "arcade_roundel":         False,
        "use_symmetry":           True,
        "weathering_intensity":   0.15,
        "active_lod":             "MID",
    },

    # -----------------------------------------------------------------------
    # MINIMAL — clean study model, all decorative features off
    # Good for learning the base generators or quick blockouts
    # -----------------------------------------------------------------------
    "Minimal": {
        "building_width":         5.0,
        "building_height":        3.5,
        "building_depth":         5.0,
        "dome_enabled":           True,
        "dome_size":              1.5,
        "dome_segments":          12,
        "minaret_enabled":        False,
        "minaret_count":          2,
        "minaret_height":         7.0,
        "minaret_radius":         0.35,
        "minaret_segments":       10,
        "balcony_enabled":        False,
        "arch_enabled":           True,
        "arch_count":             1,
        "arch_height":            2.5,
        "arch_width":             1.4,
        "muqarnas_enabled":       False,
        "muqarnas_tiers":         2,
        "pishtaq_enabled":        False,
        "pishtaq_height_factor":  1.2,
        "pishtaq_width_factor":   2.2,
        "pishtaq_crown_steps":    4,
        "iwan_enabled":           False,
        "iwan_depth_factor":      1.5,
        "iwan_side_niches":       False,
        "iwan_niche_count":       1,
        "courtyard_enabled":      False,
        "courtyard_size":         4.0,
        "fountain_enabled":       False,
        "fountain_spouts":        False,
        "girih_enabled":          False,
        "girih_cell_size":        0.45,
        "girih_extrude":          0.030,
        "girih_dome_band":        False,
        "arcade_enabled":         False,
        "arcade_bays":            0,
        "arcade_height_factor":   0.60,
        "arcade_back":            False,
        "arcade_roundel":         False,
        "use_symmetry":           True,
        "weathering_intensity":   0.0,
        "active_lod":             "LOW",
    },
}


PRESET_NAMES = list(PRESETS.keys())


def apply_preset(props, preset_name: str) -> bool:
    """
    Write preset values onto a RegistanProperties instance.
    Returns True on success, False if preset_name is unknown.
    Every key in the preset dict is written — this fully resets
    all sliders so no values from a previous session bleed through.
    """
    data = PRESETS.get(preset_name)
    if data is None:
        return False
    for key, value in data.items():
        if hasattr(props, key):
            try:
                setattr(props, key, value)
            except Exception as e:
                print(f"[Registan] preset set {key}={value} failed: {e}")
    return True
