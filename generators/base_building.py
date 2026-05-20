"""
base_building.py
Generates the main rectangular building body.

The base is a simple cuboid, but with a recessed upper section
to give a stepped / terrace feel common in Timurid structures.
"""

import bpy
import bmesh
from mathutils import Vector

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.material_utils import assign_wall_material


def generate_base(p: dict) -> bpy.types.Object:
    """
    Create the main building base and link it into p["collection"].

    Geometry:
        Lower block  : full width × depth × lower_height  (60% of total height)
        Upper block  : 90% width × 90% depth × upper_height (40%)
    Both blocks are merged into one object.
    """
    col: bpy.types.Collection = p["collection"]
    w: float = p["width"]
    d: float = p["depth"]
    h: float = p["height"]

    lower_h = h * 0.6
    upper_h = h * 0.4
    inset = 0.05  # 5% inset on each side for upper tier

    mesh = bpy.data.meshes.new("base_building_mesh")
    obj = bpy.data.objects.new("Base_Building", mesh)
    col.objects.link(obj)

    bm = bmesh.new()

    # --- Lower block ---
    _add_cuboid(bm, Vector((0, 0, lower_h / 2)), w, d, lower_h)

    # --- Upper block (slightly inset, sits on top) ---
    _add_cuboid(
        bm,
        Vector((0, 0, lower_h + upper_h / 2)),
        w * (1 - inset * 2),
        d * (1 - inset * 2),
        upper_h,
    )

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    assign_wall_material(obj)
    return obj


def _add_cuboid(
    bm: bmesh.types.BMesh,
    center: Vector,
    sx: float,
    sy: float,
    sz: float,
):
    """Add a cuboid (not unit cube) to bm centred at *center*."""
    half = Vector((sx / 2, sy / 2, sz / 2))
    corners = [
        Vector(( 1,  1, -1)),
        Vector(( 1, -1, -1)),
        Vector((-1, -1, -1)),
        Vector((-1,  1, -1)),
        Vector(( 1,  1,  1)),
        Vector(( 1, -1,  1)),
        Vector((-1, -1,  1)),
        Vector((-1,  1,  1)),
    ]
    verts = [bm.verts.new(center + Vector((c.x * half.x, c.y * half.y, c.z * half.z))) for c in corners]
    bm.faces.new([verts[0], verts[1], verts[2], verts[3]])  # bottom
    bm.faces.new([verts[4], verts[7], verts[6], verts[5]])  # top
    bm.faces.new([verts[0], verts[4], verts[5], verts[1]])  # front
    bm.faces.new([verts[1], verts[5], verts[6], verts[2]])  # right
    bm.faces.new([verts[2], verts[6], verts[7], verts[3]])  # back
    bm.faces.new([verts[3], verts[7], verts[4], verts[0]])  # left