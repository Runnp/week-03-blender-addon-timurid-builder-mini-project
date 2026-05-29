"""
dev_panel.py
Developer tools panel — shown at the bottom of the Registan sidebar.

Features:
  - Object stats (vert/face counts for Registan collection)
  - Quick reload-addon button (saves re-opening Preferences every time)
  - Blender version check
  - Changelog display (inline, folded by default)
"""

import bpy
import sys
from .utils.history import status as history_status

CHANGELOG = [
    ("Push 13", "Dev tools panel, stats, reload, changelog"),
    ("Push 12", "Full 3-building complex generator (Registan layout)"),
    ("Push 11", "LOD system: LOW/MID/HIGH with SubSurf + Bevel modifiers"),
    ("Push 10", "Randomizer: Full Roll + Tweak with seed control"),
    ("Push 9",  "Scene setup (lights/camera) + OBJ export operator"),
    ("Push 8",  "Architectural style presets: Timurid, Bukharan, Safavid, Minimal"),
    ("Push 7",  "Procedural tile materials (Voronoi dome, Brick facade, Gold trim)"),
    ("Push 6",  "Muqarnas stalactite vault generator"),
    ("Push 5",  "Repo files: README, .gitignore, requirements, tests"),
    ("Push 4",  "Minaret + arch + courtyard generators"),
    ("Push 3",  "Base building + dome generators"),
    ("Push 2",  "Utils layer: mesh, math, material helpers"),
    ("Push 1",  "Addon boilerplate, UI panel, properties, operators"),
]

COLLECTION_NAME = "Registan"
COMPLEX_COLLECTION = "Registan_Complex"


class REGISTAN_PT_DevPanel(bpy.types.Panel):
    bl_label = "Developer Tools"
    bl_idname = "REGISTAN_PT_dev"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Registan"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        # --- Generate History ---
        st = history_status()
        box_h = layout.box()
        box_h.label(text=f"Generate History  ({st['cursor'] + 1 if st['total'] else 0}/{st['total']})", icon="TIME")
        row = box_h.row(align=True)
        row_back = row.operator("registan.history_back",    text="◀  Back",    icon="TRIA_LEFT")
        row_fwd  = row.operator("registan.history_forward", text="Forward  ▶", icon="TRIA_RIGHT")

        # --- Stats ---
        box = layout.box()
        box.label(text="Scene Stats", icon="INFO")

        total_verts = 0
        total_faces = 0
        total_objects = 0

        for col_name in [COLLECTION_NAME, COMPLEX_COLLECTION]:
            if col_name in bpy.data.collections:
                col = bpy.data.collections[col_name]
                for obj in col.objects:
                    if obj.type == "MESH" and obj.data:
                        total_verts += len(obj.data.vertices)
                        total_faces += len(obj.data.polygons)
                        total_objects += 1

        # Recurse into sub-collections for complex
        if COMPLEX_COLLECTION in bpy.data.collections:
            for child in bpy.data.collections[COMPLEX_COLLECTION].children:
                for obj in child.objects:
                    if obj.type == "MESH" and obj.data:
                        total_verts += len(obj.data.vertices)
                        total_faces += len(obj.data.polygons)
                        total_objects += 1

        col_layout = box.column(align=True)
        col_layout.label(text=f"Objects : {total_objects}")
        col_layout.label(text=f"Vertices: {total_verts:,}")
        col_layout.label(text=f"Faces   : {total_faces:,}")

        # Blender version
        v = bpy.app.version
        layout.label(text=f"Blender {v[0]}.{v[1]}.{v[2]}", icon="BLENDER")

        # --- Reload Addon ---
        box = layout.box()
        box.label(text="Dev Actions", icon="SCRIPT")
        box.operator("registan.reload_addon",   text="Reload Addon",              icon="FILE_REFRESH")
        box.operator("registan.print_stats",    text="Print Stats Report",        icon="OUTLINER_DATA_STATISTICS")
        box.operator("registan.reload_config",  text="Reload config.json",        icon="FILE_CACHE")
        box.operator("registan.write_config",   text="Write Default config.json", icon="FILE_NEW")
        box.operator("registan.print_props",    text="Print Props to Console",    icon="CONSOLE")

        # --- Changelog ---
        box = layout.box()
        box.label(text="Changelog", icon="RECOVER_LAST")
        for tag, note in CHANGELOG:
            row = box.row()
            row.label(text=f"[{tag}]", icon="DOT")
            row.label(text=note)


