import bpy
from typing import NamedTuple


class LODConfig(NamedTuple):
    label: str
    dome_segments: int
    minaret_segments: int
    muqarnas_tiers_max: int
    subsurf_levels: int       # 0 = no subdivision modifier
    bevel_width: float        # 0.0 = no bevel modifier
    bevel_segments: int


LOD_LEVELS: dict[str, LODConfig] = {
    "LOW": LODConfig(
        label="Low (Game / Fast)",
        dome_segments=8,
        minaret_segments=8,
        muqarnas_tiers_max=1,
        subsurf_levels=0,
        bevel_width=0.0,
        bevel_segments=1,
    ),
    "MID": LODConfig(
        label="Mid (Preview)",
        dome_segments=16,
        minaret_segments=12,
        muqarnas_tiers_max=3,
        subsurf_levels=1,
        bevel_width=0.04,
        bevel_segments=2,
    ),
    "HIGH": LODConfig(
        label="High (Render)",
        dome_segments=32,
        minaret_segments=20,
        muqarnas_tiers_max=5,
        subsurf_levels=2,
        bevel_width=0.025,
        bevel_segments=3,
    ),
}

LOD_NAMES = list(LOD_LEVELS.keys())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def apply_lod_to_props(props, lod_name: str):
    """
    Write LOD segment counts onto RegistanProperties.
    Does NOT touch dome_size / minaret_height / arch values — only mesh resolution.
    """
    cfg = LOD_LEVELS.get(lod_name)
    if cfg is None:
        return

    props.dome_segments = cfg.dome_segments
    props.minaret_segments = cfg.minaret_segments

    # Clamp muqarnas tiers to LOD maximum
    if hasattr(props, "muqarnas_tiers"):
        props.muqarnas_tiers = min(props.muqarnas_tiers, cfg.muqarnas_tiers_max)


def apply_lod_modifiers(collection_name: str, lod_name: str):
    """
    Add / replace Subdivision Surface and Bevel modifiers on all mesh
    objects in the named collection to match the chosen LOD level.

    Safe to call multiple times — replaces existing Registan LOD modifiers.
    """
    cfg = LOD_LEVELS.get(lod_name)
    if cfg is None:
        return

    if collection_name not in bpy.data.collections:
        return

    col = bpy.data.collections[collection_name]

    for obj in col.objects:
        if obj.type != "MESH":
            continue

        _remove_lod_modifiers(obj)

        # Bevel
        if cfg.bevel_width > 0.0:
            bevel = obj.modifiers.new(name="Registan_Bevel", type="BEVEL")
            bevel.width = cfg.bevel_width
            bevel.segments = cfg.bevel_segments
            bevel.limit_method = "ANGLE"
            bevel.angle_limit = 0.785398  # 45°

        # Subdivision Surface
        if cfg.subsurf_levels > 0:
            subsurf = obj.modifiers.new(name="Registan_SubSurf", type="SUBSURF")
            subsurf.levels = cfg.subsurf_levels
            subsurf.render_levels = cfg.subsurf_levels


def remove_lod_modifiers(collection_name: str):
    """Strip all Registan LOD modifiers without changing geometry."""
    if collection_name not in bpy.data.collections:
        return
    col = bpy.data.collections[collection_name]
    for obj in col.objects:
        if obj.type == "MESH":
            _remove_lod_modifiers(obj)


# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------

def _remove_lod_modifiers(obj: bpy.types.Object):
    to_remove = [m for m in obj.modifiers if m.name.startswith("Registan_")]
    for m in to_remove:
        obj.modifiers.remove(m)
