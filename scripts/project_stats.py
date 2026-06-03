"""
project_stats.py
Headless build report — run without opening the Blender UI.

Prints a comprehensive report of the current .blend scene state:
  - Object count, vertex/face totals per generator type
  - Material list with node counts
  - Snapshot list (from bpy.data.texts)
  - Animation summary (keyframed objects, frame range)
  - Modifier inventory (subsurf levels, displace strength)
  - Estimated poly budget vs. platform targets
  - Config.json values in effect

Usage:
    blender --background your_scene.blend --python scripts/project_stats.py

Or against an empty scene to report the project structure:
    blender --background --python scripts/project_stats.py
"""

import bpy
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


# ---------------------------------------------------------------------------
# Poly budget targets
# ---------------------------------------------------------------------------

TARGETS = {
    "Game / Realtime":  50_000,
    "Archviz Preview": 300_000,
    "Render Quality":  2_000_000,
}

COLLECTION_NAMES = ["Registan", "Registan_Complex", "Registan_Scene"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _all_objects(col_name: str) -> list:
    objs = []
    if col_name not in bpy.data.collections:
        return objs
    col = bpy.data.collections[col_name]
    objs.extend(col.objects)
    for child in col.children:
        objs.extend(child.objects)
    return objs


def _classify_object(name: str) -> str:
    """Bucket object into generator category for grouping."""
    n = name.lower()
    for kw, label in [
        ("base",        "Base Building"),
        ("dome",        "Dome"),
        ("minaret",     "Minarets"),
        ("serefe",      "Balconies"),
        ("arch",        "Arches"),
        ("muqarnas",    "Muqarnas"),
        ("pishtaq",     "Pishtaq"),
        ("iwan",        "Iwan"),
        ("girih",       "Girih"),
        ("arcade",      "Arcade"),
        ("courtyard",   "Courtyard"),
        ("fountain",    "Fountain"),
        ("complex",     "Complex"),
        ("ground",      "Scene"),
        ("plaza",       "Complex"),
        ("wall_l",      "Arcade"),
        ("wall_r",      "Arcade"),
        ("wall_f",      "Arcade"),
    ]:
        if kw in n:
            return label
    return "Other"


def _sep(char="─", width=60):
    return char * width


# ---------------------------------------------------------------------------
# Report sections
# ---------------------------------------------------------------------------

def _report_geometry():
    print(_sep("═"))
    print("  GEOMETRY REPORT")
    print(_sep("═"))

    totals_by_cat: dict[str, dict] = {}
    grand_verts = 0
    grand_faces = 0
    grand_objs  = 0

    for col_name in COLLECTION_NAMES:
        objs = _all_objects(col_name)
        for obj in objs:
            if obj.type != "MESH" or not obj.data:
                continue
            cat = _classify_object(obj.name)
            v = len(obj.data.vertices)
            f = len(obj.data.polygons)
            if cat not in totals_by_cat:
                totals_by_cat[cat] = {"objs": 0, "verts": 0, "faces": 0}
            totals_by_cat[cat]["objs"]  += 1
            totals_by_cat[cat]["verts"] += v
            totals_by_cat[cat]["faces"] += f
            grand_verts += v
            grand_faces += f
            grand_objs  += 1

    if not totals_by_cat:
        print("  (no mesh objects found — generate a building first)")
    else:
        print(f"  {'Category':<20} {'Objects':>7} {'Vertices':>10} {'Faces':>10}")
        print(_sep())
        for cat, d in sorted(totals_by_cat.items()):
            print(f"  {cat:<20} {d['objs']:>7} {d['verts']:>10,} {d['faces']:>10,}")
        print(_sep())
        print(f"  {'TOTAL':<20} {grand_objs:>7} {grand_verts:>10,} {grand_faces:>10,}")

    print()

    # Poly budget check
    print("  POLY BUDGET CHECK")
    print(_sep())
    for label, target in TARGETS.items():
        pct = grand_faces / target * 100 if target else 0
        bar_w = 30
        filled = min(bar_w, int(pct / 100 * bar_w))
        bar = "█" * filled + "░" * (bar_w - filled)
        status = "✓" if grand_faces <= target else "✗"
        print(f"  {status} {label:<20} [{bar}] {pct:5.1f}%  ({target:,} target)")
    print()


def _report_materials():
    print(_sep("═"))
    print("  MATERIAL REPORT")
    print(_sep("═"))

    reg_mats = set()
    for col_name in COLLECTION_NAMES:
        for obj in _all_objects(col_name):
            if obj.type == "MESH":
                for slot in obj.material_slots:
                    if slot.material:
                        reg_mats.add(slot.material.name)

    if not reg_mats:
        print("  (no materials found)")
    else:
        print(f"  {'Material':<30} {'Nodes':>6} {'Uses':>6}")
        print(_sep())
        for mat_name in sorted(reg_mats):
            mat = bpy.data.materials[mat_name]
            node_count = len(mat.node_tree.nodes) if mat.use_nodes and mat.node_tree else 0
            uses = sum(
                1 for col_name in COLLECTION_NAMES
                for obj in _all_objects(col_name)
                if obj.type == "MESH"
                for slot in obj.material_slots
                if slot.material and slot.material.name == mat_name
            )
            print(f"  {mat_name:<30} {node_count:>6} {uses:>6}")
    print()


def _report_snapshots():
    print(_sep("═"))
    print("  SNAPSHOTS")
    print(_sep("═"))
    snaps = [t for t in bpy.data.texts if t.name.startswith("RegSnap_")]
    if not snaps:
        print("  (no snapshots saved)")
    else:
        for t in snaps:
            name = t.get("snapshot_name", t.name)
            chars = len(t.as_string())
            print(f"  • {name:<30}  ({chars} chars)")
    print()


def _report_animation():
    print(_sep("═"))
    print("  ANIMATION")
    print(_sep("═"))
    scene = bpy.context.scene
    print(f"  Frame range  : {scene.frame_start} → {scene.frame_end}")
    print(f"  Current frame: {scene.frame_current}")

    animated = []
    for col_name in COLLECTION_NAMES:
        for obj in _all_objects(col_name):
            if obj.animation_data and obj.animation_data.action:
                n_curves = len(obj.animation_data.action.fcurves)
                animated.append((obj.name, n_curves))
    if animated:
        print(f"  Animated objects: {len(animated)}")
        for name, nc in animated[:8]:
            print(f"    {name:<35} {nc} f-curves")
        if len(animated) > 8:
            print(f"    … and {len(animated) - 8} more")
    else:
        print("  (no animated objects)")
    print()


def _report_modifiers():
    print(_sep("═"))
    print("  MODIFIERS (Registan)")
    print(_sep("═"))
    mod_summary: dict[str, int] = {}
    for col_name in COLLECTION_NAMES:
        for obj in _all_objects(col_name):
            for mod in obj.modifiers:
                mod_summary[mod.type] = mod_summary.get(mod.type, 0) + 1
    if not mod_summary:
        print("  (no modifiers)")
    else:
        for mtype, count in sorted(mod_summary.items()):
            print(f"  {mtype:<25} × {count}")
    print()


def _report_config():
    print(_sep("═"))
    print("  CONFIG.JSON")
    print(_sep("═"))
    try:
        from utils.config import load_config, CONFIG_PATH
        cfg = load_config(force=True)
        print(f"  Path: {CONFIG_PATH}")
        if cfg:
            for k, v in sorted(cfg.items()):
                if k.startswith("_"):
                    continue
                print(f"  {k:<30} = {v}")
        else:
            print("  (config.json not found or empty)")
    except Exception as e:
        print(f"  (config load error: {e})")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + "  REGISTAN GENERATOR — PROJECT STATISTICS REPORT".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    print(f"  Blender  : {bpy.app.version_string}")
    print(f"  File     : {bpy.data.filepath or '(unsaved)'}")
    print()

    _report_geometry()
    _report_materials()
    _report_snapshots()
    _report_animation()
    _report_modifiers()
    _report_config()

    print(_sep("═"))
    print("  END OF REPORT")
    print(_sep("═"))
    print()


if __name__ == "__main__":
    main()
