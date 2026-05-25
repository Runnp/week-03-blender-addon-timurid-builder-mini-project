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
from utils.randomizer import randomize_full, randomize_tweak
from utils.lod import apply_lod_to_props, apply_lod_modifiers, LOD_NAMES, LOD_LEVELS
from generators.complex_generator import generate_complex, clear_complex
from generators.pishtaq import generate_pishtaq
from generators.fountain import generate_fountain
from generators.girih import generate_girih_panel, generate_girih_dome_band
from generators.balcony import generate_balconies
from generators.arcade import generate_arcade
from utils.history import push as history_push, back as history_back, forward as history_forward, status as history_status
from utils.weathering import apply_weathering, remove_weathering
from utils.svg_export import export_floor_plan
from utils.animation import create_build_animation, clear_build_animation


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
            if props.balcony_enabled:
                generate_balconies(p)

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

        if props.pishtaq_enabled:
            p["pishtaq_height"] = props.building_height * props.pishtaq_height_factor
            p["pishtaq_width"]  = props.arch_width * props.pishtaq_width_factor
            p["pishtaq_crown_steps"] = props.pishtaq_crown_steps
            generate_pishtaq(p)

        if props.girih_enabled:
            p["girih_cell"]    = props.girih_cell_size
            p["girih_extrude"] = props.girih_extrude
            generate_girih_panel(p)
            if props.dome_enabled and props.girih_dome_band:
                generate_girih_dome_band(p)

        if props.arcade_enabled:
            p["arcade_bays"]           = props.arcade_bays
            p["arcade_height"]         = props.building_height * props.arcade_height_factor
            p["arcade_back"]           = props.arcade_back
            p["arcade_roundel"]        = props.arcade_roundel
            generate_arcade(p)

        if props.courtyard_enabled:
            generate_courtyard(p)
            if props.fountain_enabled:
                p["fountain_spouts"] = props.fountain_spouts
                generate_fountain(p)

        history_push(p)
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


class REGISTAN_OT_CreateAnimation(bpy.types.Operator):
    bl_idname = "registan.create_animation"
    bl_label = "Create Build Animation"
    bl_description = "Keyframe a construction sequence: elements rise from ground in phases"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.registan
        frames = props.anim_frames
        create_build_animation(COLLECTION_NAME, total_frames=frames)
        create_build_animation("Registan_Complex", total_frames=frames)
        self.report({"INFO"}, f"Build animation created ({frames} frames).")
        return {"FINISHED"}


class REGISTAN_OT_ClearAnimation(bpy.types.Operator):
    bl_idname = "registan.clear_animation"
    bl_label = "Clear Build Animation"
    bl_description = "Remove all generated build animation keyframes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        clear_build_animation(COLLECTION_NAME)
        clear_build_animation("Registan_Complex")
        self.report({"INFO"}, "Build animation cleared.")
        return {"FINISHED"}


