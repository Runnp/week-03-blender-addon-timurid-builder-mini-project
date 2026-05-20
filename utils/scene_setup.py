"""
scene_setup.py
Utilities to set up a render-ready scene around the generated building.

Sets up:
  - Three-point lighting (key, fill, rim) with warm/cool balance
  - A ground plane (stone courtyard material)
  - Camera framing the whole building from a 3/4 view
  - Render settings (Cycles/EEVEE, resolution, samples)

All objects are placed in a "Registan_Scene" collection separate
from the building geometry so they can be toggled independently.
"""

import bpy
import math
from mathutils import Vector

SCENE_COLLECTION = "Registan_Scene"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def setup_scene(p: dict):
    """
    Create lighting, ground plane, and camera for the building described by p.

    p must contain:  width, depth, height, dome_size (or 0 if no dome)
    """
    col = _get_or_create_collection(SCENE_COLLECTION)
    _clear_collection(col)

    w = p.get("width", 6.0)
    d = p.get("depth", 6.0)
    h = p.get("height", 4.0)
    dome_r = p.get("dome_size", 0.0)
    total_h = h + dome_r * 2.2

    _add_ground(col, w, d)
    _add_lights(col, w, d, total_h)
    _add_camera(col, w, d, total_h)
    _configure_render()


def teardown_scene():
    """Remove all scene setup objects."""
    if SCENE_COLLECTION in bpy.data.collections:
        col = bpy.data.collections[SCENE_COLLECTION]
        _clear_collection(col)


# ---------------------------------------------------------------------------
# Ground plane
# ---------------------------------------------------------------------------

def _add_ground(col, w, d):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    plane = bpy.context.active_object
    plane.name = "Ground_Plane"
    plane.scale = (w * 4, d * 4, 1)
    bpy.ops.object.transform_apply(scale=True)

    # Move from default scene collection to our collection
    for c in list(plane.users_collection):
        c.objects.unlink(plane)
    col.objects.link(plane)

    # Stone ground material
    mat = bpy.data.materials.new("GroundStone")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.55, 0.50, 0.42, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.9
    plane.data.materials.append(mat)


# ---------------------------------------------------------------------------
# Lighting
# ---------------------------------------------------------------------------

def _add_lights(col, w, d, total_h):
    span = max(w, d)

    # Key light — warm afternoon sun from upper-right
    _sun(col, "Key_Sun",
         rotation_deg=(55, 0, -45),
         energy=4.0,
         colour=(1.0, 0.92, 0.78))

    # Fill light — cool sky light from left
    _area(col, "Fill_Area",
          location=(-span * 2, -span, total_h * 1.2),
          energy=200.0,
          size=span * 2,
          colour=(0.75, 0.85, 1.0))

    # Rim light — strong back-right to separate building from sky
    _spot(col, "Rim_Spot",
          location=(span * 1.5, -span * 1.5, total_h * 0.8),
          target=Vector((0, 0, total_h / 2)),
          energy=600.0,
          colour=(1.0, 0.96, 0.88),
          spot_size_deg=40)


def _sun(col, name, rotation_deg, energy, colour):
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 0))
    light = bpy.context.active_object
    light.name = name
    light.rotation_euler = [math.radians(r) for r in rotation_deg]
    light.data.energy = energy
    light.data.color = colour
    _relink(light, col)


def _area(col, name, location, energy, size, colour):
    bpy.ops.object.light_add(type="AREA", location=location)
    light = bpy.context.active_object
    light.name = name
    light.data.energy = energy
    light.data.size = size
    light.data.color = colour
    _relink(light, col)


def _spot(col, name, location, target, energy, colour, spot_size_deg):
    bpy.ops.object.light_add(type="SPOT", location=location)
    light = bpy.context.active_object
    light.name = name
    light.data.energy = energy
    light.data.color = colour
    light.data.spot_size = math.radians(spot_size_deg)
    # Point at target
    direction = target - Vector(location)
    light.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    _relink(light, col)


# ---------------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------------

def _add_camera(col, w, d, total_h):
    span = max(w, d)
    # 3/4 front view, elevated
    cam_dist = span * 2.8
    cam_loc = Vector((cam_dist * 0.7, -cam_dist, total_h * 0.55))

    bpy.ops.object.camera_add(location=cam_loc)
    cam = bpy.context.active_object
    cam.name = "Registan_Camera"

    # Point at building centre (slightly above ground)
    target = Vector((0, 0, total_h * 0.4))
    direction = target - cam_loc
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    cam.data.lens = 50          # mm — slight telephoto for architectural shots
    cam.data.clip_end = 1000.0

    bpy.context.scene.camera = cam
    _relink(cam, col)


# ---------------------------------------------------------------------------
# Render settings
# ---------------------------------------------------------------------------

def _configure_render():
    scene = bpy.context.scene
    render = scene.render

    render.resolution_x = 1920
    render.resolution_y = 1080
    render.resolution_percentage = 100
    render.image_settings.file_format = "PNG"

    # Use EEVEE for fast preview; user can switch to Cycles
    if hasattr(scene, "eevee"):
        scene.render.engine = "BLENDER_EEVEE_NEXT" if bpy.app.version >= (4, 0, 0) else "BLENDER_EEVEE"
        scene.eevee.taa_render_samples = 64

    # World background — light blue sky
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("RegWorld")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.52, 0.70, 0.90, 1.0)
        bg.inputs["Strength"].default_value = 0.6


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_or_create_collection(name):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def _clear_collection(col):
    for obj in list(col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def _relink(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)