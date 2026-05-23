import bpy

from .presets import PRESET_NAMES

import sys as _s, os as _o
_s.path.insert(0, _o.path.dirname(_o.path.dirname(_o.path.abspath(__file__))))
from utils.lod import LOD_NAMES


class RegistanProperties(bpy.types.PropertyGroup):

    active_preset: bpy.props.EnumProperty(
        name="Preset",
        items=[(n, n, f"{n} style preset") for n in PRESET_NAMES],
        default=PRESET_NAMES[0],
        description="Architectural style preset",
    )

    active_lod: bpy.props.EnumProperty(
        name="Detail Level",
        items=[(n, n, f"{n} mesh detail") for n in LOD_NAMES],
        default="MID",
        description="Mesh resolution level (LOW / MID / HIGH)",
    )

    # --- Building base ---
    building_width: bpy.props.FloatProperty(
        name="Building Width",
        default=6.0,
        min=2.0,
        max=20.0,
        description="Width of the main building base",
    )
    building_height: bpy.props.FloatProperty(
        name="Building Height",
        default=4.0,
        min=1.0,
        max=15.0,
        description="Height of the main building walls",
    )
    building_depth: bpy.props.FloatProperty(
        name="Building Depth",
        default=6.0,
        min=2.0,
        max=20.0,
        description="Depth of the main building base",
    )

    # --- Dome ---
    dome_enabled: bpy.props.BoolProperty(
        name="Dome",
        default=True,
        description="Generate a dome on top of the building",
    )
    dome_size: bpy.props.FloatProperty(
        name="Dome Size",
        default=2.5,
        min=0.5,
        max=8.0,
        description="Radius of the dome",
    )
    dome_segments: bpy.props.IntProperty(
        name="Dome Segments",
        default=16,
        min=6,
        max=64,
        description="Horizontal ring segments for dome mesh quality",
    )

    # --- Minarets ---
    minaret_enabled: bpy.props.BoolProperty(
        name="Minarets",
        default=True,
        description="Generate corner minarets",
    )
    minaret_count: bpy.props.IntProperty(
        name="Minaret Count",
        default=2,
        min=0,
        max=4,
        description="Number of minarets (placed symmetrically)",
    )
    minaret_height: bpy.props.FloatProperty(
        name="Minaret Height",
        default=7.0,
        min=2.0,
        max=20.0,
        description="Total height of each minaret",
    )
    minaret_radius: bpy.props.FloatProperty(
        name="Minaret Radius",
        default=0.4,
        min=0.1,
        max=1.5,
        description="Radius of the minaret shaft",
    )
    minaret_segments: bpy.props.IntProperty(
        name="Minaret Segments",
        default=12,
        min=6,
        max=32,
    )

    # --- Arch / Iwan entrance ---
    arch_enabled: bpy.props.BoolProperty(
        name="Arch Entrance",
        default=True,
        description="Generate an iwan arch on the front face",
    )
    arch_count: bpy.props.IntProperty(
        name="Arch Count",
        default=1,
        min=1,
        max=5,
        description="Number of arch openings on the facade",
    )
    arch_height: bpy.props.FloatProperty(
        name="Arch Height",
        default=3.0,
        min=1.0,
        max=8.0,
    )
    arch_width: bpy.props.FloatProperty(
        name="Arch Width",
        default=1.6,
        min=0.5,
        max=4.0,
    )

    # --- Randomizer ---
    random_seed: bpy.props.IntProperty(
        name="Seed",
        default=42,
        min=0,
        max=99999,
        description="Random seed for reproducible variation",
    )
    random_tweak_pct: bpy.props.FloatProperty(
        name="Tweak %",
        default=15.0,
        min=1.0,
        max=50.0,
        description="How much Tweak nudges each value (percent of range)",
    )

    # --- Muqarnas ---
    muqarnas_enabled: bpy.props.BoolProperty(
        name="Muqarnas",
        default=False,
        description="Generate stalactite vault niche above arches",
    )
    muqarnas_tiers: bpy.props.IntProperty(
        name="Muqarnas Tiers",
        default=3,
        min=1,
        max=5,
        description="Number of concentric muqarnas rings",
    )

    # --- Pishtaq Portal ---
    pishtaq_enabled: bpy.props.BoolProperty(
        name="Pishtaq Portal",
        default=False,
        description="Generate a tall gateway portal framing the main arch",
    )
    pishtaq_height_factor: bpy.props.FloatProperty(
        name="Portal Height",
        default=1.35,
        min=1.05,
        max=2.0,
        description="Pishtaq height as a multiple of building height",
    )
    pishtaq_width_factor: bpy.props.FloatProperty(
        name="Portal Width",
        default=2.8,
        min=1.5,
        max=5.0,
        description="Pishtaq width as a multiple of arch width",
    )
    pishtaq_crown_steps: bpy.props.IntProperty(
        name="Crown Steps",
        default=5,
        min=2,
        max=12,
        description="Number of merlon pairs in the stepped crown parapet",
    )

    # --- Complex Generator ---
    complex_spacing: bpy.props.FloatProperty(
        name="Building Gap",
        default=3.0,
        min=1.0,
        max=15.0,
        description="Space between the three buildings in the complex",
    )
    complex_apply_tiles: bpy.props.BoolProperty(
        name="Auto Tile Materials",
        default=True,
        description="Automatically apply tile materials after generating complex",
    )

    # --- Courtyard ---
    courtyard_enabled: bpy.props.BoolProperty(
        name="Courtyard",
        default=False,
        description="Generate an open courtyard in front",
    )
    courtyard_size: bpy.props.FloatProperty(
        name="Courtyard Size",
        default=5.0,
        min=2.0,
        max=20.0,
    )
    fountain_enabled: bpy.props.BoolProperty(
        name="Courtyard Fountain",
        default=False,
        description="Add an octagonal hauz fountain to the courtyard",
    )
    fountain_spouts: bpy.props.BoolProperty(
        name="Rim Spouts",
        default=True,
        description="Add 4 small spout jets around the basin rim",
    )

    # --- Symmetry ---
    use_symmetry: bpy.props.BoolProperty(
        name="Symmetry",
        default=True,
        description="Mirror elements across the X axis",
    )


def register():
    bpy.utils.register_class(RegistanProperties)
    bpy.types.Scene.registan = bpy.props.PointerProperty(type=RegistanProperties)


def unregister():
    del bpy.types.Scene.registan
    bpy.utils.unregister_class(RegistanProperties)