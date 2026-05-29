"""
courtyard.py
Generates a simple open courtyard in front of the building.

Phase 1: flat ground plane + low perimeter walls on 3 sides.
Phase 2: fountain, trees, arched arcades.
"""

import bpy
import bmesh
from mathutils import Vector

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.material_utils import assign_material


def generate_courtyard(p: dict):
    col = p["collection"]
    depth_building = p["depth"]
    size = p["courtyard_size"]
    w = p["width"]

    # Courtyard sits in front of the building (positive Y from front face)
    y_start = depth_building / 2
    cy = y_start + size / 2

    # Ground slab
    _ground_plane(col, cx=0, cy=cy, w=w, d=size)

    # Low perimeter walls (left, right, far end)
    wall_h = 0.8
    wall_t = 0.3
    _perimeter_walls(col, cx=0, cy=cy, w=w, d=size, wall_h=wall_h, wall_t=wall_t)


def _ground_plane(col, cx, cy, w, d):
    mesh = bpy.data.meshes.new("courtyard_ground_mesh")
    obj = bpy.data.objects.new("Courtyard_Ground", mesh)
    col.objects.link(obj)

    bm = bmesh.new()
    _box(bm, Vector((cx, cy, -0.05)), w, d, 0.1)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    assign_material(obj, "sand")


def _perimeter_walls(col, cx, cy, w, d, wall_h, wall_t):
    half_w = w / 2
    half_d = d / 2

    specs = [
        # name,      center,                              sx,     sy
        ("Wall_L", Vector((cx - half_w - wall_t / 2, cy, wall_h / 2)), wall_t, d),
        ("Wall_R", Vector((cx + half_w + wall_t / 2, cy, wall_h / 2)), wall_t, d),
        ("Wall_F", Vector((cx, cy + half_d + wall_t / 2, wall_h / 2)), w + wall_t * 2, wall_t),
    ]
    for name, center, sx, sy in specs:
        mesh = bpy.data.meshes.new(name + "_mesh")
        obj = bpy.data.objects.new(name, mesh)
        col.objects.link(obj)
        bm = bmesh.new()
        _box(bm, center, sx, sy, wall_h)
        bm.to_mesh(mesh)
        bm.free()
        mesh.update()
        assign_material(obj, "terracotta")


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