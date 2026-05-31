"""
mesh_utils.py
Shared helpers for creating and linking Blender mesh objects.
"""

import bpy
import bmesh
from mathutils import Vector


def new_mesh_object(name: str, collection: bpy.types.Collection) -> bpy.types.Object:
    """Create an empty mesh object, link it into *collection*, and return it."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def apply_bmesh(bm: bmesh.types.BMesh, obj: bpy.types.Object):
    """Write a BMesh back to the mesh data of *obj* and free it."""
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def add_box(
    bm: bmesh.types.BMesh,
    center: Vector,
    size_x: float,
    size_y: float,
    size_z: float,
) -> list:
    """
    Add a box (cuboid) to *bm* centred at *center*.
    Returns the list of created faces.
    """
    matrix = bpy.context.object.matrix_world if bpy.context.object else None  # unused but kept for future transform work
    verts_before = set(bm.verts)
    bmesh.ops.create_cube(bm, size=1.0)
    new_verts = [v for v in bm.verts if v not in verts_before]
    # Scale and translate each new vertex
    for v in new_verts:
        v.co.x = v.co.x * size_x + center.x
        v.co.y = v.co.y * size_y + center.y
        v.co.z = v.co.z * size_z + center.z
    return new_verts


def set_origin_to_bottom(obj: bpy.types.Object):
    """Move the object origin to the bottom-centre of the bounding box."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    # Shift origin down by half height
    obj.location.z += obj.dimensions.z / 2
