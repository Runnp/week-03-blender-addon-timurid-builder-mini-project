bl_info = {
    "name": "Registan Generator",
    "author": "Runnp",
    "version": (0, 1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Registan",
    "description": "Procedural Timurid / Uzbek architecture generator",
    "category": "Add Mesh",
}

import bpy
import sys, os

# Ensure project root is importable
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from . import properties, operators, panels, dev_panel, snapshot_panel, palette_panel


def register():
    properties.register()
    operators.register()
    panels.register()
    dev_panel.register()
    snapshot_panel.register()
    palette_panel.register()

    # Apply config.json defaults on first load
    try:
        from utils.config import load_config, apply_to_props
        load_config(force=True)
        if hasattr(bpy.context, "scene") and bpy.context.scene:
            apply_to_props(bpy.context.scene.registan)
    except Exception as e:
        print(f"[Registan] Config load skipped: {e}")


def unregister():
    palette_panel.unregister()
    snapshot_panel.unregister()
    dev_panel.unregister()
    panels.unregister()
    operators.unregister()
    properties.unregister()


if __name__ == "__main__":
    register()