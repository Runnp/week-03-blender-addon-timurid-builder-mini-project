"""
tile_material.py
Builds procedural Timurid-style tile materials using Blender's shader node system.

Creates two material types:
  1. dome_tile   — deep blue / turquoise girih tile pattern
  2. facade_tile — terracotta + cream geometric repeat

Both are fully procedural (no image textures required).
Based on Voronoi + Wave texture combos that approximate geometric Islamic patterns.

Usage:
    from utils.tile_material import make_dome_tile_material, make_facade_tile_material
    mat = make_dome_tile_material()
    obj.data.materials.append(mat)
"""

import bpy


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def make_dome_tile_material(name: str = "DomeTile_Timurid") -> bpy.types.Material:
    """
    Deep cobalt blue dome with turquoise girih lattice overlay.
    Approximates the Bibi-Khanym / Gur-e-Amir glazed tile look.
    """
    mat = _get_or_new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = _node(nt, "ShaderNodeOutputMaterial", (700, 0))
    bsdf = _node(nt, "ShaderNodeBsdfPrincipled", (400, 0))
    mix = _node(nt, "ShaderNodeMixRGB", (150, 0))
    voronoi = _node(nt, "ShaderNodeTexVoronoi", (-250, 100))
    wave = _node(nt, "ShaderNodeTexWave", (-250, -150))
    coord = _node(nt, "ShaderNodeTexCoord", (-600, 0))
    mapping = _node(nt, "ShaderNodeMapping", (-420, 0))

    # Colours
    mix.blend_type = "MIX"
    mix.inputs["Color1"].default_value = (0.04, 0.22, 0.58, 1.0)   # deep cobalt
    mix.inputs["Color2"].default_value = (0.05, 0.62, 0.72, 1.0)   # turquoise

    # Voronoi for cell boundaries (girih grid)
    voronoi.voronoi_dimensions = "3D"
    voronoi.inputs["Scale"].default_value = 14.0
    voronoi.inputs["Randomness"].default_value = 0.0  # regular grid

    # Wave for star-polygon overlay
    wave.wave_type = "BANDS"
    wave.inputs["Scale"].default_value = 20.0
    wave.inputs["Distortion"].default_value = 2.5
    wave.inputs["Detail"].default_value = 6.0
    wave.inputs["Detail Scale"].default_value = 2.0

    # Combine wave + voronoi into mix factor
    math_add = _node(nt, "ShaderNodeMath", (-50, 150))
    math_add.operation = "MULTIPLY"
    math_add.inputs[1].default_value = 1.0

    # Material roughness / metallic
    bsdf.inputs["Roughness"].default_value = 0.15
    bsdf.inputs["Specular IOR Level"].default_value = 0.8

    # Links
    _link(nt, coord, "UV", mapping, "Vector")
    _link(nt, mapping, "Vector", voronoi, "Vector")
    _link(nt, mapping, "Vector", wave, "Vector")
    _link(nt, voronoi, "Distance", math_add, "Value")
    _link(nt, wave, "Color", math_add, "Value")  # second input
    _link(nt, math_add, "Value", mix, "Fac")
    _link(nt, mix, "Color", bsdf, "Base Color")
    _link(nt, bsdf, "BSDF", out, "Surface")

    return mat


