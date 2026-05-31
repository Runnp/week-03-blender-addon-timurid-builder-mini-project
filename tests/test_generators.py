# tests/test_generators.py
"""
Headless geometry tests for the Registan generators.

Run inside Blender's Python interpreter:
    blender --background --python tests/test_generators.py

Each test creates geometry, checks vertex/face counts, then clears the scene.
"""

import bpy
import sys
import os

# Make sure project root is on the path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from generators.base_building import generate_base
from generators.dome import generate_dome
from generators.minaret import generate_minarets
from generators.arch import generate_arches
from generators.courtyard import generate_courtyard


def _make_collection(name="TestCol"):
    if name in bpy.data.collections:
        col = bpy.data.collections[name]
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        return col
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


BASE_PARAMS = {
    "width": 6.0,
    "depth": 6.0,
    "height": 4.0,
    "dome_size": 2.5,
    "dome_segments": 16,
    "minaret_height": 7.0,
    "minaret_radius": 0.4,
    "minaret_segments": 12,
    "minaret_count": 2,
    "arch_count": 1,
    "arch_height": 3.0,
    "arch_width": 1.6,
    "courtyard_size": 5.0,
    "symmetry": True,
}


def test_base_building():
    col = _make_collection()
    p = {**BASE_PARAMS, "collection": col}
    obj = generate_base(p)
    assert obj is not None, "Base building object is None"
    assert len(obj.data.vertices) > 0, "Base building has no vertices"
    print("PASS test_base_building")


def test_dome():
    col = _make_collection()
    p = {**BASE_PARAMS, "collection": col}
    obj = generate_dome(p)
    assert obj is not None, "Dome object is None"
    assert len(obj.data.vertices) > 0, "Dome has no vertices"
    print("PASS test_dome")


def test_minarets():
    col = _make_collection()
    p = {**BASE_PARAMS, "collection": col}
    generate_minarets(p)
    objs = [o for o in col.objects if "Minaret" in o.name]
    assert len(objs) == BASE_PARAMS["minaret_count"], f"Expected {BASE_PARAMS['minaret_count']} minarets, got {len(objs)}"
    print("PASS test_minarets")


def test_arches():
    col = _make_collection()
    p = {**BASE_PARAMS, "collection": col}
    generate_arches(p)
    objs = [o for o in col.objects if "Arch" in o.name]
    assert len(objs) == BASE_PARAMS["arch_count"], f"Expected {BASE_PARAMS['arch_count']} arches, got {len(objs)}"
    print("PASS test_arches")


def test_courtyard():
    col = _make_collection()
    p = {**BASE_PARAMS, "collection": col}
    generate_courtyard(p)
    objs = [o for o in col.objects if "Courtyard" in o.name or "Wall" in o.name]
    assert len(objs) > 0, "No courtyard objects generated"
    print("PASS test_courtyard")


if __name__ == "__main__":
    test_base_building()
    test_dome()
    test_minarets()
    test_arches()
    test_courtyard()
    print("\nAll tests passed.")