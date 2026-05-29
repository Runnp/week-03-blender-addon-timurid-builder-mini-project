"""
palette_panel.py
Material Palette Editor — a collapsible sub-panel that exposes all 6
Timurid palette colours as Blender colour pickers.

Changing a colour instantly updates every mesh object in the Registan
collection that uses that material, without needing to regenerate.

Palette slots (from material_utils.py):
  terracotta    — building walls, minarets
  azure_tile    — dome (flat colour mode)
  white_marble  — fountain column, blind niche inner panels
  gold          — trim, finials
  sand          — courtyard ground, fountain basin
  dark_brick    — pilaster frames, blind niche frames

Each colour is stored as a FloatVectorProperty (RGBA) on the scene.
On change, the corresponding bpy.data.materials entry is updated live.
"""

import bpy
from .utils.material_utils import PALETTE


# Default RGBA values (copied from material_utils.PALETTE)
_DEFAULTS = {
    "terracotta":  (0.72, 0.35, 0.18, 1.0),
    "azure_tile":  (0.10, 0.35, 0.65, 1.0),
    "white_marble":(0.90, 0.88, 0.85, 1.0),
    "gold":        (0.85, 0.68, 0.12, 1.0),
    "sand":        (0.80, 0.70, 0.50, 1.0),
    "dark_brick":  (0.45, 0.28, 0.15, 1.0),
}

_LABELS = {
    "terracotta":   "Terracotta (Walls)",
    "azure_tile":   "Azure Tile (Dome)",
    "white_marble": "White Marble (Fountain)",
    "gold":         "Gold (Trim)",
    "sand":         "Sand (Ground)",
    "dark_brick":   "Dark Brick (Frames)",
}


# ---------------------------------------------------------------------------
# Update callbacks — called whenever a colour property changes
# ---------------------------------------------------------------------------

def _make_update(slot_name: str):
    def _update(self, context):
        _apply_colour(slot_name, getattr(self, f"palette_{slot_name}"))
    return _update


def _apply_colour(slot_name: str, rgba):
    """Push rgba into the named material's Principled BSDF Base Color."""
    import bpy as _bpy
    mat_name = slot_name
    if mat_name not in _bpy.data.materials:
        return
    mat = _bpy.data.materials[mat_name]
    if not mat.use_nodes:
        return
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
    # Also update module-level PALETTE so new objects get the right colour
    PALETTE[slot_name] = tuple(rgba)


# ---------------------------------------------------------------------------
# Register palette colour properties on bpy.types.Scene
# ---------------------------------------------------------------------------

def _register_palette_props():
    for slot, default in _DEFAULTS.items():
        prop_name = f"palette_{slot}"
        if not hasattr(bpy.types.Scene, prop_name):
            setattr(bpy.types.Scene, prop_name,
                    bpy.props.FloatVectorProperty(
                        name=_LABELS[slot],
                        subtype="COLOR",
                        size=4,
                        min=0.0, max=1.0,
                        default=default,
                        update=_make_update(slot),
                    ))


def _unregister_palette_props():
    for slot in _DEFAULTS:
        prop_name = f"palette_{slot}"
        if hasattr(bpy.types.Scene, prop_name):
            delattr(bpy.types.Scene, prop_name)


# ---------------------------------------------------------------------------
# Panel
# ---------------------------------------------------------------------------

class REGISTAN_PT_PalettePanel(bpy.types.Panel):
    bl_label = "Material Palette"
    bl_idname = "REGISTAN_PT_palette"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Registan"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene  = context.scene

        layout.label(text="Live colour editors — changes apply instantly",
                     icon="INFO")
        layout.separator(factor=0.3)

        for slot, label in _LABELS.items():
            prop_name = f"palette_{slot}"
            row = layout.row(align=True)
            row.prop(scene, prop_name, text=label)

        layout.separator(factor=0.4)
        layout.operator("registan.reset_palette",
                        text="Reset to Timurid Defaults",
                        icon="LOOP_BACK")


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

class REGISTAN_OT_ResetPalette(bpy.types.Operator):
    bl_idname = "registan.reset_palette"
    bl_label = "Reset Palette"
    bl_description = "Restore all palette colours to Timurid defaults"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        for slot, default in _DEFAULTS.items():
            prop_name = f"palette_{slot}"
            if hasattr(scene, prop_name):
                setattr(scene, prop_name, default)
            _apply_colour(slot, default)
        self.report({"INFO"}, "Palette reset to Timurid defaults.")
        return {"FINISHED"}


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

_CLASSES = [
    REGISTAN_OT_ResetPalette,
    REGISTAN_PT_PalettePanel,
]


def register():
    _register_palette_props()
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
    _unregister_palette_props()
