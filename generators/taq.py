"""
taq.py
Raised diamond (lozenge) tile pattern on arch spandrel zones.

A taq (طاق) is the zone between the arch head and the rectangular
frame of the pishtaq.  Traditionally filled with small raised tile
lozenges in alternating colours.

Geometry: grid of thin extruded diamond shapes placed on the spandrel
face (front Y surface, between arch_height and pishtaq_height).
"""

import bpy
import bmesh
import math
from mathutils import Vector

DIAMOND_A = (0.10, 0.38, 0.68, 1.0)   # blue tile
DIAMOND_B = (0.85, 0.68, 0.12, 1.0)   # gold tile


def generate_taq(p: dict) -> list:
    """
    Place raised diamond tiles on the spandrel above each arch.

    Consumes from p:
        arch_count, arch_width, arch_height
        pishtaq_height  (top of spandrel zone — falls back to building_height)
        depth           (for front face Y)
        taq_cell        float  cell size  (default 0.20)
        taq_extrude     float  protrusion (default 0.025)
    """
    col       = p["collection"]
    front_y   = p["depth"] / 2
    a_count   = p["arch_count"]
    a_w       = p["arch_width"]
    a_h       = p["arch_height"]
    top_z     = p.get("pishtaq_height", p["height"])
    cell      = p.get("taq_cell",    0.20)
    ext       = p.get("taq_extrude", 0.025)
    span_h    = top_z - a_h
    total_w   = p["width"]
    spacing   = total_w / (a_count + 1)
    objects   = []

    for i in range(a_count):
        cx = -total_w / 2 + spacing * (i + 1)
        # Left spandrel zone
        objects += _diamond_grid(col, f"Taq_L_{i}",
            x0=cx - a_w / 2 * 1.6, x1=cx - a_w / 2,
            z0=a_h, z1=top_z,
            y=front_y, cell=cell, ext=ext, alt=False)
        # Right spandrel zone
        objects += _diamond_grid(col, f"Taq_R_{i}",
            x0=cx + a_w / 2, x1=cx + a_w / 2 * 1.6,
            z0=a_h, z1=top_z,
            y=front_y, cell=cell, ext=ext, alt=True)

    return objects


def _diamond_grid(col, prefix, x0, x1, z0, z1, y, cell, ext, alt):
    objs  = []
    cols  = max(1, int((x1 - x0) / cell))
    rows  = max(1, int((z1 - z0) / cell))
    cw    = (x1 - x0) / cols
    ch    = (z1 - z0) / rows

    for ci in range(cols):
        for ri in range(rows):
            cx = x0 + (ci + 0.5) * cw
            cz = z0 + (ri + 0.5) * ch
            colour = DIAMOND_B if ((ci + ri + int(alt)) % 2) else DIAMOND_A
            obj = _diamond_obj(col, f"{prefix}_{ci}_{ri}", cx, y, cz,
                               cw * 0.44, ch * 0.44, ext, colour)
            objs.append(obj)
    return objs


def _diamond_obj(col, name, cx, cy, cz, hw, hh, ext, colour):
    mesh = bpy.data.meshes.new(name + "_m")
    obj  = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    bm   = bmesh.new()

    # Diamond = 4 corner points rotated 45°
    tips = [
        Vector((cx,        cy + ext, cz + hh)),   # top
        Vector((cx + hw,   cy + ext, cz)),         # right
        Vector((cx,        cy + ext, cz - hh)),    # bottom
        Vector((cx - hw,   cy + ext, cz)),         # left
    ]
    backs = [
        Vector((cx,        cy,       cz + hh)),
        Vector((cx + hw,   cy,       cz)),
        Vector((cx,        cy,       cz - hh)),
        Vector((cx - hw,   cy,       cz)),
    ]
    fv = [bm.verts.new(v) for v in tips]
    bv = [bm.verts.new(v) for v in backs]

    try: bm.faces.new(fv)
    except Exception: pass
    for i in range(4):
        n = (i + 1) % 4
        try: bm.faces.new([fv[i], fv[n], bv[n], bv[i]])
        except Exception: pass

    bm.to_mesh(mesh); bm.free(); mesh.update()
    mat = get_or_create_material(f"Taq_{colour[0]:.2f}", colour)
    obj.data.materials.append(mat)
    return obj
