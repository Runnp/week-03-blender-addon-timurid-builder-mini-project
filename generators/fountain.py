"""
fountain.py
Generates a traditional Central Asian courtyard fountain (hauz).

Structure:
  - Octagonal stone basin (low walls around a water surface)
  - Central column / pedestal
  - Thin jet nozzle on top of column
  - Water surface plane (flat, semi-transparent material in Phase 2)
  - Optional 4 small corner spout jets around the basin rim

Inspired by the marble hauz fountains of Bukhara courtyards
and the Shakhristan pool layouts.
"""

import bpy
import bmesh
import math
from mathutils import Vector

from ..utils.material_utils import get_or_create_material, assign_material


# Colours
STONE_COLOUR  = (0.70, 0.65, 0.55, 1.0)
WATER_COLOUR  = (0.08, 0.28, 0.48, 0.72)   # alpha < 1 for Phase 2 transparency
MARBLE_COLOUR = (0.92, 0.90, 0.87, 1.0)


def generate_fountain(p: dict) -> list:
    """
    Build a fountain and link objects into p["collection"].

    Extra keys consumed:
        fountain_cx      float  — centre X (default: 0)
        fountain_cy      float  — centre Y (default: courtyard centre)
        fountain_radius  float  — outer basin radius (default: courtyard_size * 0.22)
        fountain_col_h   float  — central column height (default: radius * 1.4)
        fountain_spouts  bool   — add 4 rim spouts (default: True)
    """
    col = p["collection"]
    cs  = p.get("courtyard_size", 5.0)
    bd  = p.get("depth", 6.0)

    cx  = p.get("fountain_cx", 0.0)
    cy  = p.get("fountain_cy", bd / 2 + cs / 2)
    r   = p.get("fountain_radius",  cs * 0.22)
    col_h = p.get("fountain_col_h", r * 1.4)
    spouts = p.get("fountain_spouts", True)

    objects = []

    # --- Basin walls (octagonal ring) ---
    basin_wall_h = r * 0.28
    basin_wall_t = r * 0.12
    objects.append(_octagonal_ring(
        col, "Fountain_Basin",
        cx, cy, z=0.0,
        outer_r=r, inner_r=r - basin_wall_t,
        height=basin_wall_h,
        sides=8,
        colour=STONE_COLOUR,
    ))

    # --- Water surface (flat octagonal disc) ---
    objects.append(_octagonal_disc(
        col, "Fountain_Water",
        cx, cy, z=basin_wall_h * 0.85,
        radius=r - basin_wall_t,
        sides=8,
        colour=WATER_COLOUR,
    ))

    # --- Central pedestal ---
    ped_r = r * 0.14
    ped_h = col_h * 0.35
    objects.append(_cylinder_obj(
        col, "Fountain_Pedestal",
        cx, cy, z=0.0,
        radius=ped_r * 1.4, height=ped_h,
        sides=8, colour=MARBLE_COLOUR,
    ))

    # --- Column shaft ---
    objects.append(_cylinder_obj(
        col, "Fountain_Column",
        cx, cy, z=ped_h,
        radius=ped_r, height=col_h,
        sides=12, colour=MARBLE_COLOUR,
    ))

    # --- Capital (wider disc on top of column) ---
    objects.append(_cylinder_obj(
        col, "Fountain_Capital",
        cx, cy, z=ped_h + col_h,
        radius=ped_r * 1.6, height=r * 0.06,
        sides=12, colour=MARBLE_COLOUR,
    ))

    # --- Jet nozzle (thin cylinder) ---
    objects.append(_cylinder_obj(
        col, "Fountain_Nozzle",
        cx, cy, z=ped_h + col_h + r * 0.06,
        radius=ped_r * 0.18, height=r * 0.22,
        sides=8, colour=MARBLE_COLOUR,
    ))

    # --- Optional rim spouts ---
    if spouts:
        for i in range(4):
            angle = math.pi / 4 + i * math.pi / 2
            sx = cx + math.cos(angle) * (r - basin_wall_t * 0.5)
            sy = cy + math.sin(angle) * (r - basin_wall_t * 0.5)
            obj = _cylinder_obj(
                col, f"Fountain_Spout_{i}",
                sx, sy, z=basin_wall_h * 0.6,
                radius=ped_r * 0.14, height=r * 0.15,
                sides=6, colour=STONE_COLOUR,
            )
            objects.append(obj)

    return objects


# ---------------------------------------------------------------------------
# Geometry primitives
# ---------------------------------------------------------------------------

def _octagonal_ring(col, name, cx, cy, z, outer_r, inner_r, height, sides, colour):
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj  = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    bm = bmesh.new()

    outer_verts_b, outer_verts_t = [], []
    inner_verts_b, inner_verts_t = [], []

    for i in range(sides):
        a = 2 * math.pi * i / sides + math.pi / sides
        co, si = math.cos(a), math.sin(a)
        outer_verts_b.append(bm.verts.new(Vector((cx + co * outer_r, cy + si * outer_r, z))))
        outer_verts_t.append(bm.verts.new(Vector((cx + co * outer_r, cy + si * outer_r, z + height))))
        inner_verts_b.append(bm.verts.new(Vector((cx + co * inner_r, cy + si * inner_r, z))))
        inner_verts_t.append(bm.verts.new(Vector((cx + co * inner_r, cy + si * inner_r, z + height))))

    for i in range(sides):
        n = (i + 1) % sides
        # Outer wall
        bm.faces.new([outer_verts_b[i], outer_verts_b[n], outer_verts_t[n], outer_verts_t[i]])
        # Inner wall
        bm.faces.new([inner_verts_b[n], inner_verts_b[i], inner_verts_t[i], inner_verts_t[n]])
        # Top ring
        bm.faces.new([outer_verts_t[i], outer_verts_t[n], inner_verts_t[n], inner_verts_t[i]])
        # Bottom ring
        bm.faces.new([inner_verts_b[i], inner_verts_b[n], outer_verts_b[n], outer_verts_b[i]])

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bm.to_mesh(mesh); bm.free(); mesh.update()
    _assign_colour(obj, name + "_mat", colour)
    return obj


def _octagonal_disc(col, name, cx, cy, z, radius, sides, colour):
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj  = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    bm = bmesh.new()
    verts = []
    for i in range(sides):
        a = 2 * math.pi * i / sides + math.pi / sides
        verts.append(bm.verts.new(Vector((cx + math.cos(a) * radius, cy + math.sin(a) * radius, z))))
    bm.faces.new(verts)
    bm.to_mesh(mesh); bm.free(); mesh.update()
    _assign_colour(obj, name + "_mat", colour)
    return obj


def _cylinder_obj(col, name, cx, cy, z, radius, height, sides, colour):
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj  = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    bm = bmesh.new()
    bot, top = [], []
    for i in range(sides):
        a = 2 * math.pi * i / sides
        x = cx + math.cos(a) * radius
        y = cy + math.sin(a) * radius
        bot.append(bm.verts.new(Vector((x, y, z))))
        top.append(bm.verts.new(Vector((x, y, z + height))))
    for i in range(sides):
        n = (i + 1) % sides
        bm.faces.new([bot[i], bot[n], top[n], top[i]])
    bm.faces.new(bot[::-1])
    bm.faces.new(top)
    bm.to_mesh(mesh); bm.free(); mesh.update()
    _assign_colour(obj, name + "_mat", colour)
    return obj


def _assign_colour(obj, mat_name, rgba):
    mat = get_or_create_material(mat_name, rgba)
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    