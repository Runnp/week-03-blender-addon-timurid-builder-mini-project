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
from generators.muqarnas import generate_muqarnas

import sys as _sys
_sys.path.insert(0, _addon_dir)
from utils.tile_material import apply_tile_materials_to_collection

import sys as _sys2
_sys2.path.insert(0, _addon_dir)
from addon.presets import apply_preset
from utils.scene_setup import setup_scene, teardown_scene


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
            if props.muqarnas_enabled:
                p["muqarnas_tiers"] = props.muqarnas_tiers
                p["muqarnas_radius"] = props.arch_width * 0.48
                for i in range(props.arch_count):
                    spacing = p["width"] / (props.arch_count + 1)
                    cx = -p["width"] / 2 + spacing * (i + 1)
                    p["muqarnas_x"] = cx
                    p["muqarnas_z"] = props.arch_height * 0.72
                    generate_muqarnas(p)

        if props.courtyard_enabled:
            generate_courtyard(p)

        self.report({"INFO"}, "Registan building generated.")
        return {"FINISHED"}


class REGISTAN_OT_ApplyPreset(bpy.types.Operator):
    bl_idname = "registan.apply_preset"
    bl_label = "Load Preset"
    bl_description = "Apply the selected architectural style preset to all sliders"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.registan
        name = props.active_preset
        ok = apply_preset(props, name)
        if ok:
            self.report({"INFO"}, f"Preset '{name}' applied.")
        else:
            self.report({"WARNING"}, f"Unknown preset: {name}")
        return {"FINISHED"}


class REGISTAN_OT_ApplyTiles(bpy.types.Operator):
    bl_idname = "registan.apply_tiles"
    bl_label = "Apply Tile Materials"
    bl_description = "Replace flat colours with procedural Timurid tile shaders"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if COLLECTION_NAME not in bpy.data.collections:
            self.report({"WARNING"}, "No Registan collection found. Generate first.")
            return {"CANCELLED"}
        col = bpy.data.collections[COLLECTION_NAME]
        apply_tile_materials_to_collection(col)
        self.report({"INFO"}, "Tile materials applied.")
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


class REGISTAN_OT_SetupScene(bpy.types.Operator):
    bl_idname = "registan.setup_scene"
    bl_label = "Setup Scene (Lights + Camera)"
    bl_description = "Add three-point lighting, ground plane, and framed camera"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.registan
        p = {
            "width": props.building_width,
            "depth": props.building_depth,
            "height": props.building_height,
            "dome_size": props.dome_size if props.dome_enabled else 0.0,
        }
        setup_scene(p)
        self.report({"INFO"}, "Scene lighting and camera set up.")
        return {"FINISHED"}


class REGISTAN_OT_TeardownScene(bpy.types.Operator):
    bl_idname = "registan.teardown_scene"
    bl_label = "Remove Scene Setup"
    bl_description = "Remove generated lights, camera, and ground plane"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        teardown_scene()
        self.report({"INFO"}, "Scene setup removed.")
        return {"FINISHED"}


class REGISTAN_OT_ExportOBJ(bpy.types.Operator):
    bl_idname = "registan.export_obj"
    bl_label = "Export to OBJ"
    bl_description = "Export all Registan objects to an OBJ file"
    bl_options = {"REGISTER"}

    filepath: bpy.props.StringProperty(
        subtype="FILE_PATH",
        default="//registan_export.obj",
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        if COLLECTION_NAME not in bpy.data.collections:
            self.report({"WARNING"}, "No Registan collection. Generate first.")
            return {"CANCELLED"}

        col = bpy.data.collections[COLLECTION_NAME]

        # Select only Registan objects
        bpy.ops.object.select_all(action="DESELECT")
        for obj in col.objects:
            if obj.type == "MESH":
                obj.select_set(True)

        bpy.ops.wm.obj_export(
            filepath=self.filepath,
            export_selected_objects=True,
            export_materials=True,
            export_uv=True,
        )

        bpy.ops.object.select_all(action="DESELECT")
        self.report({"INFO"}, f"Exported to {self.filepath}")
        return {"FINISHED"}


def register():
    bpy.utils.register_class(REGISTAN_OT_ApplyPreset)
    bpy.utils.register_class(REGISTAN_OT_Generate)
    bpy.utils.register_class(REGISTAN_OT_ApplyTiles)
    bpy.utils.register_class(REGISTAN_OT_SetupScene)
    bpy.utils.register_class(REGISTAN_OT_TeardownScene)
    bpy.utils.register_class(REGISTAN_OT_ExportOBJ)
    bpy.utils.register_class(REGISTAN_OT_Clear)


def unregister():
    bpy.utils.unregister_class(REGISTAN_OT_Clear)
    bpy.utils.unregister_class(REGISTAN_OT_ExportOBJ)
    bpy.utils.unregister_class(REGISTAN_OT_TeardownScene)
    bpy.utils.unregister_class(REGISTAN_OT_SetupScene)
    bpy.utils.unregister_class(REGISTAN_OT_ApplyTiles)
    bpy.utils.unregister_class(REGISTAN_OT_Generate)
    bpy.utils.unregister_class(REGISTAN_OT_ApplyPreset)