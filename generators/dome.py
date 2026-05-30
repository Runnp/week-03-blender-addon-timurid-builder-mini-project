"""
dome.py
Generates the signature blue dome placed on top of the building.

Uses a truncated UV-sphere approach:
  1. Create a full UV sphere
  2. Delete the bottom hemisphere
  3. Add a drum cylinder beneath it (the neck / tambour)
"""

import bpy
import bmesh
import math
from mathutils import Vector

from ..utils.material_utils import assign_dome_material


def generate_dome(p: dict) -> bpy.types.Object:
    """
    Create a dome object and link it into p["collection"].

    Placement: centred above the building, resting on a short drum.
    """
    col: bpy.types.Collection = p["collection"]
    w: float = p["width"]
    h: float = p["height"]           # total building height
    radius: float = p["dome_size"]
    segs: int = p["dome_segments"]
    rings: int = max(6, segs // 2)

    # Top of the building (upper block top surface)
    building_top_z = h

    drum_height = radius * 0.35
    drum_radius = radius * 0.72

    mesh = bpy.data.meshes.new("dome_mesh")
    obj = bpy.data.objects.new("Dome", mesh)
    col.objects.link(obj)

    bm = bmesh.new()

    # --- Drum (tambour) ---
    _add_cylinder(bm, segs, drum_radius, drum_height, z_base=building_top_z)

    # --- Hemisphere ---
    dome_base_z = building_top_z + drum_height
    _add_hemisphere(bm, segs, rings, radius, z_base=dome_base_z)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    assign_dome_material(obj)
    return obj


def _add_cylinder(
    bm: bmesh.types.BMesh,
    segs: int,
    radius: float,
    height: float,
    z_base: float,
):
    bottom_verts = []
    top_verts = []
    for i in range(segs):
        angle = 2 * math.pi * i / segs
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius
        bottom_verts.append(bm.verts.new(Vector((x, y, z_base))))
        top_verts.append(bm.verts.new(Vector((x, y, z_base + height))))

    # Side faces
    for i in range(segs):
        ni = (i + 1) % segs
        bm.faces.new([bottom_verts[i], bottom_verts[ni], top_verts[ni], top_verts[i]])

    # Cap faces
    bm.faces.new(bottom_verts[::-1])
    bm.faces.new(top_verts)


def _add_hemisphere(
    bm: bmesh.types.BMesh,
    segs_h: int,  # horizontal (longitude)
    rings: int,   # vertical (latitude), equator → pole
    radius: float,
    z_base: float,
):
    """Build a hemisphere as stacked rings from equator to pole."""
    ring_verts = []

    for ring_i in range(rings + 1):
        lat = math.pi / 2 * ring_i / rings  # 0 = equator, π/2 = north pole
        r = math.cos(lat) * radius
        z = math.sin(lat) * radius + z_base

        if ring_i == rings:
            # Pole: single vertex
            ring_verts.append([bm.verts.new(Vector((0, 0, z)))])
        else:
            row = []
            for seg_i in range(segs_h):
                angle = 2 * math.pi * seg_i / segs_h
                x = math.cos(angle) * r
                y = math.sin(angle) * r
                row.append(bm.verts.new(Vector((x, y, z))))
            ring_verts.append(row)

    # Quad strips between rings
    for ri in range(rings - 1):
        curr = ring_verts[ri]
        nxt = ring_verts[ri + 1]
        for si in range(segs_h):
            ns = (si + 1) % segs_h
            bm.faces.new([curr[si], curr[ns], nxt[ns], nxt[si]])

    # Triangle fan at pole
    last_ring = ring_verts[rings - 1]
    pole = ring_verts[rings][0]
    for si in range(segs_h):
        ns = (si + 1) % segs_h
        bm.faces.new([last_ring[si], last_ring[ns], pole])
