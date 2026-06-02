"""
panels.py

Defines the Blender UI panels for the Registan Generator addon. 
The main panel is located in the 3D View sidebar under the "Registan" tab, 
and it provides access to all user-configurable settings, presets, randomization controls,
and actions like generating the building or exporting assets.

"""


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
        # LOD
        row = box.row(align=True)
        row.prop(props, "active_lod", text="")
        row.operator("registan.apply_lod", text="Apply LOD", icon="MESH_ICOSPHERE")
        # Language
        box.prop(props, "ui_language", text="Language", icon="WORLD")

        layout.separator(factor=0.5)

        # --- Randomizer ---
        box = layout.box()
        box.label(text="Randomizer", icon="RNDCURVE")
        row = box.row(align=True)
        row.prop(props, "random_seed", text="Seed")
        row = box.row(align=True)
        row.operator("registan.randomize_full", text="Full Roll", icon="FILE_REFRESH")
        row.operator("registan.randomize_tweak", text="Tweak", icon="CURVE_BEZCURVE")
        box.prop(props, "random_tweak_pct", text="Tweak %", slider=True)

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
            sub_b = box.row()
            sub_b.prop(props, "balcony_enabled", text="")
            sub_b.label(text="Serefe Balcony", icon="HANDLETYPE_AUTO_CLAMP_VEC")

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
            # Pishtaq sub-toggle
            sub2 = box.row()
            sub2.prop(props, "pishtaq_enabled", text="")
            sub2.label(text="Pishtaq Portal", icon="WINDOW")
            if props.pishtaq_enabled:
                col2 = box.column(align=True)
                col2.prop(props, "pishtaq_height_factor")
                col2.prop(props, "pishtaq_width_factor")
                col2.prop(props, "pishtaq_crown_steps")
            # Iwan sub-toggle
            sub3 = box.row()
            sub3.prop(props, "iwan_enabled", text="")
            sub3.label(text="Iwan Hall", icon="MOD_BUILD")
            if props.iwan_enabled:
                col3 = box.column(align=True)
                col3.prop(props, "iwan_depth_factor")
                col3.prop(props, "iwan_side_niches")
                if props.iwan_side_niches:
                    col3.prop(props, "iwan_niche_count")

        # --- Courtyard ---
        box = layout.box()
        row = box.row()
        row.prop(props, "courtyard_enabled", text="")
        row.label(text="Courtyard", icon="GRID")
        if props.courtyard_enabled:
            box.prop(props, "courtyard_size")
            row_f = box.row()
            row_f.prop(props, "fountain_enabled", text="")
            row_f.label(text="Hauz Fountain", icon="FORCE_TURBULENCE")
            if props.fountain_enabled:
                box.prop(props, "fountain_spouts")

        # --- Misc ---
        layout.prop(props, "use_symmetry", icon="MOD_MIRROR")

        # --- Girih ---
        box = layout.box()
        row = box.row()
        row.prop(props, "girih_enabled", text="")
        row.label(text="Girih Relief", icon="MESH_GRID")
        if props.girih_enabled:
            col = box.column(align=True)
            col.prop(props, "girih_cell_size")
            col.prop(props, "girih_extrude")
            col.prop(props, "girih_dome_band")

        # --- Arcade ---
        box = layout.box()
        row = box.row()
        row.prop(props, "arcade_enabled", text="")
        row.label(text="Wall Arcade", icon="MOD_ARRAY")
        if props.arcade_enabled:
            col = box.column(align=True)
            col.prop(props, "arcade_bays")
            col.prop(props, "arcade_height_factor")
            col.prop(props, "arcade_back")
            col.prop(props, "arcade_roundel")

        # --- Complex Generator ---
        box = layout.box()
        box.label(text="Full Complex (3 Buildings)", icon="GROUP")
        col_box = box.column(align=True)
        col_box.prop(props, "complex_spacing")
        col_box.prop(props, "complex_apply_tiles")
        row = box.row(align=True)
        row.operator("registan.generate_complex", text="Generate Complex", icon="COMMUNITY")
        row.operator("registan.clear_complex", text="", icon="X")

        layout.separator()

        # --- Actions ---
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
        layout.operator(
            "registan.apply_node_groups",
            text="Apply Advanced Shaders",
            icon="NODETREE",
        )
        # Weathering
        row = layout.row(align=True)
        row.prop(context.scene.registan, "weathering_intensity", text="Weather", slider=True)
        row.operator("registan.apply_weathering", text="Apply", icon="FREEZE")
        row.operator("registan.remove_weathering", text="", icon="X")
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
        layout.operator(
            "registan.export_svg",
            text="Export Floor Plan SVG…",
            icon="FILE_IMAGE",
        )
        layout.separator(factor=0.3)
        row_anim = layout.row(align=True)
        row_anim.prop(context.scene.registan, "anim_frames", text="Frames")
        row_anim.operator("registan.create_animation", text="Animate", icon="PLAY")
        row_anim.operator("registan.clear_animation",  text="",        icon="X")
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
