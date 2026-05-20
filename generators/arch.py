"""
arch.py
Generates pointed iwan-style arch openings on the front face of the building.

Each arch is built as:
  - Two vertical leg columns (rectangular pillars)
  - A semi-circular / pointed arch bridge between them
  - A recessed back plane

The arch opening is purely additive (no boolean subtraction for Phase 1).
In Phase 2 we can use bmesh boolean to actually cut into the wall.
"""

import bpy
import bmesh
import math
from mathutils import Vector

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.material_utils import assign_wall_material, get_or_create_material


def generate_arches(p: dict):
    col = p["collection"]
    w = p["width"]
    h = p["height"]
    count = p["arch_count"]
    a_h = p["arch_height"]
    a_w = p["arch_width"]

    front_y = p["depth"] / 2  # front face Y position

    # Spread arches evenly across the facade
    spacing = w / (count + 1)
    for i in range(count):
        cx = -w / 2 + spacing * (i + 1)
        _build_arch(
            name=f"Arch_{i + 1}",
            col=col,
            cx=cx,
            front_y=front_y,
            arch_width=a_w,
            arch_height=a_h,
            depth=0.25,  # how far the arch protrudes from the wall
        )


def _build_arch(
    name: str,
    col: bpy.types.Collection,
    cx: float,
    front_y: float,
    arch_width: float,
    arch_height: float,
    depth: float,
):
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)

    bm = bmesh.new()

    leg_w = arch_width * 0.18
    leg_h = arch_height * 0.65
    half_span = arch_width / 2

    # Left leg
    _box(bm,
         Vector((cx - half_span + leg_w / 2, front_y + depth / 2, leg_h / 2)),
         leg_w, depth, leg_h)

    # Right leg
    _box(bm,
         Vector((cx + half_span - leg_w / 2, front_y + depth / 2, leg_h / 2)),
         leg_w, depth, leg_h)

    # Pointed arch crown
    arch_base_z = leg_h
    inner_r = (arch_width - leg_w * 2) / 2
    segs = 14
    _pointed_arch_strip(bm, cx, front_y, arch_base_z, inner_r, depth, segs)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    assign_wall_material(obj)


def _box(bm, center, sx, sy, sz):
    corners = [
        Vector((1, 1, -1)), Vector((1, -1, -1)), Vector((-1, -1, -1)), Vector((-1, 1, -1)),
        Vector((1, 1,  1)), Vector((1, -1,  1)), Vector((-1, -1,  1)), Vector((-1, 1,  1)),
    ]
    verts = [bm.verts.new(center + Vector((c.x * sx / 2, c.y * sy / 2, c.z * sz / 2))) for c in corners]
    bm.faces.new([verts[0], verts[1], verts[2], verts[3]])
    bm.faces.new([verts[4], verts[7], verts[6], verts[5]])
    bm.faces.new([verts[0], verts[4], verts[5], verts[1]])
    bm.faces.new([verts[1], verts[5], verts[6], verts[2]])
    bm.faces.new([verts[2], verts[6], verts[7], verts[3]])
    bm.faces.new([verts[3], verts[7], verts[4], verts[0]])


def _pointed_arch_strip(bm, cx, front_y, base_z, radius, depth, segs):
    """
    Build a thin strip following the inner edge of a pointed (ogival) arch.
    The arch is approximated as two circular arcs meeting at the apex.
    """
    front_verts = []
    back_verts = []

    for i in range(segs + 1):
        t = i / segs
        # Two-centred pointed arch: left arc then right arc
        if t <= 0.5:
            angle = math.pi * t  # 0 → π/2 on left circle
            arc_cx = cx - radius * 0.5
            x = arc_cx + math.cos(math.pi - angle) * radius
            z = base_z + math.sin(angle) * radius
        else:
            angle = math.pi * (t - 0.5)
            arc_cx = cx + radius * 0.5
            x = arc_cx + math.cos(angle) * radius
            z = base_z + math.sin(math.pi - angle + math.pi / 2) * radius * 0.8 + radius * 0.2

        front_verts.append(bm.verts.new(Vector((x, front_y, z))))
        back_verts.append(bm.verts.new(Vector((x, front_y - depth, z))))

    for i in range(segs):
        bm.faces.new([front_verts[i], front_verts[i + 1], back_verts[i + 1], back_verts[i]])

    # End caps
    for i in range(segs):
        pass  # kept open for Phase 2 wall boolean