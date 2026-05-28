import bpy

PALETTE = {
    "terracotta": (0.72, 0.35, 0.18, 1.0),
    "azure_tile": (0.10, 0.35, 0.65, 1.0),
    "white_marble": (0.90, 0.88, 0.85, 1.0),
    "gold": (0.85, 0.68, 0.12, 1.0),
    "sand": (0.80, 0.70, 0.50, 1.0),
    "dark_brick": (0.45, 0.28, 0.15, 1.0),
}


def get_or_create_material(name: str, rgba: tuple) -> bpy.types.Material:
    """Return an existing material by name, or create a new Principled one."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]

    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = 0.6
    return mat


def assign_material(obj: bpy.types.Object, material_name: str):
    """Assign a palette material to *obj* by name key."""
    rgba = PALETTE.get(material_name, (0.8, 0.8, 0.8, 1.0))
    mat = get_or_create_material(material_name, rgba)
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def assign_dome_material(obj: bpy.types.Object):
    assign_material(obj, "azure_tile")


def assign_wall_material(obj: bpy.types.Object):
    assign_material(obj, "terracotta")


def assign_minaret_material(obj: bpy.types.Object):
    assign_material(obj, "sand")
