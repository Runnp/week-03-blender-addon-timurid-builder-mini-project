"""
balcony.py
Generates a serefe (şerefe) — the projecting balcony gallery that rings
the minaret shaft at roughly 2/3 height.

In traditional minarets (Kalon, Sultan Ahmed, etc.) the muezzin would
stand on the serefe to call the adhan. Architecturally it provides a
strong horizontal break in the vertical shaft and is often decorated
with a muqarnas corbel bracket beneath the floor slab.

Structure of each serefe:
  1. Corbel bracket ring  — series of small stepped projections just below
  2. Balcony floor slab   — thin annular disc wider than the shaft
  3. Parapet ring         — low wall around the slab perimeter
  4. Return taper         — shaft continues above narrowed back to minaret_radius
"""

import bpy
import bmesh
import math
from mathutils import Vector

from ..utils.material_utils import assign_material, get_or_create_material

BALCONY_COLOUR = (0.82, 0.76, 0.62, 1.0)   # warm sandstone


def generate_balconies(p: dict):
    """
    Add a serefe ring to each minaret already described in p.

    Requires same keys as minaret generator:
        width, depth, minaret_count, minaret_height, minaret_radius,
        height (building wall height), collection.

    balcony_height_frac : float  — fraction of minaret_height for placement (default 0.65)
    balcony_overhang    : float  — how far the slab extends beyond shaft radius (default 0.3 m)
    balcony_parapet_h   : float  — height of the low parapet wall (default 0.15 m)
    balcony_corbel_n    : int    — number of corbel notches (default 12)
    """
    col     = p["collection"]
    w       = p["width"]
    d       = p["depth"]
    count   = min(p["minaret_count"], 4)
    m_h     = p["minaret_height"]
    m_r     = p["minaret_radius"]
    segs    = p.get("minaret_segments", 12)

    frac      = p.get("balcony_height_frac", 0.65)
    overhang  = p.get("balcony_overhang",    m_r * 0.75)
    parapet_h = p.get("balcony_parapet_h",   0.15)
    corbel_n  = p.get("balcony_corbel_n",    12)

    positions = _corner_positions(count, w, d)

    for idx, (px, py) in enumerate(positions):
        base_z = m_h * frac
        _build_serefe(
            col, f"Serefe_{idx + 1}",
            px, py, base_z,
            shaft_r=m_r * (1.0 - frac * 0.45),   # taper to match shaft at this height
            overhang=overhang,
            parapet_h=parapet_h,
            corbel_n=corbel_n,
            segs=segs,
        )


def _corner_positions(count, w, d):
    corners = [
        (-w / 2 - 0.1,  d / 2 + 0.1),
        ( w / 2 + 0.1,  d / 2 + 0.1),
        ( w / 2 + 0.1, -d / 2 - 0.1),
        (-w / 2 - 0.1, -d / 2 - 0.1),
    ]
    return corners[:count]


def _build_serefe(col, name, cx, cy, base_z,
                  shaft_r, overhang, parapet_h, corbel_n, segs):
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj  = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)

    bm = bmesh.new()

    slab_r   = shaft_r + overhang
    slab_t   = 0.08      # slab thickness
    corbel_h = 0.18      # total corbel bracket height

    # --- Corbel brackets (stepped ring of small blocks) ---
    for i in range(corbel_n):
        angle  = 2 * math.pi * i / corbel_n
        a_mid  = angle + math.pi / corbel_n
        # Two stepped levels
        for step, (sr, sh, sy_off) in enumerate([
            (shaft_r + overhang * 0.35, corbel_h * 0.55, 0),
            (shaft_r + overhang * 0.70, corbel_h * 0.30, corbel_h * 0.55),
        ]):
            bw = 2 * math.pi * sr / corbel_n * 0.72   # arc width
            _bm_box_polar(bm, cx, cy, base_z - corbel_h + sy_off,
                          angle, sr, bw, sh, depth=0.10)

    # --- Floor slab (annular ring) ---
    _annular_ring(bm, cx, cy, base_z, shaft_r * 0.9, slab_r, slab_t, segs)

    # --- Parapet wall (ring on slab edge) ---
    _ring_wall(bm, cx, cy, base_z + slab_t, slab_r - 0.04, 0.06, parapet_h, segs)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    mat = get_or_create_material("Serefe_Stone", BALCONY_COLOUR)
    obj.data.materials.append(mat)
    return obj


# ---------------------------------------------------------------------------
# Geometry primitives
# ---------------------------------------------------------------------------

def _bm_box_polar(bm, cx, cy, z, angle, radius, width, height, depth):
    """Small box placed radially, tangent-aligned."""
    tang = angle + math.pi / 2
    hw, hd = width / 2, depth / 2
    corners2d = [
        (-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd)
    ]
    verts_b, verts_t = [], []
    for u, v in corners2d:
        x = cx + math.cos(angle) * radius + u * math.cos(tang) + v * math.cos(angle)
        y = cy + math.sin(angle) * radius + u * math.sin(tang) + v * math.sin(angle)
        verts_b.append(bm.verts.new(Vector((x, y, z))))
        verts_t.append(bm.verts.new(Vector((x, y, z + height))))
    try:
        bm.faces.new(verts_b[::-1])
        bm.faces.new(verts_t)
        for i in range(4):
            ni = (i + 1) % 4
            bm.faces.new([verts_b[i], verts_b[ni], verts_t[ni], verts_t[i]])
    except Exception:
        pass


def _annular_ring(bm, cx, cy, z, inner_r, outer_r, thickness, segs):
    ivb, ivt, ovb, ovt = [], [], [], []
    for i in range(segs):
        a = 2 * math.pi * i / segs
        co, si = math.cos(a), math.sin(a)
        ivb.append(bm.verts.new(Vector((cx + co * inner_r, cy + si * inner_r, z))))
        ivt.append(bm.verts.new(Vector((cx + co * inner_r, cy + si * inner_r, z + thickness))))
        ovb.append(bm.verts.new(Vector((cx + co * outer_r, cy + si * outer_r, z))))
        ovt.append(bm.verts.new(Vector((cx + co * outer_r, cy + si * outer_r, z + thickness))))
    for i in range(segs):
        n = (i + 1) % segs
        try:
            bm.faces.new([ovb[i], ovb[n], ivb[n], ivb[i]])   # bottom
            bm.faces.new([ivt[i], ivt[n], ovt[n], ovt[i]])   # top
            bm.faces.new([ovb[i], ovt[i], ovt[n], ovb[n]])   # outer wall
            bm.faces.new([ivb[n], ivt[n], ivt[i], ivb[i]])   # inner wall
        except Exception:
            pass


def _ring_wall(bm, cx, cy, z, radius, thickness, height, segs):
    outer_r = radius + thickness / 2
    inner_r = radius - thickness / 2
    _annular_ring(bm, cx, cy, z, inner_r, outer_r, height, segs)
