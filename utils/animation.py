"""
animation.py
Build animation system for the Registan Generator.

Creates a "construction grow" animation where each building element
rises from the ground into its final position over a configurable
number of frames. Elements are ordered by build logic:

  Frame 0      : all objects at Z=0 (underground / flattened)
  Phase 1      : base building rises (0–30% of total frames)
  Phase 2      : minarets grow up (20–60%)
  Phase 3      : dome descends from above (40–70%)
  Phase 4      : arches / pishtaq / girih appear (60–85%)
  Phase 5      : courtyard, fountain, muqarnas fade in (75–100%)

Each object gets two keyframes:
  - START : location Z offset = -final_height  (buried)
  - END   : location Z offset = 0              (final position)

Easing: Blender's default Bezier interpolation gives a natural ease-in/out.
"""

import bpy
import re


# Phase timing as (start_frac, end_frac) of total_frames
PHASE_TIMING = {
    "base":      (0.00, 0.35),
    "minaret":   (0.20, 0.65),
    "dome":      (0.40, 0.72),
    "arch":      (0.55, 0.82),
    "pishtaq":   (0.60, 0.85),
    "girih":     (0.65, 0.88),
    "muqarnas":  (0.70, 0.90),
    "courtyard": (0.75, 0.95),
    "fountain":  (0.80, 1.00),
    "crown":     (0.62, 0.88),
    "niche":     (0.65, 0.90),
    "plaza":     (0.78, 1.00),
}

DEFAULT_FRAMES = 120


def create_build_animation(collection_name: str,
                           total_frames: int = DEFAULT_FRAMES,
                           start_frame: int = 1):
    """
    Insert location keyframes on all objects in the collection to animate
    the building construction sequence.

    Objects are matched to phases by name prefix (case-insensitive).
    """
    if collection_name not in bpy.data.collections:
        return

    scene = bpy.context.scene
    scene.frame_start = start_frame
    scene.frame_end   = start_frame + total_frames

    col = bpy.data.collections[collection_name]
    all_objects = list(col.objects)

    # Also gather from sub-collections (complex)
    for child in col.children:
        all_objects.extend(child.objects)

    for obj in all_objects:
        if obj.type != "MESH":
            continue

        phase = _classify(obj.name)
        t0, t1 = PHASE_TIMING.get(phase, (0.0, 0.5))

        frame_start_obj = start_frame + int(t0 * total_frames)
        frame_end_obj   = start_frame + int(t1 * total_frames)

        # Bury amount = object bounding box height
        bury_z = -(obj.dimensions.z + 0.5)

        original_z = obj.location.z

        # Keyframe 1: buried
        scene.frame_set(frame_start_obj)
        obj.location.z = original_z + bury_z
        obj.keyframe_insert(data_path="location", index=2)

        # Keyframe 2: final position
        scene.frame_set(frame_end_obj)
        obj.location.z = original_z
        obj.keyframe_insert(data_path="location", index=2)

        # Set interpolation to BACK (overshoot) for dome, EASE for rest
        _set_interpolation(obj, phase)

    # Reset to start
    scene.frame_set(start_frame)


def clear_build_animation(collection_name: str):
    """Remove all location animation curves on Registan objects."""
    if collection_name not in bpy.data.collections:
        return

    col = bpy.data.collections[collection_name]
    all_objects = list(col.objects)
    for child in col.children:
        all_objects.extend(child.objects)

    for obj in all_objects:
        if obj.type != "MESH" or obj.animation_data is None:
            continue
        action = obj.animation_data.action
        if action is None:
            continue
        # Remove only location Z curves
        to_remove = [fc for fc in action.fcurves
                     if fc.data_path == "location" and fc.array_index == 2]
        for fc in to_remove:
            action.fcurves.remove(fc)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_NAME_MAP = [
    (r"base|building|wall",   "base"),
    (r"minaret",              "minaret"),
    (r"dome",                 "dome"),
    (r"arch(?!.*pishtaq)",    "arch"),
    (r"pishtaq|pier|spandrel|crown|niche", "pishtaq"),
    (r"girih",                "girih"),
    (r"muqarnas",             "muqarnas"),
    (r"courtyard|ground|plaza", "courtyard"),
    (r"fountain|basin|water|column|pedestal|nozzle|capital|spout", "fountain"),
]


def _classify(name: str) -> str:
    n = name.lower()
    for pattern, phase in _NAME_MAP:
        if re.search(pattern, n):
            return phase
    return "base"


def _set_interpolation(obj, phase):
    if obj.animation_data is None or obj.animation_data.action is None:
        return
    interp = "BACK" if phase == "dome" else "EASE_IN_OUT"
    for fc in obj.animation_data.action.fcurves:
        if fc.data_path == "location" and fc.array_index == 2:
            for kp in fc.keyframe_points:
                kp.interpolation = interp