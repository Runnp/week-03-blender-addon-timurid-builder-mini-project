"""
arcade.py
Generates a wall arcade — a series of pointed blind niches running along
the side walls of the building.

Timurid facades are rarely left as bare brick. The standard treatment is
a repeating bay of shallow pointed arches (sometimes called "engaged arches"
or "blind arcade") that divide the wall into vertical panels, reducing
visual mass and providing depth through shadow.

Structure of each arcade bay:
  1. A thin pilaster (vertical rib) separating each niche
  2. A pointed arch head above the niche opening
  3. A shallow recessed back panel
  4. Optional: small roundel boss at the arch apex

The arcade wraps both side walls (±X faces) and optionally the back wall.

Parameters (from p dict):
  arcade_bays       int    — number of bays per wall (default: auto from width/2)
  arcade_height     float  — total niche height including arch (default: wall_h * 0.70)
  arcade_depth      float  — recess depth from wall face (default: 0.10)
  arcade_sides      bool   — apply to ±X side walls (default: True)
  arcade_back       bool   — apply to -Y back wall (default: False)
  arcade_roundel    bool   — add boss roundel at arch apex (default: True)
"""

import bpy
import bmesh
import math
from mathutils import Vector

from ..utils.material_utils import assign_wall_material, get_or_create_material


PILASTER_COLOUR = (0.65, 0.55, 0.40, 1.0)
NICHE_COLOUR    = (0.55, 0.48, 0.36, 1.0)   # slightly darker for shadow effect
ROUNDEL_COLOUR  = (0.88, 0.80, 0.60, 1.0)


def generate_arcade(p: dict) -> list:
    """
    Build blind arcade niches on the building walls and link into p["collection"].
    Returns list of created objects.
    """
    col = p["collection"]
    w   = p["width"]
    d   = p["depth"]
    h   = p["height"]

    bays       = p.get("arcade_bays",    max(2, int(d / 1.6)))
    arc_h      = p.get("arcade_height",  h * 0.68)
    arc_depth  = p.get("arcade_depth",   0.10)
    do_sides   = p.get("arcade_sides",   True)
    do_back    = p.get("arcade_back",    False)
    do_roundel = p.get("arcade_roundel", True)

    objects = []

    if do_sides:
        # Left wall (−X face, facing −X)
        objects += _wall_arcade(col, "Arcade_L",
                                wall_cx=-w / 2 - arc_depth / 2,
                                wall_span=d, span_axis="y",
                                face_sign=-1,
                                bays=bays, arc_h=arc_h,
                                arc_depth=arc_depth,
                                do_roundel=do_roundel)
        # Right wall (+X face, facing +X)
        objects += _wall_arcade(col, "Arcade_R",
                                wall_cx= w / 2 + arc_depth / 2,
                                wall_span=d, span_axis="y",
                                face_sign=+1,
                                bays=bays, arc_h=arc_h,
                                arc_depth=arc_depth,
                                do_roundel=do_roundel)

    if do_back:
        back_bays = max(2, int(w / 1.6))
        objects += _wall_arcade(col, "Arcade_B",
                                wall_cx=-d / 2 - arc_depth / 2,
                                wall_span=w, span_axis="x",
                                face_sign=-1,
                                bays=back_bays, arc_h=arc_h,
                                arc_depth=arc_depth,
                                do_roundel=do_roundel,
                                is_back=True)
    return objects


# ---------------------------------------------------------------------------
# Per-wall arcade
# ---------------------------------------------------------------------------

def _wall_arcade(col, prefix, wall_cx, wall_span, span_axis,
                 face_sign, bays, arc_h, arc_depth, do_roundel,
                 is_back=False):
    objects = []
    bay_w = wall_span / bays
    pilaster_w = bay_w * 0.18
    niche_w    = bay_w - pilaster_w
    niche_leg  = arc_h * 0.55
    arch_r     = niche_w / 2

    for i in range(bays):
        # Bay centre along the span axis
        span_pos = -wall_span / 2 + bay_w * (i + 0.5)

        cx, cy = _wall_pos(wall_cx, span_pos, span_axis, is_back)

        # Pilaster (leading edge of bay)
        pil_span = -wall_span / 2 + bay_w * i
        px, py = _wall_pos(wall_cx, pil_span, span_axis, is_back)
        pil = _box_obj(col, f"{prefix}_Pil_{i}",
                       px, py,
                       arc_h / 2,
                       pilaster_w if span_axis == "y" else arc_depth * 1.2,
                       arc_depth * 1.2 if span_axis == "y" else pilaster_w,
                       arc_h,
                       face_sign, span_axis)
        assign_wall_material(pil)
        objects.append(pil)

        # Recessed niche back panel (flat box slightly inset)
        niche = _box_obj(col, f"{prefix}_Niche_{i}",
                         cx, cy,
                         arc_h * 0.35,
                         niche_w if span_axis == "y" else arc_depth * 0.5,
                         arc_depth * 0.5 if span_axis == "y" else niche_w,
                         niche_leg,
                         face_sign, span_axis,
                         inset=arc_depth * 0.6)
        mat = get_or_create_material("Arcade_Niche", NICHE_COLOUR)
        niche.data.materials.append(mat)
        objects.append(niche)

        # Pointed arch over the niche
        arch = _pointed_arch_obj(col, f"{prefix}_Arch_{i}",
                                 cx, cy,
                                 niche_leg, arch_r,
                                 arc_depth * 0.55,
                                 face_sign, span_axis)
        assign_wall_material(arch)
        objects.append(arch)

        # Optional roundel boss at apex
        if do_roundel:
            apex_z = niche_leg + arch_r * 1.25
            rx, ry = _wall_pos(wall_cx + face_sign * arc_depth * 0.4,
                               span_pos, span_axis, is_back)
            rnd = _roundel_obj(col, f"{prefix}_Roundel_{i}",
                               rx, ry, apex_z,
                               arch_r * 0.22,
                               face_sign, span_axis)
            mat_r = get_or_create_material("Arcade_Roundel", ROUNDEL_COLOUR)
            rnd.data.materials.append(mat_r)
            objects.append(rnd)

    return objects


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def _wall_pos(wall_cx, span_pos, span_axis, is_back):
    if span_axis == "y":
        return wall_cx, span_pos
    else:
        return span_pos, wall_cx


