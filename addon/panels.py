import bpy


class REGISTAN_PT_MainPanel(bpy.types.Panel):
    bl_label = "Registan Generator"
    bl_idname = "REGISTAN_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Registan"

    def draw(self, context):
        layout = self.layout
        props = context.scene.registan

        # --- Presets ---
        box = layout.box()
        box.label(text="Style Preset", icon="BOOKMARKS")
        row = box.row(align=True)
        row.prop(props, "active_preset", text="")
        row.operator("registan.apply_preset", text="Load", icon="IMPORT")

        layout.separator(factor=0.5)

        # --- Building ---
        box = layout.box()
        box.label(text="Building Base", icon="MESH_CUBE")
        col = box.column(align=True)
        col.prop(props, "building_width")
        col.prop(props, "building_depth")
        col.prop(props, "building_height")

        # --- Dome ---
        box = layout.box()
        row = box.row()
        row.prop(props, "dome_enabled", text="")
        row.label(text="Dome", icon="MESH_UVSPHERE")
        if props.dome_enabled:
            col = box.column(align=True)
            col.prop(props, "dome_size")
            col.prop(props, "dome_segments")

        # --- Minarets ---
        box = layout.box()
        row = box.row()
        row.prop(props, "minaret_enabled", text="")
        row.label(text="Minarets", icon="MESH_CYLINDER")
        if props.minaret_enabled:
            col = box.column(align=True)
            col.prop(props, "minaret_count")
            col.prop(props, "minaret_height")
            col.prop(props, "minaret_radius")
            col.prop(props, "minaret_segments")

        # --- Arch ---
        box = layout.box()
        row = box.row()
        row.prop(props, "arch_enabled", text="")
        row.label(text="Arch Entrance", icon="MESH_TORUS")
        if props.arch_enabled:
            col = box.column(align=True)
            col.prop(props, "arch_count")
            col.prop(props, "arch_height")
            col.prop(props, "arch_width")
            # Muqarnas sub-toggle
            sub = box.row()
            sub.prop(props, "muqarnas_enabled", text="")
            sub.label(text="Muqarnas Vault", icon="OUTLINER_OB_LATTICE")
            if props.muqarnas_enabled:
                box.prop(props, "muqarnas_tiers")

        # --- Courtyard ---
        box = layout.box()
        row = box.row()
        row.prop(props, "courtyard_enabled", text="")
        row.label(text="Courtyard", icon="GRID")
        if props.courtyard_enabled:
            box.prop(props, "courtyard_size")

        # --- Misc ---
        layout.prop(props, "use_symmetry", icon="MOD_MIRROR")
        layout.separator()

        # --- Generate Button ---
        layout.operator(
            "registan.generate",
            text="Generate Building",
            icon="PLAY",
        )
        layout.operator(
            "registan.apply_tiles",
            text="Apply Tile Materials",
            icon="MATERIAL",
        )
        layout.separator(factor=0.3)
        layout.operator(
            "registan.setup_scene",
            text="Setup Scene",
            icon="LIGHT_SUN",
        )
        layout.operator(
            "registan.export_obj",
            text="Export OBJ…",
            icon="EXPORT",
        )
        layout.separator(factor=0.3)
        layout.operator(
            "registan.teardown_scene",
            text="Remove Scene Setup",
            icon="X",
        )
        layout.operator(
            "registan.clear",
            text="Clear Scene",
            icon="TRASH",
        )


def register():
    bpy.utils.register_class(REGISTAN_PT_MainPanel)


def unregister():
    bpy.utils.unregister_class(REGISTAN_PT_MainPanel)