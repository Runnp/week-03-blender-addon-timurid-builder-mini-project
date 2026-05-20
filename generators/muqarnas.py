"""
muqarnas.py
Generates a simplified muqarnas (stalactite vault) niche.

Muqarnas are the signature decorative vaulting system of Islamic architecture —
layered concave cells that fill the transition between a wall and a dome or arch.

Phase 1 approach:
  - N tiers of radially-arranged concave cells
  - Each tier is slightly smaller radius and higher Z than the one below
  - Cells alternate between "square" (rotated 45°) and "lozenge" forms
  - The result is a half-dome-shaped decorative canopy

Placement: typically used above arch entrances or under dome springings.
"""

import bpy
import bmesh
import math
from mathutils import Vector

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.material_utils import get_or_create_material


# Muqarnas cell colours — off-white stucco with slight warm tone
MUQARNAS_COLOUR = (0.88, 0.84, 0.76, 1.0)


def generate_muqarnas(p: dict) -> bpy.types.Object:
    """
    Create a muqarnas canopy and link it into p["collection"].

    Required keys in p:
        collection      bpy.types.Collection
        muqarnas_x      float  — centre X
        muqarnas_y      float  — centre Y (front face of building)
        muqarnas_z      float  — base Z (top of arch opening)
        muqarnas_radius float  — outer radius of lowest tier
        muqarnas_tiers  int    — number of concentric tiers (2–5)
    """
    col: bpy.types.Collection = p["collection"]
    cx: float = p.get("muqarnas_x", 0.0)
    cy: float = p.get("muqarnas_y", p["depth"] / 2)
    cz: float = p.get("muqarnas_z", p["arch_height"])
    radius: float = p.get("muqarnas_radius", p["arch_width"] * 0.5)
    tiers: int = int(p.get("muqarnas_tiers", 3))

    mesh = bpy.data.meshes.new("muqarnas_mesh")
    obj = bpy.data.objects.new("Muqarnas", mesh)
    col.objects.link(obj)

    bm = bmesh.new()

    tier_height = radius * 0.28
    cells_per_tier_base = 8  # doubles each tier for visual density

    for tier in range(tiers):
        t = tier / max(tiers - 1, 1)
        r_outer = radius * (1.0 - t * 0.72)
        r_inner = r_outer * 0.55
        z_bot = cz + tier * tier_height
        z_top = z_bot + tier_height * 0.85
        cell_depth = tier_height * 0.4

        n_cells = cells_per_tier_base * (tier + 1)
        # Only render the front-facing half (π arc)
        _add_tier_cells(
            bm,
            cx=cx, cy=cy,
            r_outer=r_outer, r_inner=r_inner,
            z_bot=z_bot, z_top=z_top,
            cell_depth=cell_depth,
            n_cells=n_cells,
            arc_start=-math.pi / 2,   # facing forward
            arc_end=math.pi / 2,
            alternate_offset=(tier % 2 == 1),
        )

    # Closing cap disc at the top
    _add_cap(bm, cx, cy, cz + tiers * tier_height, radius * 0.08)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    mat = get_or_create_material("muqarnas_stucco", MUQARNAS_COLOUR)
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    return obj


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _add_tier_cells(
    bm,
    cx, cy,
    r_outer, r_inner,
    z_bot, z_top,
    cell_depth,
    n_cells,
    arc_start, arc_end,
    alternate_offset: bool,
):
    """Add one tier of muqarnas cells arranged in an arc."""
    arc_span = arc_end - arc_start
    offset = (arc_span / n_cells / 2) if alternate_offset else 0.0

    for i in range(n_cells):
        t0 = i / n_cells
        t1 = (i + 1) / n_cells
        a0 = arc_start + offset + arc_span * t0
        a1 = arc_start + offset + arc_span * t1
        a_mid = (a0 + a1) / 2

        # Outer arc corners
        o0 = Vector((cx + math.cos(a0) * r_outer, cy + math.sin(a0) * r_outer, z_bot))
        o1 = Vector((cx + math.cos(a1) * r_outer, cy + math.sin(a1) * r_outer, z_bot))
        o2 = Vector((cx + math.cos(a1) * r_outer, cy + math.sin(a1) * r_outer, z_top))
        o3 = Vector((cx + math.cos(a0) * r_outer, cy + math.sin(a0) * r_outer, z_top))

        # Inner arc corners (recessed)
        i0 = Vector((cx + math.cos(a0) * r_inner, cy + math.sin(a0) * r_inner, z_bot))
        i1 = Vector((cx + math.cos(a1) * r_inner, cy + math.sin(a1) * r_inner, z_bot))
        i2 = Vector((cx + math.cos(a1) * r_inner, cy + math.sin(a1) * r_inner, z_top))
        i3 = Vector((cx + math.cos(a0) * r_inner, cy + math.sin(a0) * r_inner, z_top))

        # Concave back face (the actual cell hollow)
        back_r = r_inner - cell_depth
        b_mid_bot = Vector((cx + math.cos(a_mid) * back_r, cy + math.sin(a_mid) * back_r, z_bot + (z_top - z_bot) * 0.3))
        b_mid_top = Vector((cx + math.cos(a_mid) * back_r, cy + math.sin(a_mid) * back_r, z_top))

        # Build cell walls
        _safe_face(bm, [o0, o1, o2, o3])                    # outer front face
        _safe_face(bm, [o0, i0, i3, o3])                    # left side
        _safe_face(bm, [o1, o2, i2, i1])                    # right side (reversed for normal)
        _safe_face(bm, [i0, i1, b_mid_bot])                 # inner bottom tri
        _safe_face(bm, [i3, b_mid_top, i2])                 # inner top tri
        _safe_face(bm, [i0, b_mid_bot, b_mid_top, i3])      # inner left
        _safe_face(bm, [i1, i2, b_mid_top, b_mid_bot])      # inner right


def _add_cap(bm, cx, cy, z, radius):
    """Small flat disc at the top of the muqarnas."""
    segs = 8
    verts = []
    for i in range(segs):
        angle = 2 * math.pi * i / segs
        verts.append(bm.verts.new(Vector((
            cx + math.cos(angle) * radius,
            cy + math.sin(angle) * radius,
            z
        ))))
    _safe_face(bm, verts)


def _safe_face(bm, verts):
    """Create a face only if all verts are distinct and count >= 3."""
    if len(verts) < 3:
        return
    try:
        bm.faces.new(verts)
    except Exception:
        pass  # duplicate face or degenerate — skip silently