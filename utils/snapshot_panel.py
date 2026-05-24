"""
snapshot_panel.py
Blender panel + operators for the geometry snapshot system.

Panel: VIEW_3D > Sidebar > Registan > Snapshots (collapsed by default)

Operators:
  registan.snapshot_save    — write current props to a named slot
  registan.snapshot_load    — restore props from a named slot
  registan.snapshot_delete  — remove a named slot
"""

import bpy
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.snapshots import (
    save_snapshot, load_snapshot, delete_snapshot, list_snapshots, SNAPSHOT_LIMIT
)


# ---------------------------------------------------------------------------
# Property for the snapshot name text field (stored on scene)
# ---------------------------------------------------------------------------

def _ensure_snapshot_prop():
    if not hasattr(bpy.types.Scene, "registan_snap_name"):
        bpy.types.Scene.registan_snap_name = bpy.props.StringProperty(
            name="Snapshot Name",
            default="my_build",
            maxlen=48,
            description="Name for the snapshot slot to save / load / delete",
        )


# ---------------------------------------------------------------------------
# Panel
# ---------------------------------------------------------------------------

class REGISTAN_PT_SnapshotPanel(bpy.types.Panel):
    bl_label = "Snapshots"
    bl_idname = "REGISTAN_PT_snapshots"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Registan"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Name field + action buttons
        box = layout.box()
        box.label(text="Slot Name", icon="BOOKMARKS")
        box.prop(scene, "registan_snap_name", text="")
        row = box.row(align=True)
        row.operator("registan.snapshot_save",   text="Save",   icon="FILE_TICK")
        row.operator("registan.snapshot_load",   text="Load",   icon="RECOVER_LAST")
        row.operator("registan.snapshot_delete", text="",       icon="TRASH")

        # Saved slots list
        snaps = list_snapshots()
        if snaps:
            box2 = layout.box()
            box2.label(text=f"Saved Snapshots ({len(snaps)}/{SNAPSHOT_LIMIT})", icon="PRESET")
            for snap in snaps:
                row = box2.row(align=True)
                # Click name to fill the text field
                op = row.operator("registan.snapshot_select", text=snap["name"], icon="DOT")
                op.snap_name = snap["name"]
        else:
            layout.label(text="No snapshots saved yet.", icon="INFO")


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

class REGISTAN_OT_SnapshotSave(bpy.types.Operator):
    bl_idname = "registan.snapshot_save"
    bl_label = "Save Snapshot"
    bl_description = "Save current building parameters to the named snapshot slot"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        snaps = list_snapshots()
        name = context.scene.registan_snap_name.strip()
        if not name:
            self.report({"WARNING"}, "Enter a snapshot name first.")
            return {"CANCELLED"}
        existing_names = {s["name"] for s in snaps}
        if len(snaps) >= SNAPSHOT_LIMIT and name not in existing_names:
            self.report({"WARNING"}, f"Snapshot limit ({SNAPSHOT_LIMIT}) reached. Delete one first.")
            return {"CANCELLED"}
        text_name = save_snapshot(context.scene.registan, name)
        self.report({"INFO"}, f"Saved snapshot '{name}' → {text_name}")
        return {"FINISHED"}


class REGISTAN_OT_SnapshotLoad(bpy.types.Operator):
    bl_idname = "registan.snapshot_load"
    bl_label = "Load Snapshot"
    bl_description = "Restore building parameters from the named snapshot slot"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        name = context.scene.registan_snap_name.strip()
        if not name:
            self.report({"WARNING"}, "Enter a snapshot name first.")
            return {"CANCELLED"}
        ok = load_snapshot(context.scene.registan, name)
        if ok:
            self.report({"INFO"}, f"Loaded snapshot '{name}'.")
        else:
            self.report({"WARNING"}, f"Snapshot '{name}' not found.")
        return {"FINISHED"}


class REGISTAN_OT_SnapshotDelete(bpy.types.Operator):
    bl_idname = "registan.snapshot_delete"
    bl_label = "Delete Snapshot"
    bl_description = "Delete the named snapshot slot"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        name = context.scene.registan_snap_name.strip()
        if not name:
            self.report({"WARNING"}, "Enter a snapshot name first.")
            return {"CANCELLED"}
        ok = delete_snapshot(name)
        if ok:
            self.report({"INFO"}, f"Deleted snapshot '{name}'.")
        else:
            self.report({"WARNING"}, f"Snapshot '{name}' not found.")
        return {"FINISHED"}


class REGISTAN_OT_SnapshotSelect(bpy.types.Operator):
    """Click a saved snapshot name to fill the name field."""
    bl_idname = "registan.snapshot_select"
    bl_label = "Select Snapshot"
    bl_options = {"INTERNAL"}

    snap_name: bpy.props.StringProperty()

    def execute(self, context):
        context.scene.registan_snap_name = self.snap_name
        return {"FINISHED"}


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

_CLASSES = [
    REGISTAN_OT_SnapshotSave,
    REGISTAN_OT_SnapshotLoad,
    REGISTAN_OT_SnapshotDelete,
    REGISTAN_OT_SnapshotSelect,
    REGISTAN_PT_SnapshotPanel,
]


def register():
    _ensure_snapshot_prop()
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
    if hasattr(bpy.types.Scene, "registan_snap_name"):
        del bpy.types.Scene.registan_snap_name