class REGISTAN_OT_ReloadAddon(bpy.types.Operator):
    bl_idname = "registan.reload_addon"
    bl_label = "Reload Registan Addon"
    bl_description = "Disable and re-enable the addon without leaving Blender"

    def execute(self, context):
        import importlib
        import addon_utils

        addon_name = __name__.split(".")[0]  # top-level package name

        # Collect all registan submodules currently loaded
        mods_to_reload = [
            name for name in sys.modules
            if name.startswith(addon_name) or name.startswith("generators") or name.startswith("utils")
        ]

        # Disable
        try:
            addon_utils.disable(addon_name, default_set=False)
        except Exception as e:
            self.report({"WARNING"}, f"Disable failed: {e}")

        # Reload submodules
        for mod_name in mods_to_reload:
            if mod_name in sys.modules:
                try:
                    importlib.reload(sys.modules[mod_name])
                except Exception:
                    del sys.modules[mod_name]

        # Re-enable
        try:
            addon_utils.enable(addon_name, default_set=False)
            self.report({"INFO"}, "Addon reloaded successfully.")
        except Exception as e:
            self.report({"ERROR"}, f"Re-enable failed: {e}")

        return {"FINISHED"}


class REGISTAN_OT_PrintStats(bpy.types.Operator):
    bl_idname = "registan.print_stats"
    bl_label = "Print Stats Report"
    bl_description = "Run the project statistics reporter and print to system console"

    def execute(self, context):
        try:
            import importlib.util, os
            script = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "scripts", "project_stats.py"
            )
            spec = importlib.util.spec_from_file_location("project_stats", script)
            mod  = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.main()
            self.report({"INFO"}, "Stats printed to system console.")
        except Exception as e:
            self.report({"ERROR"}, str(e))
        return {"FINISHED"}


class REGISTAN_OT_ReloadConfig(bpy.types.Operator):
    bl_idname = "registan.reload_config"
    bl_label = "Reload config.json"
    bl_description = "Re-read config.json and apply values to current scene properties"

    def execute(self, context):
        try:
            from .utils.config import load_config, apply_to_props
            load_config(force=True)
            applied = apply_to_props(context.scene.registan)
            self.report({"INFO"}, f"Config reloaded — {len(applied)} props updated.")
        except Exception as e:
            self.report({"ERROR"}, str(e))
        return {"FINISHED"}


class REGISTAN_OT_WriteConfig(bpy.types.Operator):
    bl_idname = "registan.write_config"
    bl_label = "Write Default config.json"
    bl_description = "Write a default config.json to the project root"

    def execute(self, context):
        try:
            from .utils.config import write_default_config, CONFIG_PATH
            write_default_config()
            self.report({"INFO"}, f"config.json written to {CONFIG_PATH}")
        except Exception as e:
            self.report({"ERROR"}, str(e))
        return {"FINISHED"}


class REGISTAN_OT_PrintProps(bpy.types.Operator):
    bl_idname = "registan.print_props"
    bl_label = "Print Props to Console"
    bl_description = "Print all current Registan property values to the system console"

    def execute(self, context):
        props = context.scene.registan
        print("\n=== Registan Properties ===")
        prop_names = [p.identifier for p in props.bl_rna.properties if p.identifier != "rna_type"]
        for name in prop_names:
            val = getattr(props, name, "?")
            print(f"  {name:30s} = {val}")
        print("===========================\n")
        self.report({"INFO"}, "Properties printed to system console.")
        return {"FINISHED"}


def register():
    bpy.utils.register_class(REGISTAN_OT_PrintStats)
    bpy.utils.register_class(REGISTAN_OT_ReloadConfig)
    bpy.utils.register_class(REGISTAN_OT_WriteConfig)
    bpy.utils.register_class(REGISTAN_OT_ReloadAddon)
    bpy.utils.register_class(REGISTAN_OT_PrintProps)
    bpy.utils.register_class(REGISTAN_PT_DevPanel)


def unregister():
    bpy.utils.unregister_class(REGISTAN_PT_DevPanel)
    bpy.utils.unregister_class(REGISTAN_OT_PrintProps)
    bpy.utils.unregister_class(REGISTAN_OT_ReloadAddon)
    bpy.utils.unregister_class(REGISTAN_OT_WriteConfig)
    bpy.utils.unregister_class(REGISTAN_OT_ReloadConfig)
    bpy.utils.unregister_class(REGISTAN_OT_PrintStats)
