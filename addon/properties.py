import bpy


class RegistanProperties(bpy.types.PropertyGroup):

    # --- Building base ---
    building_width: bpy.props.FloatProperty(
        name="Building Width",
        default=6.0,
        min=2.0,
        max=20.0,
        description="Width of the main building base",
    )
    building_height: bpy.props.FloatProperty(
        name="Building Height",
        default=4.0,
        min=1.0,
        max=15.0,
        description="Height of the main building walls",
    )
    building_depth: bpy.props.FloatProperty(
        name="Building Depth",
        default=6.0,
        min=2.0,
        max=20.0,
        description="Depth of the main building base",
    )

    # --- Dome ---
    dome_enabled: bpy.props.BoolProperty(
        name="Dome",
        default=True,
        description="Generate a dome on top of the building",
    )
    dome_size: bpy.props.FloatProperty(
        name="Dome Size",
        default=2.5,
        min=0.5,
        max=8.0,
        description="Radius of the dome",
    )
    dome_segments: bpy.props.IntProperty(
        name="Dome Segments",
        default=16,
        min=6,
        max=64,
        description="Horizontal ring segments for dome mesh quality",
    )

    # --- Minarets ---
    minaret_enabled: bpy.props.BoolProperty(
        name="Minarets",
        default=True,
        description="Generate corner minarets",
    )
    minaret_count: bpy.props.IntProperty(
        name="Minaret Count",
        default=2,
        min=0,
        max=4,
        description="Number of minarets (placed symmetrically)",
    )
    minaret_height: bpy.props.FloatProperty(
        name="Minaret Height",
        default=7.0,
        min=2.0,
        max=20.0,
        description="Total height of each minaret",
    )
    minaret_radius: bpy.props.FloatProperty(
        name="Minaret Radius",
        default=0.4,
        min=0.1,
        max=1.5,
        description="Radius of the minaret shaft",
    )
    minaret_segments: bpy.props.IntProperty(
        name="Minaret Segments",
        default=12,
        min=6,
        max=32,
    )

    # --- Arch / Iwan entrance ---
    arch_enabled: bpy.props.BoolProperty(
        name="Arch Entrance",
        default=True,
        description="Generate an iwan arch on the front face",
    )
    arch_count: bpy.props.IntProperty(
        name="Arch Count",
        default=1,
        min=1,
        max=5,
        description="Number of arch openings on the facade",
    )
    arch_height: bpy.props.FloatProperty(
        name="Arch Height",
        default=3.0,
        min=1.0,
        max=8.0,
    )
    arch_width: bpy.props.FloatProperty(
        name="Arch Width",
        default=1.6,
        min=0.5,
        max=4.0,
    )

    # --- Courtyard ---
    courtyard_enabled: bpy.props.BoolProperty(
        name="Courtyard",
        default=False,
        description="Generate an open courtyard in front",
    )
    courtyard_size: bpy.props.FloatProperty(
        name="Courtyard Size",
        default=5.0,
        min=2.0,
        max=20.0,
    )

    # --- Symmetry ---
    use_symmetry: bpy.props.BoolProperty(
        name="Symmetry",
        default=True,
        description="Mirror elements across the X axis",
    )


def register():
    bpy.utils.register_class(RegistanProperties)
    bpy.types.Scene.registan = bpy.props.PointerProperty(type=RegistanProperties)


def unregister():
    del bpy.types.Scene.registan
    bpy.utils.unregister_class(RegistanProperties)