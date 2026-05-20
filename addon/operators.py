import bpy
import sys
import os

# Allow importing from generators/ when addon is loaded as a package
_addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _addon_dir not in sys.path:
    sys.path.insert(0, _addon_dir)

from generators.base_building import generate_base
from generators.dome import generate_dome
from generators.minaret import generate_minarets
from generators.arch import generate_arches
from generators.courtyard import generate_courtyard


COLLECTION_NAME = "Registan"


def _get_or_create_collection(name: str) -> bpy.types.Collection:
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def _clear_collection(col: bpy.types.Collection):
    for obj in list(col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


class REGISTAN_OT_Generate(bpy.types.Operator):
    bl_idname = "registan.generate"
    bl_label = "Generate Registan Building"
    bl_description = "Procedurally generate a Timurid-style building"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.registan
        col = _get_or_create_collection(COLLECTION_NAME)
        _clear_collection(col)

        # Build params dict passed to every generator
        p = {
            "width": props.building_width,
            "depth": props.building_depth,
            "height": props.building_height,
            "dome_size": props.dome_size,
            "dome_segments": props.dome_segments,
            "minaret_height": props.minaret_height,
            "minaret_radius": props.minaret_radius,
            "minaret_segments": props.minaret_segments,
            "minaret_count": props.minaret_count,
            "arch_count": props.arch_count,
            "arch_height": props.arch_height,
            "arch_width": props.arch_width,
            "courtyard_size": props.courtyard_size,
            "symmetry": props.use_symmetry,
            "collection": col,
        }

        generate_base(p)

        if props.dome_enabled:
            generate_dome(p)

        if props.minaret_enabled:
            generate_minarets(p)

        if props.arch_enabled:
            generate_arches(p)

        if props.courtyard_enabled:
            generate_courtyard(p)

        self.report({"INFO"}, "Registan building generated.")
        return {"FINISHED"}


class REGISTAN_OT_Clear(bpy.types.Operator):
    bl_idname = "registan.clear"
    bl_label = "Clear Registan Scene"
    bl_description = "Remove all generated Registan objects"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if COLLECTION_NAME in bpy.data.collections:
            col = bpy.data.collections[COLLECTION_NAME]
            _clear_collection(col)
            self.report({"INFO"}, "Registan collection cleared.")
        return {"FINISHED"}


def register():
    bpy.utils.register_class(REGISTAN_OT_Generate)
    bpy.utils.register_class(REGISTAN_OT_Clear)


def unregister():
    bpy.utils.unregister_class(REGISTAN_OT_Clear)
    bpy.utils.unregister_class(REGISTAN_OT_Generate)