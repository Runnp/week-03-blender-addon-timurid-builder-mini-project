"""
minaret.py
Generates corner minarets as tapered multi-segment cylinders.

Each minaret has:
  - A slightly wider base ring
  - A gently tapering shaft (base_radius → top_radius)
  - A small pointed cap (cone)

Count determines how many minarets and where they are placed
relative to the building corners.
"""

import bpy
import bmesh
import math
from mathutils import Vector

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.material_utils import assign_minaret_material


def generate_minarets(p: dict):
    col = p["collection"]
    w = p["width"]
    d = p["depth"]
    h = p["height"]
    m_h = p["minaret_height"]
    m_r = p["minaret_radius"]
    segs = p["minaret_segments"]
    count = min(p["minaret_count"], 4)

    positions = _corner_positions(count, w, d)

    for idx, (px, py) in enumerate(positions):
        obj = _build_minaret(
            name=f"Minaret_{idx + 1}",
            col=col,
            base_x=px,
            base_y=py,
            base_z=0.0,
            total_height=m_h,
            base_radius=m_r,
            top_radius=m_r * 0.55,
            segs=segs,
        )
        assign_minaret_material(obj)


def _corner_positions(count: int, w: float, d: float) -> list:
    """Return up to 4 (x, y) corner positions for minarets."""
    corners = [
        (-w / 2 - 0.1,  d / 2 + 0.1),
        ( w / 2 + 0.1,  d / 2 + 0.1),
        ( w / 2 + 0.1, -d / 2 - 0.1),
        (-w / 2 - 0.1, -d / 2 - 0.1),
    ]
    return corners[:count]


def _build_minaret(
    name: str,
    col: bpy.types.Collection,
    base_x: float,
    base_y: float,
    base_z: float,
    total_height: float,
    base_radius: float,
    top_radius: float,
    segs: int,
) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)

    bm = bmesh.new()

    shaft_h = total_height * 0.85
    cap_h = total_height * 0.15
    stack = 6  # vertical divisions in shaft

    prev_ring = None
    for si in range(stack + 1):
        t = si / stack
        r = base_radius + (top_radius - base_radius) * t
        z = base_z + shaft_h * t
        ring = _add_ring(bm, base_x, base_y, z, r, segs)
        if prev_ring is not None:
            _connect_rings(bm, prev_ring, ring, segs)
        prev_ring = ring

    # Bottom cap
    bm.faces.new(prev_ring[0:1] + _add_ring(bm, base_x, base_y, base_z, base_radius, segs)[::-1])

    # Pointed cap (cone)
    tip_z = base_z + total_height
    tip = bm.verts.new(Vector((base_x, base_y, tip_z)))
    for si in range(segs):
        ns = (si + 1) % segs
        bm.faces.new([prev_ring[si], prev_ring[ns], tip])

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj


def _add_ring(bm, cx, cy, z, radius, segs):
    verts = []
    for i in range(segs):
        angle = 2 * math.pi * i / segs
        x = cx + math.cos(angle) * radius
        y = cy + math.sin(angle) * radius
        verts.append(bm.verts.new(Vector((x, y, z))))
    return verts


def _connect_rings(bm, r1, r2, segs):
    for i in range(segs):
        ni = (i + 1) % segs
        bm.faces.new([r1[i], r1[ni], r2[ni], r2[i]])