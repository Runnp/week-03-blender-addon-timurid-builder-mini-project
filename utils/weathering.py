"""
weathering.py
Procedural weathering system for Registan buildings.

Applies two layers of age/wear simulation:

  1. GEOMETRY DISPLACEMENT
     A Displace modifier with a Musgrave texture gives subtle
     surface irregularity (crumbling brick, eroded plaster).
     Intensity controlled by `weather_intensity` (0–1).

  2. MATERIAL WEAR MASK
     Injects a wear overlay into existing Principled BSDF materials:
     - Darker staining at the base (moisture / dirt accumulation)
     - Lighter streaking higher up (salt effloresence / bleaching)
     - Roughness increase in worn areas
     Uses a ColorRamp + Gradient Texture node group.

  3. CRACK LINES (Phase 2 placeholder)
     Reserved for a future pass using grease-pencil or curve objects
     baked into the mesh surface.

All changes are additive — the original material is preserved; only
a new node group is injected before the BSDF output.
"""

import bpy
import math

WEATHER_TEX_PREFIX = "RegWeather_"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def apply_weathering(collection_name: str, intensity: float = 0.35):
    """
    Apply displacement + material wear to all mesh objects in the collection.

    intensity : 0.0 = pristine  |  1.0 = heavily weathered
    """
    if collection_name not in bpy.data.collections:
        return

    col = bpy.data.collections[collection_name]
    _apply_to_collection(col, intensity)

    # Recurse into sub-collections (for complex)
    for child in col.children:
        _apply_to_collection(child, intensity)


def remove_weathering(collection_name: str):
    """Strip all Registan weathering modifiers and reset materials."""
    if collection_name not in bpy.data.collections:
        return
    col = bpy.data.collections[collection_name]
    _remove_from_collection(col)
    for child in col.children:
        _remove_from_collection(child)


# ---------------------------------------------------------------------------
# Per-collection helpers
# ---------------------------------------------------------------------------

def _apply_to_collection(col, intensity: float):
    for obj in col.objects:
        if obj.type != "MESH":
            continue
        _add_displace(obj, intensity)
        _inject_wear_nodes(obj, intensity)


def _remove_from_collection(col):
    for obj in col.objects:
        if obj.type != "MESH":
            continue
        _remove_modifiers(obj)
        _remove_wear_nodes(obj)


# ---------------------------------------------------------------------------
# Displacement modifier
# ---------------------------------------------------------------------------

def _add_displace(obj: bpy.types.Object, intensity: float):
    _remove_modifiers(obj)   # clean slate

    # Create or reuse Musgrave texture
    tex_name = WEATHER_TEX_PREFIX + "Displace"
    if tex_name not in bpy.data.textures:
        tex = bpy.data.textures.new(tex_name, type="MUSGRAVE")
        tex.musgrave_type = "FBM"
        tex.noise_scale   = 1.8
        tex.octaves       = 5
        tex.lacunarity    = 2.1
        tex.dimension_max = 1.0
    else:
        tex = bpy.data.textures[tex_name]

    mod = obj.modifiers.new(name="Registan_Weather_Displace", type="DISPLACE")
    mod.texture          = tex
    mod.texture_coords   = "LOCAL"
    mod.direction        = "NORMAL"
    mod.strength         = intensity * 0.08   # max ~8 cm displacement
    mod.mid_level        = 0.5


def _remove_modifiers(obj: bpy.types.Object):
    to_rm = [m for m in obj.modifiers if m.name.startswith("Registan_Weather")]
    for m in to_rm:
        obj.modifiers.remove(m)


# ---------------------------------------------------------------------------
# Material wear node injection
# ---------------------------------------------------------------------------

def _inject_wear_nodes(obj: bpy.types.Object, intensity: float):
    for slot in obj.material_slots:
        mat = slot.material
        if mat is None or not mat.use_nodes:
            continue
        nt = mat.node_tree

        # Skip if already has wear injection
        if any(n.name == "RegWear_Mix" for n in nt.nodes):
            continue

        bsdf = nt.nodes.get("Principled BSDF")
        out  = nt.nodes.get("Material Output")
        if bsdf is None or out is None:
            continue

        # Gradient texture (vertical — dark at base, light at top)
        coord  = _node(nt, "ShaderNodeTexCoord",   (-700, -200))
        grad   = _node(nt, "ShaderNodeTexGradient", (-500, -200))
        grad.gradient_type = "LINEAR"
        ramp   = _node(nt, "ShaderNodeValToRGB",   (-280, -200))
        ramp.name = "RegWear_Ramp"
        # Dark staining at bottom, clean at top
        ramp.color_ramp.elements[0].position = 0.0
        ramp.color_ramp.elements[0].color    = (0.15, 0.12, 0.08, 1.0)
        ramp.color_ramp.elements[1].position = 1.0
        ramp.color_ramp.elements[1].color    = (1.0, 1.0, 1.0, 1.0)

        # Mix with existing base colour
        mix_col = _node(nt, "ShaderNodeMixRGB", (-80, 50))
        mix_col.name       = "RegWear_Mix"
        mix_col.blend_type = "MULTIPLY"
        mix_col.inputs["Fac"].default_value = intensity * 0.55

        # Roughness boost
        math_n = _node(nt, "ShaderNodeMath", (-80, -100))
        math_n.name      = "RegWear_Rough"
        math_n.operation = "ADD"
        math_n.inputs[1].default_value = intensity * 0.25

        # Wire
        _link(nt, coord,  "Object",   grad,    "Vector")
        _link(nt, grad,   "Color",    ramp,    "Fac")
        _link(nt, ramp,   "Color",    mix_col, "Color2")
        # Intercept existing base colour input
        existing = bsdf.inputs["Base Color"].links
        if existing:
            src_node   = existing[0].from_node
            src_socket = existing[0].from_socket.name
            _link(nt, src_node, src_socket, mix_col, "Color1")
        else:
            mix_col.inputs["Color1"].default_value = \
                bsdf.inputs["Base Color"].default_value
        _link(nt, mix_col, "Color", bsdf, "Base Color")

        # Roughness intercept
        _link(nt, math_n, "Value", bsdf, "Roughness")
        math_n.inputs[0].default_value = bsdf.inputs["Roughness"].default_value


def _remove_wear_nodes(obj: bpy.types.Object):
    for slot in obj.material_slots:
        mat = slot.material
        if mat is None or not mat.use_nodes:
            continue
        nt = mat.node_tree
        to_rm = [n for n in nt.nodes
                 if n.name.startswith("RegWear_")]
        for n in to_rm:
            nt.nodes.remove(n)


# ---------------------------------------------------------------------------
# Node helpers (same pattern as tile_material.py)
# ---------------------------------------------------------------------------

def _node(nt, type_name, loc):
    n = nt.nodes.new(type=type_name)
    n.location = loc
    return n


def _link(nt, fn, fs, tn, ts):
    nt.links.new(fn.outputs[fs], tn.inputs[ts])