def _box_obj(col, name, cx, cy, cz, sx, sy, sz, face_sign, span_axis, inset=0.0):
    """Box with optional inset (positive = pulled back from wall face)."""
    if span_axis == "y":
        cx_adj = cx - face_sign * inset
    else:
        cy_adj = cy - face_sign * inset
        cx, cy = cx, cy_adj

    mesh = bpy.data.meshes.new(name + "_mesh")
    obj  = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    bm = bmesh.new()
    _bm_box(bm, Vector((cx, cy, cz)), sx, sy, sz)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj


def _pointed_arch_obj(col, name, cx, cy, base_z, radius, depth, face_sign, span_axis):
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj  = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    bm = bmesh.new()

    segs = 10
    front_v, back_v = [], []

    for i in range(segs + 1):
        t = i / segs
        if t <= 0.5:
            angle = math.pi * t
            arc_cx = cx - radius * 0.5 if span_axis == "y" else cx
            arc_cy = cy if span_axis == "y" else cy - radius * 0.5
            if span_axis == "y":
                x = arc_cx + math.cos(math.pi - angle) * radius
                y = cy
            else:
                x = cx
                y = arc_cy + math.cos(math.pi - angle) * radius
            z = base_z + math.sin(angle) * radius
        else:
            angle = math.pi * (t - 0.5)
            arc_cx = cx + radius * 0.5 if span_axis == "y" else cx
            arc_cy = cy if span_axis == "y" else cy + radius * 0.5
            if span_axis == "y":
                x = arc_cx + math.cos(angle) * radius
                y = cy
            else:
                x = cx
                y = arc_cy + math.cos(angle) * radius
            z = base_z + math.sin(math.pi - angle + math.pi / 2) * radius * 0.8 + radius * 0.2

        if span_axis == "y":
            front_v.append(bm.verts.new(Vector((x, y + face_sign * depth,       z))))
            back_v.append( bm.verts.new(Vector((x, y + face_sign * depth * 0.2, z))))
        else:
            front_v.append(bm.verts.new(Vector((x, y + face_sign * depth,       z))))
            back_v.append( bm.verts.new(Vector((x, y + face_sign * depth * 0.2, z))))

    for i in range(segs):
        try:
            bm.faces.new([front_v[i], front_v[i+1], back_v[i+1], back_v[i]])
        except Exception:
            pass

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj


def _roundel_obj(col, name, cx, cy, cz, radius, face_sign, span_axis):
    """Small disc boss."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj  = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    bm = bmesh.new()
    segs = 10
    verts = []
    for i in range(segs):
        a = 2 * math.pi * i / segs
        if span_axis == "y":
            verts.append(bm.verts.new(Vector((cx + math.cos(a) * radius,
                                              cy + face_sign * radius * 0.2,
                                              cz + math.sin(a) * radius))))
        else:
            verts.append(bm.verts.new(Vector((cx + math.cos(a) * radius * 0.2,
                                              cy + math.sin(a) * radius,
                                              cz + radius * 0.2))))
    try:
        bm.faces.new(verts)
    except Exception:
        pass
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj


def _bm_box(bm, center, sx, sy, sz):
    corners = [
        ( 1,  1, -1), ( 1, -1, -1), (-1, -1, -1), (-1,  1, -1),
        ( 1,  1,  1), ( 1, -1,  1), (-1, -1,  1), (-1,  1,  1),
    ]
    verts = [bm.verts.new(center + Vector((c[0]*sx/2, c[1]*sy/2, c[2]*sz/2)))
             for c in corners]
    bm.faces.new([verts[0], verts[1], verts[2], verts[3]])
    bm.faces.new([verts[4], verts[7], verts[6], verts[5]])
    bm.faces.new([verts[0], verts[4], verts[5], verts[1]])
    bm.faces.new([verts[1], verts[5], verts[6], verts[2]])
    bm.faces.new([verts[2], verts[6], verts[7], verts[3]])
    bm.faces.new([verts[3], verts[7], verts[4], verts[0]])
