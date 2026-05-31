"""
node_groups.py
Reusable Blender shader node group library for Timurid tile patterns.

Creates named NodeGroup datablocks that can be instanced across multiple
materials — one group definition, many material uses.

Node groups provided:
  GirihStarUV     — procedural 8-pointed star pattern from UV coords
  HexTileUV       — hexagonal grid tile pattern
  BrickBandUV     — alternating brick courses with thin mortar
  MarbleVein      — organic marble vein overlay
  AgeGradient     — vertical age/dirt gradient (reusable wear layer)

Each function is idempotent: calling it twice returns the existing group.

Usage inside a material:
    from utils.node_groups import get_girih_star_group
    group = get_girih_star_group()
    node = mat.node_tree.nodes.new("ShaderNodeGroup")
    node.node_tree = group
    # Outputs: Color, Factor
"""

import bpy


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_girih_star_group() -> bpy.types.NodeGroup:
    return _ensure("GirihStarUV", _build_girih_star)


def get_hex_tile_group() -> bpy.types.NodeGroup:
    return _ensure("HexTileUV", _build_hex_tile)


def get_brick_band_group() -> bpy.types.NodeGroup:
    return _ensure("BrickBandUV", _build_brick_band)


def get_marble_vein_group() -> bpy.types.NodeGroup:
    return _ensure("MarbleVein", _build_marble_vein)


def get_age_gradient_group() -> bpy.types.NodeGroup:
    return _ensure("AgeGradient", _build_age_gradient)


def apply_girih_to_material(mat: bpy.types.Material,
                             colour_a=(0.08, 0.28, 0.62, 1.0),
                             colour_b=(0.04, 0.18, 0.45, 1.0)):
    """
    Inject the GirihStar node group into an existing material,
    replacing its base colour with a procedural star pattern.
    """
    if not mat.use_nodes:
        mat.use_nodes = True
    nt   = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    out  = nt.nodes.get("Material Output")
    if bsdf is None or out is None:
        return

    # Skip if already injected
    if any(n.name == "RegGirihGroup" for n in nt.nodes):
        return

    grp  = nt.nodes.new("ShaderNodeGroup")
    grp.node_tree = get_girih_star_group()
    grp.name      = "RegGirihGroup"
    grp.location  = (-300, 200)

    mix = nt.nodes.new("ShaderNodeMixRGB")
    mix.name      = "RegGirihMix"
    mix.location  = (-80, 200)
    mix.blend_type = "MIX"
    mix.inputs["Color1"].default_value = colour_a
    mix.inputs["Color2"].default_value = colour_b

    coord = nt.nodes.new("ShaderNodeTexCoord")
    coord.location = (-520, 200)

    nt.links.new(coord.outputs["UV"],     grp.inputs["UV"])
    nt.links.new(grp.outputs["Factor"],   mix.inputs["Fac"])
    nt.links.new(mix.outputs["Color"],    bsdf.inputs["Base Color"])


# ---------------------------------------------------------------------------
# Internal builders
# ---------------------------------------------------------------------------

def _ensure(name: str, builder) -> bpy.types.NodeGroup:
    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]
    return builder(name)


def _new_group(name: str):
    """Create a new node group with UV input + Color/Factor outputs."""
    grp = bpy.data.node_groups.new(name, "ShaderNodeTree")

    # Inputs
    grp.inputs.new("NodeSocketVector", "UV")
    # Outputs
    grp.outputs.new("NodeSocketColor",  "Color")
    grp.outputs.new("NodeSocketFloat",  "Factor")

    # Group I/O nodes
    inp = grp.nodes.new("NodeGroupInput")
    inp.location = (-400, 0)
    out = grp.nodes.new("NodeGroupOutput")
    out.location = (400, 0)
    return grp, inp, out


def _node(nt, type_name, loc):
    n = nt.nodes.new(type=type_name)
    n.location = loc
    return n


def _link(nt, fn, fs, tn, ts):
    nt.links.new(fn.outputs[fs], tn.inputs[ts])


