"""
base_shader.py
Foundational Principled BSDF shader builder for the Registan Generator.

All other material utilities (material_utils.py, tile_material.py,
node_groups.py) call into this module rather than constructing nodes
directly, so there is a single place to:
  - ensure consistent node layout
  - set shared defaults (roughness, IOR, alpha mode)
  - handle Blender version differences (EEVEE vs Cycles inputs)

Public API
----------
make_principled(name, rgba, roughness, metallic, alpha)
    Create or update a Principled BSDF material.

make_emission(name, rgba, strength)
    Emissive material (used for light-up tile accents in Phase 2).

make_glass(name, rgba, ior, roughness)
    Glass / water material (used for fountain water surface).

make_two_layer(name, base_rgba, coat_rgba, coat_mix)
    Two-layer material: base colour blended with a coat layer.
    Approximates plaster over brick, or glaze over terracotta.

clone_material(source_name, new_name)
    Deep-copy an existing material under a new name.

set_roughness(mat, roughness)
    Update roughness on an existing material in-place.

set_base_colour(mat, rgba)
    Update base colour on an existing material in-place.

All functions are idempotent — if a material with *name* already exists
it is returned unchanged (unless force=True is passed).
"""

import bpy


# ---------------------------------------------------------------------------
# Shared defaults
# ---------------------------------------------------------------------------