class REGISTAN_OT_ExportSVG(bpy.types.Operator):
    bl_idname = "registan.export_svg"
    bl_label = "Export Floor Plan SVG"
    bl_description = "Export a 2D top-down architectural floor plan as SVG"
    bl_options = {"REGISTER"}

    filepath: bpy.props.StringProperty(
        subtype="FILE_PATH",
        default="//registan_floor_plan.svg",
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        props = context.scene.registan
        p = {
            "width":             props.building_width,
            "depth":             props.building_depth,
            "height":            props.building_height,
            "dome_size":         props.dome_size,
            "arch_width":        props.arch_width,
            "arch_count":        props.arch_count,
            "minaret_count":     props.minaret_count,
            "minaret_radius":    props.minaret_radius,
            "courtyard_enabled": props.courtyard_enabled,
            "courtyard_size":    props.courtyard_size,
            "fountain_enabled":  props.fountain_enabled,
            "active_preset":     props.active_preset,
        }
        export_floor_plan(p, bpy.path.abspath(self.filepath))
        self.report({"INFO"}, f"SVG floor plan saved to {self.filepath}")
        return {"FINISHED"}


class REGISTAN_OT_ApplyWeathering(bpy.types.Operator):
    bl_idname = "registan.apply_weathering"
    bl_label = "Apply Weathering"
    bl_description = "Add displacement + material wear to simulate age"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        intensity = context.scene.registan.weathering_intensity
        apply_weathering(COLLECTION_NAME, intensity)
        apply_weathering("Registan_Complex", intensity)
        self.report({"INFO"}, f"Weathering applied (intensity {intensity:.2f}).")
        return {"FINISHED"}


class REGISTAN_OT_RemoveWeathering(bpy.types.Operator):
    bl_idname = "registan.remove_weathering"
    bl_label = "Remove Weathering"
    bl_description = "Strip all weathering effects"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        remove_weathering(COLLECTION_NAME)
        remove_weathering("Registan_Complex")
        self.report({"INFO"}, "Weathering removed.")
        return {"FINISHED"}


class REGISTAN_OT_HistoryBack(bpy.types.Operator):
    bl_idname = "registan.history_back"
    bl_label = "History Back"
    bl_description = "Restore previous build parameters from generate history"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        entry = history_back(context.scene.registan)
        if entry is None:
            self.report({"WARNING"}, "Already at oldest history entry.")
            return {"CANCELLED"}
        st = history_status()
        self.report({"INFO"}, f"History ← step {st['cursor'] + 1}/{st['total']}")
        return {"FINISHED"}


class REGISTAN_OT_HistoryForward(bpy.types.Operator):
    bl_idname = "registan.history_forward"
    bl_label = "History Forward"
    bl_description = "Restore next build parameters from generate history"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        entry = history_forward(context.scene.registan)
        if entry is None:
            self.report({"WARNING"}, "Already at newest history entry.")
            return {"CANCELLED"}
        st = history_status()
        self.report({"INFO"}, f"History → step {st['cursor'] + 1}/{st['total']}")
        return {"FINISHED"}


class REGISTAN_OT_ApplyLOD(bpy.types.Operator):
    bl_idname = "registan.apply_lod"
    bl_label = "Apply LOD"
    bl_description = "Set mesh resolution and modifiers for the chosen detail level"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.registan
        lod = props.active_lod
        apply_lod_to_props(props, lod)
        apply_lod_modifiers(COLLECTION_NAME, lod)
        cfg = LOD_LEVELS[lod]
        self.report({"INFO"}, f"LOD '{lod}' applied — SubSurf x{cfg.subsurf_levels}, Bevel {cfg.bevel_width:.3f}m.")
        return {"FINISHED"}


class REGISTAN_OT_RandomizeFull(bpy.types.Operator):
    bl_idname = "registan.randomize_full"
    bl_label = "Full Randomize"
    bl_description = "Randomize all parameters within architectural constraints"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.registan
        seed = props.random_seed
        applied = randomize_full(props, seed=seed)
        # Bump seed so next click gives a new result
        props.random_seed = (seed + 1) % 100000
        self.report({"INFO"}, f"Randomized (seed {seed}). Seed bumped to {props.random_seed}.")
        return {"FINISHED"}


class REGISTAN_OT_RandomizeTweak(bpy.types.Operator):
    bl_idname = "registan.randomize_tweak"
    bl_label = "Tweak"
    bl_description = "Nudge current values by a small random amount"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.registan
        seed = props.random_seed
        pct = props.random_tweak_pct / 100.0
        randomize_tweak(props, tweak_pct=pct, seed=seed)
        props.random_seed = (seed + 1) % 100000
        self.report({"INFO"}, f"Tweaked (seed {seed}).")
        return {"FINISHED"}


class REGISTAN_OT_GenerateComplex(bpy.types.Operator):
    bl_idname = "registan.generate_complex"
    bl_label = "Generate Full Complex"
    bl_description = "Generate three-building Registan madrasa complex"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.registan
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
            "muqarnas_enabled": props.muqarnas_enabled,
            "muqarnas_tiers": props.muqarnas_tiers,
            "courtyard_size": props.courtyard_size,
            "symmetry": props.use_symmetry,
            "complex_spacing": props.complex_spacing,
            "complex_apply_tiles": props.complex_apply_tiles,
        }
        generate_complex(p)
        self.report({"INFO"}, "Registan complex generated.")
        return {"FINISHED"}


class REGISTAN_OT_ClearComplex(bpy.types.Operator):
    bl_idname = "registan.clear_complex"
    bl_label = "Clear Complex"
    bl_description = "Remove the full madrasa complex"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        clear_complex()
        self.report({"INFO"}, "Complex cleared.")
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
    bpy.utils.register_class(REGISTAN_OT_ApplyLOD)
    bpy.utils.register_class(REGISTAN_OT_ApplyWeathering)
    bpy.utils.register_class(REGISTAN_OT_RemoveWeathering)
    bpy.utils.register_class(REGISTAN_OT_ExportSVG)
    bpy.utils.register_class(REGISTAN_OT_CreateAnimation)
    bpy.utils.register_class(REGISTAN_OT_ClearAnimation)
    bpy.utils.register_class(REGISTAN_OT_HistoryBack)
    bpy.utils.register_class(REGISTAN_OT_HistoryForward)
    bpy.utils.register_class(REGISTAN_OT_RandomizeFull)
    bpy.utils.register_class(REGISTAN_OT_RandomizeTweak)
    bpy.utils.register_class(REGISTAN_OT_Generate)
    bpy.utils.register_class(REGISTAN_OT_GenerateComplex)
    bpy.utils.register_class(REGISTAN_OT_ClearComplex)
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
    bpy.utils.unregister_class(REGISTAN_OT_ClearComplex)
    bpy.utils.unregister_class(REGISTAN_OT_GenerateComplex)
    bpy.utils.unregister_class(REGISTAN_OT_Generate)
    bpy.utils.unregister_class(REGISTAN_OT_RandomizeTweak)
    bpy.utils.unregister_class(REGISTAN_OT_RandomizeFull)
    bpy.utils.unregister_class(REGISTAN_OT_HistoryForward)
    bpy.utils.unregister_class(REGISTAN_OT_HistoryBack)
    bpy.utils.unregister_class(REGISTAN_OT_ClearAnimation)
    bpy.utils.unregister_class(REGISTAN_OT_CreateAnimation)
    bpy.utils.unregister_class(REGISTAN_OT_ExportSVG)
    bpy.utils.unregister_class(REGISTAN_OT_RemoveWeathering)
    bpy.utils.unregister_class(REGISTAN_OT_ApplyWeathering)
    bpy.utils.unregister_class(REGISTAN_OT_ApplyLOD)
    bpy.utils.unregister_class(REGISTAN_OT_ApplyPreset)