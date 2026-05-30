"""
girih.py
Generates extruded girih tile pattern geometry.

Girih (Persian: گره — "knot") is the geometric strapwork system used on
Timurid and Safavid facades. It consists of five canonical tiles:
  regular decagon, elongated hexagon, bowtie, rhombus, pentagon
arranged into a periodic or quasi-periodic tiling.

Phase 1 approach: a rectangular grid of "stars and crosses" pattern
(the simplest periodic Islamic star pattern, 6-fold). Each cell is
extruded slightly from the wall surface to create real mesh relief.

Parameters:
  gx, gy      — number of grid cells across / up
  cell_size   — size of each repeating unit
  extrude_h   — how far each tile element protrudes (default 0.04 m)
  surface_y   — Y position of the wall face
  x0, z0      — bottom-left corner of the tiled region
  width, height — total region dimensions
"""

import bpy
import bmesh
import math
from mathutils import Vector

from ..utils.material_utils import get_or_create_material


GIRIH_COLOUR = (0.12, 0.42, 0.72, 1.0)   # classic Timurid blue


def generate_girih_panel(p: dict) -> bpy.types.Object:
    """
    Build a girih-patterned relief panel and link it into p["collection"].

    Extra keys:
        girih_x0       float  — left edge X
        girih_z0       float  — bottom edge Z
        girih_width    float  — total panel width
        girih_height   float  — total panel height
        girih_surface_y float — Y position (front face of wall)
        girih_cell     float  — repeat cell size (default 0.45)
        girih_extrude  float  — protrusion depth (default 0.035)
        girih_cols     int    — override column count (0 = auto)
        girih_rows     int    — override row count (0 = auto)
    """
    col    = p["collection"]
    x0     = p.get("girih_x0",       -p["width"] / 2)
    z0     = p.get("girih_z0",        0.0)
    pw     = p.get("girih_width",     p["width"])
    ph     = p.get("girih_height",    p["height"])
    surf_y = p.get("girih_surface_y", p["depth"] / 2)
    cell   = p.get("girih_cell",      0.45)
    ext    = p.get("girih_extrude",   0.035)
    cols   = p.get("girih_cols",      0) or max(1, int(pw / cell))
    rows   = p.get("girih_rows",      0) or max(1, int(ph / cell))

    mesh = bpy.data.meshes.new("GirihPanel_mesh")
    obj  = bpy.data.objects.new("GirihPanel", mesh)
    col.objects.link(obj)

    bm = bmesh.new()

    cell_w = pw / cols
    cell_h = ph / rows

    for ci in range(cols):
        for ri in range(rows):
            cx = x0 + (ci + 0.5) * cell_w
            cz = z0 + (ri + 0.5) * cell_h
            _star_cell(bm, cx, surf_y, cz, cell_w * 0.48, cell_h * 0.48, ext)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.003)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    mat = get_or_create_material("GirihBlue", GIRIH_COLOUR)
    obj.data.materials.append(mat)
    return obj


def generate_girih_dome_band(p: dict) -> bpy.types.Object:
    """
    Build a horizontal band of girih stars around the dome drum.

    Keys:
        dome_size      float  — dome radius (for placement)
        height         float  — building height
        girih_band_rows int   — rows of stars in the band (default 2)
        girih_cell     float  — star cell size
        girih_extrude  float  — protrusion
    """
    col    = p["collection"]
    radius = p["dome_size"] * 0.72 + 0.02   # drum radius + tiny gap
    z_base = p["height"]
    band_h = p.get("dome_size", 2.5) * 0.35  # drum height
    cell   = p.get("girih_cell", 0.45)
    ext    = p.get("girih_extrude", 0.035)
    rows   = p.get("girih_band_rows", 2)

    circumference = 2 * math.pi * radius
    cols = max(4, int(circumference / cell))

    mesh = bpy.data.meshes.new("GirihDomeBand_mesh")
    obj  = bpy.data.objects.new("GirihDomeBand", mesh)
    col.objects.link(obj)

    bm = bmesh.new()

    cell_arc = 2 * math.pi / cols
    cell_h   = band_h / rows

    for ci in range(cols):
        angle = cell_arc * (ci + 0.5)
        for ri in range(rows):
            cz = z_base + (ri + 0.5) * cell_h
            cr = radius + ext
            cx = math.cos(angle) * cr
            cy = math.sin(angle) * cr
            # Project a flat star onto the curved surface by building it
            # in local tangent space then placing it
            _radial_star(bm, cx, cy, cz, angle, cell_arc * radius * 0.46, cell_h * 0.46, ext)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.003)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    mat = get_or_create_material("GirihBlue", GIRIH_COLOUR)
    obj.data.materials.append(mat)
    return obj


# ---------------------------------------------------------------------------
# Cell geometry builders
# ---------------------------------------------------------------------------

def _star_cell(bm, cx, cy, cz, hw, hh, ext):
    """
    8-pointed star relief cell at (cx, cy=wall_y, cz).
    hw/hh = half-width / half-height of bounding box.
    ext   = protrusion in +Y.
    """
    n = 8
    outer_r = min(hw, hh)
    inner_r = outer_r * 0.42

    # Build star polygon (flat back, extruded front)
    back_verts  = []
    front_verts = []

    for i in range(n * 2):
        angle = math.pi / n * i - math.pi / 2
        r = outer_r if i % 2 == 0 else inner_r
        x = cx + math.cos(angle) * r * (hw / outer_r)
        z = cz + math.sin(angle) * r * (hh / outer_r)
        back_verts.append(bm.verts.new(Vector((x, cy,       z))))
        front_verts.append(bm.verts.new(Vector((x, cy + ext, z))))

    # Front face
    try:
        bm.faces.new(front_verts)
    except Exception:
        pass

    # Side walls around the star perimeter
    nv = len(back_verts)
    for i in range(nv):
        ni = (i + 1) % nv
        try:
            bm.faces.new([back_verts[i], back_verts[ni],
                          front_verts[ni], front_verts[i]])
        except Exception:
            pass


def _radial_star(bm, cx, cy, cz, angle, half_arc, half_h, ext):
    """Star cell oriented tangentially on a curved surface."""
    n = 8
    outer_r = min(half_arc, half_h)
    inner_r = outer_r * 0.42
    tang = angle + math.pi / 2   # tangent direction

    back_verts  = []
    front_verts = []

    for i in range(n * 2):
        a = math.pi / n * i - math.pi / 2
        r = outer_r if i % 2 == 0 else inner_r
        # local tangent + z
        dx = math.cos(a) * r * math.cos(tang)
        dy = math.cos(a) * r * math.sin(tang)
        dz = math.sin(a) * half_h / outer_r * r

        back_verts.append(bm.verts.new(Vector((cx + dx,        cy + dy,        cz + dz))))
        front_verts.append(bm.verts.new(Vector((cx + dx + math.cos(angle) * ext,
                                                cy + dy + math.sin(angle) * ext,
                                                cz + dz))))
    try:
        bm.faces.new(front_verts)
    except Exception:
        pass
    nv = len(back_verts)
    for i in range(nv):
        ni = (i + 1) % nv
        try:
            bm.faces.new([back_verts[i], back_verts[ni],
                          front_verts[ni], front_verts[i]])
        except Exception:
            pass