DEFAULTS = {
    "roughness":   0.65,
    "metallic":    0.0,
    "specular":    0.5,
    "ior":         1.45,
    "alpha":       1.0,
    "sheen":       0.0,
    "clearcoat":   0.0,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def make_principled(
    name:      str,
    rgba:      tuple = (0.8, 0.8, 0.8, 1.0),
    roughness: float = DEFAULTS["roughness"],
    metallic:  float = DEFAULTS["metallic"],
    alpha:     float = DEFAULTS["alpha"],
    force:     bool  = False,
) -> bpy.types.Material:
    """
    Create (or retrieve) a Principled BSDF material.

    Parameters
    ----------
    name      : material datablock name
    rgba      : base colour (R, G, B, A) in linear 0–1
    roughness : 0 = mirror, 1 = fully diffuse
    metallic  : 0 = dielectric, 1 = full metal
    alpha     : 1 = opaque, <1 = transparent (enables blend mode)
    force     : if True, overwrite an existing material with the same name
    """
    if name in bpy.data.materials and not force:
        return bpy.data.materials[name]

    mat = _get_or_new(name, force)
    mat.use_nodes = True
    nt  = mat.node_tree
    nt.nodes.clear()

    out  = _node(nt, "ShaderNodeOutputMaterial", (400, 0))
    bsdf = _node(nt, "ShaderNodeBsdfPrincipled",  (100, 0))

    bsdf.inputs["Base Color"].default_value   = rgba
    bsdf.inputs["Roughness"].default_value    = roughness
    bsdf.inputs["Metallic"].default_value     = metallic

    # Handle alpha / transparency
    if alpha < 1.0:
        _set_alpha(bsdf, mat, alpha)

    # Version-safe specular
    _set_specular(bsdf, DEFAULTS["specular"])

    _link(nt, bsdf, "BSDF", out, "Surface")
    return mat


def make_emission(
    name:     str,
    rgba:     tuple = (1.0, 0.9, 0.6, 1.0),
    strength: float = 1.0,
    force:    bool  = False,
) -> bpy.types.Material:
    """
    Emissive material — glowing tile accent or light panel.
    Used in Phase 2 for illuminated calligraphy bands.
    """
    if name in bpy.data.materials and not force:
        return bpy.data.materials[name]

    mat = _get_or_new(name, force)
    mat.use_nodes = True
    nt  = mat.node_tree
    nt.nodes.clear()

    out    = _node(nt, "ShaderNodeOutputMaterial", (400,   0))
    emit   = _node(nt, "ShaderNodeEmission",        (100,   0))

    emit.inputs["Color"].default_value    = rgba
    emit.inputs["Strength"].default_value = strength

    _link(nt, emit, "Emission", out, "Surface")
    return mat


def make_glass(
    name:      str,
    rgba:      tuple = (0.08, 0.28, 0.48, 0.72),
    ior:       float = 1.33,   # water
    roughness: float = 0.05,
    force:     bool  = False,
) -> bpy.types.Material:
    """
    Glass / water material for fountain surfaces.
    Uses Principled BSDF transmission for Cycles;
    sets blend mode to BLEND for EEVEE.
    """
    if name in bpy.data.materials and not force:
        return bpy.data.materials[name]

    mat = _get_or_new(name, force)
    mat.use_nodes  = True
    mat.blend_method = "BLEND"
    nt  = mat.node_tree
    nt.nodes.clear()

    out  = _node(nt, "ShaderNodeOutputMaterial", (400, 0))
    bsdf = _node(nt, "ShaderNodeBsdfPrincipled",  (100, 0))

    bsdf.inputs["Base Color"].default_value  = rgba
    bsdf.inputs["Roughness"].default_value   = roughness
    bsdf.inputs["Metallic"].default_value    = 0.0
    _set_alpha(bsdf, mat, rgba[3])
    _set_ior(bsdf, ior)

    # Transmission (Cycles)
    try:
        bsdf.inputs["Transmission"].default_value = 0.85
    except KeyError:
        try:
            bsdf.inputs["Transmission Weight"].default_value = 0.85
        except KeyError:
            pass

    _link(nt, bsdf, "BSDF", out, "Surface")
    return mat


def make_two_layer(
    name:      str,
    base_rgba: tuple = (0.72, 0.35, 0.18, 1.0),
    coat_rgba: tuple = (0.90, 0.85, 0.75, 1.0),
    coat_mix:  float = 0.25,
    roughness: float = 0.70,
    force:     bool  = False,
) -> bpy.types.Material:
    """
    Two-layer material blending a base colour with a coat layer.
    Approximates: plaster over brick, glaze over terracotta,
    whitewash over stone.

    coat_mix = 0.0 → pure base
    coat_mix = 1.0 → pure coat
    """
    if name in bpy.data.materials and not force:
        return bpy.data.materials[name]

    mat = _get_or_new(name, force)
    mat.use_nodes = True
    nt  = mat.node_tree
    nt.nodes.clear()

    out   = _node(nt, "ShaderNodeOutputMaterial", (600,   0))
    bsdf  = _node(nt, "ShaderNodeBsdfPrincipled",  (380,   0))
    mix   = _node(nt, "ShaderNodeMixRGB",           (180,   0))
    noise = _node(nt, "ShaderNodeTexNoise",         (-80,  50))
    coord = _node(nt, "ShaderNodeTexCoord",         (-280,  50))

    # Noise breaks up the sharp coat edge for realism
    noise.inputs["Scale"].default_value     = 12.0
    noise.inputs["Detail"].default_value    = 4.0
    noise.inputs["Roughness"].default_value = 0.6

    mix.blend_type = "MIX"
    mix.inputs["Color1"].default_value = base_rgba
    mix.inputs["Color2"].default_value = coat_rgba
    mix.inputs["Fac"].default_value    = coat_mix

    bsdf.inputs["Roughness"].default_value = roughness
    _set_specular(bsdf, DEFAULTS["specular"])

    _link(nt, coord, "Object", noise, "Vector")
    _link(nt, noise, "Fac",    mix,   "Fac")
    _link(nt, mix,   "Color",  bsdf,  "Base Color")
    _link(nt, bsdf,  "BSDF",   out,   "Surface")
    return mat


def clone_material(source_name: str, new_name: str) -> bpy.types.Material | None:
    """
    Deep-copy an existing material under a new name.
    Returns None if source_name does not exist.
    """
    if source_name not in bpy.data.materials:
        return None
    src = bpy.data.materials[source_name]
    clone = src.copy()
    clone.name = new_name
    return clone


def set_roughness(mat: bpy.types.Material, roughness: float):
    """Update roughness on an existing material in-place."""
    if not mat.use_nodes:
        return
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Roughness"].default_value = max(0.0, min(1.0, roughness))


def set_base_colour(mat: bpy.types.Material, rgba: tuple):
    """Update base colour on an existing material in-place."""
    if not mat.use_nodes:
        return
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba


# ---------------------------------------------------------------------------
# Convenience wrappers used by material_utils.py
# ---------------------------------------------------------------------------

def timurid_wall() -> bpy.types.Material:
    return make_principled("timurid_wall",
                           rgba=(0.72, 0.35, 0.18, 1.0),
                           roughness=0.75)


def timurid_dome() -> bpy.types.Material:
    return make_principled("timurid_dome",
                           rgba=(0.10, 0.35, 0.65, 1.0),
                           roughness=0.15)


def timurid_marble() -> bpy.types.Material:
    return make_principled("timurid_marble",
                           rgba=(0.90, 0.88, 0.85, 1.0),
                           roughness=0.20)


def timurid_gold() -> bpy.types.Material:
    return make_principled("timurid_gold",
                           rgba=(0.85, 0.68, 0.12, 1.0),
                           roughness=0.20,
                           metallic=1.0)


def timurid_sand() -> bpy.types.Material:
    return make_principled("timurid_sand",
                           rgba=(0.80, 0.70, 0.50, 1.0),
                           roughness=0.90)


def timurid_water() -> bpy.types.Material:
    return make_glass("timurid_water",
                      rgba=(0.08, 0.28, 0.48, 0.72))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_or_new(name: str, force: bool) -> bpy.types.Material:
    if force and name in bpy.data.materials:
        bpy.data.materials.remove(bpy.data.materials[name])
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    return bpy.data.materials.new(name=name)


def _node(nt, type_name: str, loc: tuple) -> bpy.types.Node:
    n = nt.nodes.new(type=type_name)
    n.location = loc
    return n


def _link(nt, fn, fs: str, tn, ts: str):
    nt.links.new(fn.outputs[fs], tn.inputs[ts])


def _set_alpha(bsdf, mat, alpha: float):
    """Set alpha on BSDF and material blend mode — version safe."""
    try:
        bsdf.inputs["Alpha"].default_value = alpha
    except KeyError:
        pass
    if alpha < 1.0:
        mat.blend_method = "BLEND"


def _set_specular(bsdf, value: float):
    """Specular input was renamed between Blender 3.x and 4.x."""
    for key in ("Specular", "Specular IOR Level"):
        try:
            bsdf.inputs[key].default_value = value
            return
        except KeyError:
            continue


def _set_ior(bsdf, value: float):
    for key in ("IOR", "Index of Refraction"):
        try:
            bsdf.inputs[key].default_value = value
            return
        except KeyError:
            continue