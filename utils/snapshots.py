"""
snapshots.py
Save and restore named building parameter snapshots.

Snapshots store the full set of RegistanProperties values as a JSON string
inside a Blender Text datablock (bpy.data.texts). This means snapshots
survive with the .blend file, are undoable, and need no external files.

Up to SNAPSHOT_LIMIT named slots are supported.
The snapshot index is stored as a custom property on the scene.

Usage (from operators):
    from utils.snapshots import save_snapshot, load_snapshot, list_snapshots, delete_snapshot
"""

import bpy
import json

SNAPSHOT_LIMIT = 8
SNAPSHOT_TEXT_PREFIX = "RegSnap_"
SNAPSHOT_INDEX_KEY = "registan_snapshot_index"   # stored on bpy.types.Scene


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def save_snapshot(props, name: str) -> str:
    """
    Serialise all RegistanProperties into a JSON Text block.
    Returns the text block name used.
    Overwrites existing snapshot with the same name.
    """
    name = _sanitize(name)
    text_name = SNAPSHOT_TEXT_PREFIX + name
    data = _props_to_dict(props)
    json_str = json.dumps(data, indent=2)

    if text_name in bpy.data.texts:
        bpy.data.texts.remove(bpy.data.texts[text_name])
    text = bpy.data.texts.new(text_name)
    text.write(json_str)
    text["registan_snapshot"] = True
    text["snapshot_name"] = name
    return text_name


def load_snapshot(props, name: str) -> bool:
    """
    Restore RegistanProperties from the named snapshot.
    Returns True on success, False if not found.
    """
    name = _sanitize(name)
    text_name = SNAPSHOT_TEXT_PREFIX + name
    if text_name not in bpy.data.texts:
        return False

    text = bpy.data.texts[text_name]
    try:
        data = json.loads(text.as_string())
    except json.JSONDecodeError:
        return False

    _dict_to_props(props, data)
    return True


def delete_snapshot(name: str) -> bool:
    name = _sanitize(name)
    text_name = SNAPSHOT_TEXT_PREFIX + name
    if text_name in bpy.data.texts:
        bpy.data.texts.remove(bpy.data.texts[text_name])
        return True
    return False


def list_snapshots() -> list[dict]:
    """
    Return a list of dicts with keys: name, text_name, prop_count.
    Sorted alphabetically by name.
    """
    results = []
    for text in bpy.data.texts:
        if text.name.startswith(SNAPSHOT_TEXT_PREFIX) and text.get("registan_snapshot"):
            snap_name = text.get("snapshot_name", text.name[len(SNAPSHOT_TEXT_PREFIX):])
            try:
                data = json.loads(text.as_string())
                count = len(data)
            except Exception:
                count = 0
            results.append({"name": snap_name, "text_name": text.name, "prop_count": count})
    return sorted(results, key=lambda x: x["name"])


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------

_SKIP = {"rna_type", "name"}


def _props_to_dict(props) -> dict:
    d = {}
    for p in props.bl_rna.properties:
        if p.identifier in _SKIP:
            continue
        val = getattr(props, p.identifier, None)
        if val is None:
            continue
        # Convert to JSON-safe types
        if isinstance(val, (bool, int, float, str)):
            d[p.identifier] = val
        elif hasattr(val, "__iter__"):
            d[p.identifier] = list(val)
    return d


def _dict_to_props(props, d: dict):
    for key, val in d.items():
        if not hasattr(props, key):
            continue
        try:
            current = getattr(props, key)
            if isinstance(current, bool):
                setattr(props, key, bool(val))
            elif isinstance(current, int):
                setattr(props, key, int(val))
            elif isinstance(current, float):
                setattr(props, key, float(val))
            elif isinstance(current, str):
                setattr(props, key, str(val))
        except Exception:
            pass


def _sanitize(name: str) -> str:
    """Strip characters that would break a Text block name."""
    return "".join(c if c.isalnum() or c in "_- " else "_" for c in name).strip() or "unnamed"
