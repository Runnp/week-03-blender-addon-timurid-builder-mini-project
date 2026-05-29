"""
headless_render.py
Headless render pipeline — run without opening the Blender UI.

Usage:
    blender --background --python scripts/headless_render.py -- [OPTIONS]

Options (pass after the double-dash):
    --preset    TIMURID | BUKHARAN | SAFAVID | MINIMAL   (default: TIMURID)
    --lod       LOW | MID | HIGH                          (default: MID)
    --outdir    path to output folder                     (default: demo_renders/)
    --samples   render sample count                       (default: 64)
    --tiles     apply tile materials                      (flag, default: off)
    --complex   generate full 3-building complex          (flag, default: off)
    --seed      random seed (0 = no randomize)            (default: 0)

Example:
    blender --background --python scripts/headless_render.py -- \\
        --preset SAFAVID --lod HIGH --tiles --samples 128 --outdir ./demo_renders

The script:
  1. Clears the default scene
  2. Applies the chosen preset to a dummy PropertyGroup
  3. Generates geometry (single building or complex)
  4. Applies tile materials (optional)
  5. Sets up lights + camera via scene_setup
  6. Renders to PNG at demo_renders/<preset>_<lod>_<seed>.png
"""

import bpy
import sys
import os
import argparse

# ---------------------------------------------------------------------------
# Path setup — add project root to sys.path
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from addon.presets import PRESETS, apply_preset
from utils.lod import apply_lod_to_props, apply_lod_modifiers, LOD_LEVELS
from utils.scene_setup import setup_scene
from utils.tile_material import apply_tile_materials_to_collection
from utils.randomizer import randomize_full

from generators.base_building import generate_base
from generators.dome import generate_dome
from generators.minaret import generate_minarets
from generators.arch import generate_arches
from generators.courtyard import generate_courtyard
from generators.muqarnas import generate_muqarnas
from generators.pishtaq import generate_pishtaq
from generators.complex_generator import generate_complex

COLLECTION_NAME = "Registan"


# ---------------------------------------------------------------------------
# Argument parsing (argv after the Blender separator --)
# ---------------------------------------------------------------------------

def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description="Registan headless renderer")
    parser.add_argument("--preset",  default="Timurid",
                        choices=list(PRESETS.keys()))
    parser.add_argument("--lod",     default="MID",
                        choices=["LOW", "MID", "HIGH"])
    parser.add_argument("--outdir",  default=os.path.join(PROJECT_ROOT, "demo_renders"))
    parser.add_argument("--samples", type=int, default=64)
    parser.add_argument("--tiles",   action="store_true")
    parser.add_argument("--complex", action="store_true", dest="do_complex")
    parser.add_argument("--seed",    type=int, default=0)
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Fake PropertyGroup (plain object that mimics bpy props for apply_preset)
# ---------------------------------------------------------------------------

class FakeProps:
    """Holds all RegistanProperties defaults as plain Python attributes."""

    # Defaults mirror properties.py
    active_preset = "Timurid"
    active_lod = "MID"
    building_width = 6.0
    building_depth = 6.0
    building_height = 4.0
    dome_enabled = True
    dome_size = 2.5
    dome_segments = 16
    minaret_enabled = True
    minaret_count = 2
    minaret_height = 7.0
    minaret_radius = 0.4
    minaret_segments = 12
    arch_enabled = True
    arch_count = 1
    arch_height = 3.0
    arch_width = 1.6
    muqarnas_enabled = False
    muqarnas_tiers = 3
    pishtaq_enabled = True
    pishtaq_height_factor = 1.35
    pishtaq_width_factor = 2.8
    pishtaq_crown_steps = 5
    courtyard_enabled = False
    courtyard_size = 5.0
    use_symmetry = True
    complex_spacing = 3.0
    complex_apply_tiles = False
    random_seed = 42
    random_tweak_pct = 15.0

    # Satisfy apply_preset / lod helpers
    bl_rna = None  # not needed for dict-based apply_preset


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    # 1. Clear default scene
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)

    # 2. Build params from preset
    props = FakeProps()
    preset_data = PRESETS.get(args.preset, {})
    for k, v in preset_data.items():
        if hasattr(props, k):
            setattr(props, k, v)

    # 3. Optional randomize
    if args.seed > 0:
        from utils.randomizer import randomize_full as _rf
        # randomize_full expects a props object; use simple dict-based fallback
        import random
        rng = random.Random(args.seed)
        props.building_width  = round(rng.uniform(4.0, 10.0) * 2) / 2
        props.dome_size       = props.building_height * rng.uniform(0.38, 0.60)
        props.minaret_height  = props.building_height + props.dome_size * 1.1 + rng.uniform(0, 2)

    # 4. Apply LOD to segment counts
    lod_cfg = LOD_LEVELS[args.lod]
    props.dome_segments     = lod_cfg.dome_segments
    props.minaret_segments  = lod_cfg.minaret_segments

    # 5. Build parameter dict
    p = {
        "width": props.building_width,
        "depth": props.building_depth,
        "height": props.building_height,
        "dome_size": props.dome_size,
        "dome_segments": props.dome_segments,
        "minaret_height": props.minaret_height,
        "minaret_radius": props.minaret_radius,
        "minaret_segments": props.minaret_segments,
        "minaret_count": props.minaret_count,
        "arch_count": props.arch_count,
        "arch_height": props.arch_height,
        "arch_width": props.arch_width,
        "muqarnas_enabled": props.muqarnas_enabled,
        "muqarnas_tiers": props.muqarnas_tiers,
        "courtyard_size": props.courtyard_size,
        "symmetry": props.use_symmetry,
        "complex_spacing": props.complex_spacing,
        "complex_apply_tiles": args.tiles,
    }

    # 6. Create collection + generate
    if COLLECTION_NAME in bpy.data.collections:
        col = bpy.data.collections[COLLECTION_NAME]
    else:
        col = bpy.data.collections.new(COLLECTION_NAME)
        bpy.context.scene.collection.children.link(col)
    p["collection"] = col

    if args.do_complex:
        generate_complex(p)
    else:
        generate_base(p)
        if props.dome_enabled:
            generate_dome(p)
        if props.minaret_enabled:
            generate_minarets(p)
        if props.arch_enabled:
            generate_arches(p)
            if props.pishtaq_enabled:
                p["pishtaq_height"] = props.building_height * props.pishtaq_height_factor
                p["pishtaq_width"]  = props.arch_width * props.pishtaq_width_factor
                p["pishtaq_crown_steps"] = props.pishtaq_crown_steps
                generate_pishtaq(p)
        if props.courtyard_enabled:
            generate_courtyard(p)

    # 7. Tile materials
    if args.tiles:
        apply_tile_materials_to_collection(col)

    # 8. LOD modifiers
    apply_lod_modifiers(COLLECTION_NAME, args.lod)

    # 9. Scene setup (lights + camera)
    setup_scene(p)

    # 10. Render settings
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT" if bpy.app.version >= (4, 0, 0) else "BLENDER_EEVEE"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = args.samples

    seed_tag = f"_s{args.seed}" if args.seed > 0 else ""
    fname = f"{args.preset}_{args.lod}{seed_tag}.png"
    outpath = os.path.join(args.outdir, fname)
    scene.render.filepath = outpath
    scene.render.image_settings.file_format = "PNG"

    print(f"\n[Registan] Rendering → {outpath}")
    bpy.ops.render.render(write_still=True)
    print(f"[Registan] Done.\n")


if __name__ == "__main__":
    main()