# ---------------------------------------------------------------------------
# GirihStarUV
# ---------------------------------------------------------------------------

def _build_girih_star(name: str) -> bpy.types.NodeGroup:
    grp, inp, out = _new_group(name)
    nt = grp

    mapping  = _node(nt, "ShaderNodeMapping",     (-200, 100))
    mapping.inputs["Scale"].default_value = (12, 12, 12)

    voronoi  = _node(nt, "ShaderNodeTexVoronoi",  (  0, 100))
    voronoi.voronoi_dimensions = "2D"
    voronoi.inputs["Scale"].default_value   = 1.0
    voronoi.inputs["Randomness"].default_value = 0.0

    wave     = _node(nt, "ShaderNodeTexWave",     (  0, -80))
    wave.wave_type = "BANDS"
    wave.inputs["Scale"].default_value     = 8.0
    wave.inputs["Distortion"].default_value = 1.2

    math_mul = _node(nt, "ShaderNodeMath",        (180,  20))
    math_mul.operation = "MULTIPLY"

    ramp     = _node(nt, "ShaderNodeValToRGB",    (340,  20))
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[1].position = 0.7

    _link(nt, inp,     "UV",       mapping, "Vector")
    _link(nt, mapping, "Vector",   voronoi, "Vector")
    _link(nt, mapping, "Vector",   wave,    "Vector")
    _link(nt, voronoi, "Distance", math_mul, "Value")
    _link(nt, wave,    "Color",    math_mul, "Value")
    _link(nt, math_mul,"Value",    ramp,    "Fac")
    _link(nt, ramp,    "Color",    out,     "Color")
    _link(nt, ramp,    "Alpha",    out,     "Factor")
    return grp


# ---------------------------------------------------------------------------
# HexTileUV
# ---------------------------------------------------------------------------

def _build_hex_tile(name: str) -> bpy.types.NodeGroup:
    grp, inp, out = _new_group(name)
    nt = grp

    mapping = _node(nt, "ShaderNodeMapping", (-200, 0))
    mapping.inputs["Scale"].default_value = (8, 8, 8)

    voronoi = _node(nt, "ShaderNodeTexVoronoi", (0, 0))
    voronoi.feature = "DISTANCE_TO_EDGE"
    voronoi.voronoi_dimensions = "2D"
    voronoi.inputs["Scale"].default_value = 1.0

    math_gt = _node(nt, "ShaderNodeMath", (200, 0))
    math_gt.operation = "GREATER_THAN"
    math_gt.inputs[1].default_value = 0.08

    ramp = _node(nt, "ShaderNodeValToRGB", (360, 0))
    ramp.color_ramp.elements[0].color = (0.08, 0.35, 0.70, 1.0)
    ramp.color_ramp.elements[1].color = (0.02, 0.15, 0.40, 1.0)

    _link(nt, inp,     "UV",       mapping, "Vector")
    _link(nt, mapping, "Vector",   voronoi, "Vector")
    _link(nt, voronoi, "Distance", math_gt, "Value")
    _link(nt, math_gt, "Value",    ramp,    "Fac")
    _link(nt, ramp,    "Color",    out,     "Color")
    _link(nt, math_gt, "Value",    out,     "Factor")
    return grp


# ---------------------------------------------------------------------------
# BrickBandUV
# ---------------------------------------------------------------------------

def _build_brick_band(name: str) -> bpy.types.NodeGroup:
    grp, inp, out = _new_group(name)
    nt = grp

    mapping = _node(nt, "ShaderNodeMapping", (-200, 0))
    mapping.inputs["Scale"].default_value = (6, 10, 1)

    brick = _node(nt, "ShaderNodeTexBrick", (0, 0))
    brick.inputs["Scale"].default_value       = 5.0
    brick.inputs["Mortar Size"].default_value = 0.03
    brick.inputs["Brick Width"].default_value = 0.62
    brick.inputs["Row Height"].default_value  = 0.25
    brick.inputs["Color1"].default_value      = (0.72, 0.38, 0.18, 1.0)
    brick.inputs["Color2"].default_value      = (0.65, 0.32, 0.14, 1.0)
    brick.inputs["Mortar"].default_value      = (0.85, 0.80, 0.72, 1.0)

    _link(nt, inp,    "UV",    mapping, "Vector")
    _link(nt, mapping,"Vector", brick,  "Vector")
    _link(nt, brick,  "Color",  out,    "Color")
    _link(nt, brick,  "Fac",    out,    "Factor")
    return grp


