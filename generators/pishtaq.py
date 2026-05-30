"""
pishtaq.py
Generates a pishtaq — the tall rectangular gateway portal that frames the
main iwan entrance on a Timurid facade.

A pishtaq consists of:
  1. Two vertical jamb piers flanking the arch (taller than the arch itself)
  2. A horizontal spandrel panel above the arch
  3. A stepped / crenellated crown parapet at the very top
  4. Shallow recessed panels on each jamb face (blind niches)

This generator is additive — it wraps around whatever arch geometry already
exists and is placed on the building's front face at the same X centre.

Phase 2 will add the muqarnas hood inside the spandrel zone and inlaid
tile calligraphy panels (calligraphy as extruded curves).
"""

import bpy
import bmesh
import math
from mathutils import Vector

from ..utils.material_utils import assign_wall_material, assign_material


def generate_pishtaq(p: dict) -> list:
    """
    Build a pishtaq portal and link objects into p["collection"].

    Extra keys consumed from p:
        pishtaq_width     float  — total portal width (default: arch_width * 2.8)
        pishtaq_height    float  — total portal height (default: building_height * 1.35)
        pishtaq_depth     float  — protrusion from wall face (default: 0.3)
        pishtaq_cx        float  — centre X (default: 0.0)
        pishtaq_crown_steps int  — stepped parapet notches (default: 5)

    Returns list of created objects.
    """
    col = p["collection"]
    front_y = p["depth"] / 2

    p_w = p.get("pishtaq_width",  p["arch_width"] * 2.8)
    p_h = p.get("pishtaq_height", p["height"] * 1.35)
    p_d = p.get("pishtaq_depth",  0.30)
    cx  = p.get("pishtaq_cx",     0.0)
    crown_steps = int(p.get("pishtaq_crown_steps", 5))

    arch_w = p["arch_width"]
    arch_h = p["arch_height"]

    pier_w = (p_w - arch_w) / 2          # width of each side pier
    spandrel_h = p_h - arch_h - 0.0      # height of zone above arch

    objects = []

    # --- Left pier ---
    objects.append(_box_obj(
        col, "Pishtaq_Pier_L",
        cx=cx - arch_w / 2 - pier_w / 2,
        cy=front_y + p_d / 2,
        cz=p_h / 2,
        sx=pier_w, sy=p_d, sz=p_h,
    ))

    # --- Right pier ---
    objects.append(_box_obj(
        col, "Pishtaq_Pier_R",
        cx=cx + arch_w / 2 + pier_w / 2,
        cy=front_y + p_d / 2,
        cz=p_h / 2,
        sx=pier_w, sy=p_d, sz=p_h,
    ))

    # --- Spandrel panel (above arch, between piers) ---
    if spandrel_h > 0.05:
        objects.append(_box_obj(
            col, "Pishtaq_Spandrel",
            cx=cx,
            cy=front_y + p_d / 2,
            cz=arch_h + spandrel_h / 2,
            sx=arch_w, sy=p_d, sz=spandrel_h,
        ))

    # --- Stepped crown parapet ---
    crown_objs = _stepped_crown(
        col, cx, front_y, p_w, p_h, p_d, crown_steps
    )
    objects.extend(crown_objs)

    # --- Blind niche recesses on each pier ---
    niche_objs = _blind_niches(col, cx, front_y, pier_w, p_h, p_d, arch_w)
    objects.extend(niche_objs)

    for obj in objects:
        assign_wall_material(obj)

    return objects


# ---------------------------------------------------------------------------
# Crown
# ---------------------------------------------------------------------------

def _stepped_crown(col, cx, front_y, p_w, p_h, p_d, steps):
    """
    Build a stepped merlons parapet above the pishtaq.
    Alternating tall / short blocks across the full portal width.
    """
    objects = []
    total_w = p_w
    block_w = total_w / (steps * 2)
    merlon_h = 0.35
    gap_h    = 0.18

    for i in range(steps * 2):
        is_merlon = (i % 2 == 0)
        h = merlon_h if is_merlon else gap_h
        bx = cx - total_w / 2 + block_w * i + block_w / 2
        obj = _box_obj(
            col, f"Crown_Block_{i}",
            cx=bx, cy=front_y + p_d / 2,
            cz=p_h + h / 2,
            sx=block_w * 0.92, sy=p_d * 0.9, sz=h,
        )
        objects.append(obj)
    return objects


# ---------------------------------------------------------------------------
# Blind niches
# ---------------------------------------------------------------------------

def _blind_niches(col, cx, front_y, pier_w, p_h, p_d, arch_w):
    """
    Two shallow recessed rectangular blind niches — one per pier face.
    Gives visual depth to the jamb surfaces.
    """
    objects = []
    niche_w  = pier_w * 0.55
    niche_h  = p_h * 0.45
    niche_d  = 0.06   # recess depth (additive slab that sits proud of wall)
    niche_z  = p_h * 0.30

    for side, label in [(-1, "L"), (1, "R")]:
        bx = cx + side * (arch_w / 2 + pier_w / 2)
        # Outer frame ring (slightly larger box)
        frame = _box_obj(
            col, f"NicheFrame_{label}",
            cx=bx, cy=front_y + p_d + niche_d / 2,
            cz=niche_z + niche_h / 2,
            sx=niche_w + 0.08, sy=niche_d, sz=niche_h + 0.08,
        )
        assign_material(frame, "dark_brick")
        # Inner panel (slightly recessed, lighter)
        inner = _box_obj(
            col, f"NicheInner_{label}",
            cx=bx, cy=front_y + p_d + niche_d * 0.3,
            cz=niche_z + niche_h / 2,
            sx=niche_w, sy=niche_d * 0.5, sz=niche_h,
        )
        assign_material(inner, "white_marble")
        objects += [frame, inner]

    return objects


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------

def _box_obj(col, name, cx, cy, cz, sx, sy, sz):
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj  = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)

    bm = bmesh.new()
    _bm_box(bm, Vector((cx, cy, cz)), sx, sy, sz)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj


def _bm_box(bm, center, sx, sy, sz):
    corners = [
        ( 1,  1, -1), ( 1, -1, -1), (-1, -1, -1), (-1,  1, -1),
        ( 1,  1,  1), ( 1, -1,  1), (-1, -1,  1), (-1,  1,  1),
    ]
    verts = [bm.verts.new(center + Vector((c[0]*sx/2, c[1]*sy/2, c[2]*sz/2)))
             for c in corners]
    bm.faces.new([verts[0], verts[1], verts[2], verts[3]])
    bm.faces.new([verts[4], verts[7], verts[6], verts[5]])
    bm.faces.new([verts[0], verts[4], verts[5], verts[1]])
    bm.faces.new([verts[1], verts[5], verts[6], verts[2]])
    bm.faces.new([verts[2], verts[6], verts[7], verts[3]])
    bm.faces.new([verts[3], verts[7], verts[4], verts[0]])
