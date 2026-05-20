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

from . import properties, operators, panels


def register():
    properties.register()
    operators.register()
    panels.register()


def unregister():
    panels.unregister()
    operators.unregister()
    properties.unregister()


if __name__ == "__main__":
    register()