# ---------------------------------------------------------------------------
# MarbleVein
# ---------------------------------------------------------------------------

def _build_marble_vein(name: str) -> bpy.types.NodeGroup:
    grp, inp, out = _new_group(name)
    nt = grp

    mapping = _node(nt, "ShaderNodeMapping", (-200, 0))
    mapping.inputs["Scale"].default_value = (3, 3, 3)

    noise = _node(nt, "ShaderNodeTexNoise", (0, 60))
    noise.inputs["Scale"].default_value   = 5.0
    noise.inputs["Detail"].default_value  = 8.0
    noise.inputs["Roughness"].default_value = 0.7

    wave = _node(nt, "ShaderNodeTexWave", (0, -60))
    wave.wave_type = "BANDS"
    wave.inputs["Scale"].default_value       = 4.0
    wave.inputs["Distortion"].default_value  = 4.0
    wave.inputs["Detail"].default_value      = 6.0

    math_add = _node(nt, "ShaderNodeMath", (180, 0))
    math_add.operation = "ADD"
    math_add.inputs[1].default_value = 0.0

    ramp = _node(nt, "ShaderNodeValToRGB", (340, 0))
    ramp.color_ramp.elements[0].color = (0.92, 0.90, 0.87, 1.0)
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[1].color = (0.70, 0.68, 0.64, 1.0)
    ramp.color_ramp.elements[1].position = 1.0

    _link(nt, inp,     "UV",    mapping,  "Vector")
    _link(nt, mapping, "Vector", noise,   "Vector")
    _link(nt, mapping, "Vector", wave,    "Vector")
    _link(nt, noise,   "Fac",   math_add, "Value")
    _link(nt, wave,    "Color", math_add, "Value")
    _link(nt, math_add,"Value",  ramp,    "Fac")
    _link(nt, ramp,    "Color",  out,     "Color")
    _link(nt, ramp,    "Alpha",  out,     "Factor")
    return grp


# ---------------------------------------------------------------------------
# AgeGradient
# ---------------------------------------------------------------------------

def _build_age_gradient(name: str) -> bpy.types.NodeGroup:
    grp, inp, out = _new_group(name)
    nt = grp

    coord   = _node(nt, "ShaderNodeTexCoord",   (-300, 0))
    mapping = _node(nt, "ShaderNodeMapping",    (-120, 0))
    grad    = _node(nt, "ShaderNodeTexGradient", ( 60, 0))
    grad.gradient_type = "LINEAR"
    noise   = _node(nt, "ShaderNodeTexNoise",   ( 60,-120))
    noise.inputs["Scale"].default_value = 8.0

    math_add = _node(nt, "ShaderNodeMath",      (220, 0))
    math_add.operation = "ADD"
    math_add.inputs[1].default_value = 0.0

    ramp = _node(nt, "ShaderNodeValToRGB",      (380, 0))
    ramp.color_ramp.elements[0].color    = (0.12, 0.10, 0.07, 1.0)
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[1].color    = (0.95, 0.93, 0.90, 1.0)
    ramp.color_ramp.elements[1].position = 0.6

    _link(nt, coord,   "Object",  mapping,  "Vector")
    _link(nt, mapping, "Vector",  grad,     "Vector")
    _link(nt, coord,   "Object",  noise,    "Vector")
    _link(nt, grad,    "Color",   math_add, "Value")
    _link(nt, noise,   "Fac",     math_add, "Value")
    _link(nt, math_add,"Value",   ramp,     "Fac")
    _link(nt, ramp,    "Color",   out,      "Color")
    _link(nt, ramp,    "Alpha",   out,      "Factor")
    return grp