def make_facade_tile_material(name: str = "FacadeTile_Timurid") -> bpy.types.Material:
    """
    Warm terracotta base with cream/white geometric repeat.
    Approximates Bukharan brick + plaster decorative banding.
    """
    mat = _get_or_new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = _node(nt, "ShaderNodeOutputMaterial", (700, 0))
    bsdf = _node(nt, "ShaderNodeBsdfPrincipled", (420, 0))
    mix = _node(nt, "ShaderNodeMixRGB", (180, 0))
    brick = _node(nt, "ShaderNodeTexBrick", (-150, 100))
    wave = _node(nt, "ShaderNodeTexWave", (-150, -200))
    coord = _node(nt, "ShaderNodeTexCoord", (-550, 0))
    mapping = _node(nt, "ShaderNodeMapping", (-380, 0))
    math_n = _node(nt, "ShaderNodeMath", (0, 0))
    math_n.operation = "GREATER_THAN"
    math_n.inputs[1].default_value = 0.55

    # Brick texture for mortar lines
    brick.inputs["Scale"].default_value = 8.0
    brick.inputs["Mortar Size"].default_value = 0.04
    brick.inputs["Mortar Smooth"].default_value = 0.2
    brick.inputs["Bias"].default_value = 0.0
    brick.inputs["Brick Width"].default_value = 0.62
    brick.inputs["Row Height"].default_value = 0.25
    brick.inputs["Color1"].default_value = (0.72, 0.38, 0.18, 1.0)   # terracotta
    brick.inputs["Color2"].default_value = (0.65, 0.32, 0.14, 1.0)   # darker terracotta
    brick.inputs["Mortar"].default_value = (0.88, 0.84, 0.76, 1.0)   # cream mortar

    # Wave for banding overlay
    wave.wave_type = "RINGS"
    wave.inputs["Scale"].default_value = 12.0
    wave.inputs["Distortion"].default_value = 0.8
    wave.inputs["Detail"].default_value = 4.0

    mix.blend_type = "MIX"
    mix.inputs["Color2"].default_value = (0.90, 0.86, 0.76, 1.0)   # cream highlight

    bsdf.inputs["Roughness"].default_value = 0.75

    _link(nt, coord, "UV", mapping, "Vector")
    _link(nt, mapping, "Vector", brick, "Vector")
    _link(nt, mapping, "Vector", wave, "Vector")
    _link(nt, brick, "Color", mix, "Color1")
    _link(nt, wave, "Color", math_n, "Value")
    _link(nt, math_n, "Value", mix, "Fac")
    _link(nt, mix, "Color", bsdf, "Base Color")
    _link(nt, bsdf, "BSDF", out, "Surface")

    return mat


def make_gold_trim_material(name: str = "GoldTrim_Timurid") -> bpy.types.Material:
    """Metallic gold used on dome finials and arch keystone trim."""
    mat = _get_or_new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = _node(nt, "ShaderNodeOutputMaterial", (400, 0))
    bsdf = _node(nt, "ShaderNodeBsdfPrincipled", (150, 0))
    bsdf.inputs["Base Color"].default_value = (0.85, 0.65, 0.10, 1.0)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.2
    _link(nt, bsdf, "BSDF", out, "Surface")
    return mat


def apply_tile_materials_to_collection(col: bpy.types.Collection):
    """
    Auto-assign tile materials to objects in the Registan collection
    based on their name prefix.
    """
    dome_mat = make_dome_tile_material()
    facade_mat = make_facade_tile_material()
    gold_mat = make_gold_trim_material()

    for obj in col.objects:
        if obj.type != "MESH":
            continue
        name = obj.name.lower()
        if "dome" in name:
            _assign(obj, dome_mat)
        elif "base" in name or "wall" in name or "arch" in name:
            _assign(obj, facade_mat)
        elif "minaret" in name:
            _assign(obj, facade_mat)
        elif "muqarnas" in name:
            cream = _get_or_new("MuqarnasCream")
            cream.use_nodes = True
            bsdf = cream.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Base Color"].default_value = (0.92, 0.88, 0.80, 1.0)
                bsdf.inputs["Roughness"].default_value = 0.65
            _assign(obj, cream)


# ---------------------------------------------------------------------------
# Node helpers
# ---------------------------------------------------------------------------

def _get_or_new(name: str) -> bpy.types.Material:
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    return bpy.data.materials.new(name=name)


def _node(nt, type_name: str, loc: tuple) -> bpy.types.Node:
    n = nt.nodes.new(type=type_name)
    n.location = loc
    return n


def _link(nt, from_node, from_socket: str, to_node, to_socket: str):
    nt.links.new(from_node.outputs[from_socket], to_node.inputs[to_socket])


def _assign(obj: bpy.types.Object, mat: bpy.types.Material):
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)