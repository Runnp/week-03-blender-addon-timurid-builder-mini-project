"""
history.py
In-session generate history stack.

Every time the user clicks "Generate Building", the full parameter dict
is pushed onto a deque (max HISTORY_LIMIT entries).  Two operators let
the user step backward / forward through the history, restoring props.

Limitations:
  - History lives only for the current Blender session (not saved to .blend).
    Use snapshots.py for persistent saves.
  - Max HISTORY_LIMIT entries; oldest are dropped automatically.

Architecture:
  A module-level deque acts as the stack.
  A pointer (int) tracks the current position.
  push()   — append to history (clears forward-future entries)
  back()   — step pointer left, restore props
  forward()— step pointer right, restore props
  peek()   — return current entry without moving pointer
"""

from collections import deque
import copy

HISTORY_LIMIT = 20

# Module-level state
_stack: deque = deque(maxlen=HISTORY_LIMIT)
_cursor: int  = -1   # index into _stack (-1 = empty)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def push(params: dict):
    """
    Push a copy of *params* onto the history stack.
    Any entries ahead of the cursor are discarded (standard undo-tree behaviour).
    """
    global _cursor, _stack

    # Trim future entries beyond current cursor
    stack_list = list(_stack)
    if _cursor >= 0 and _cursor < len(stack_list) - 1:
        stack_list = stack_list[:_cursor + 1]
        _stack = deque(stack_list, maxlen=HISTORY_LIMIT)

    _stack.append(copy.deepcopy(params))
    _cursor = len(_stack) - 1


def back(props) -> dict | None:
    """
    Step backward one entry and restore props.
    Returns the restored param dict, or None if already at oldest entry.
    """
    global _cursor
    if _cursor <= 0:
        return None
    _cursor -= 1
    entry = list(_stack)[_cursor]
    _restore_props(props, entry)
    return entry


def forward(props) -> dict | None:
    """
    Step forward one entry and restore props.
    Returns the restored param dict, or None if already at newest entry.
    """
    global _cursor
    stack_list = list(_stack)
    if _cursor >= len(stack_list) - 1:
        return None
    _cursor += 1
    entry = stack_list[_cursor]
    _restore_props(props, entry)
    return entry


def peek() -> dict | None:
    """Return the current history entry without moving the cursor."""
    if _cursor < 0 or not _stack:
        return None
    stack_list = list(_stack)
    if _cursor >= len(stack_list):
        return None
    return stack_list[_cursor]


def clear():
    global _cursor, _stack
    _stack.clear()
    _cursor = -1


def status() -> dict:
    """Return a status dict for display in the dev panel."""
    n = len(_stack)
    return {
        "total":   n,
        "cursor":  _cursor,
        "can_back":    _cursor > 0,
        "can_forward": _cursor < n - 1,
        "limit":   HISTORY_LIMIT,
    }


# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------

_PROP_MAP = {
    "width":            "building_width",
    "depth":            "building_depth",
    "height":           "building_height",
    "dome_size":        "dome_size",
    "dome_segments":    "dome_segments",
    "minaret_height":   "minaret_height",
    "minaret_radius":   "minaret_radius",
    "minaret_segments": "minaret_segments",
    "minaret_count":    "minaret_count",
    "arch_count":       "arch_count",
    "arch_height":      "arch_height",
    "arch_width":       "arch_width",
    "courtyard_size":   "courtyard_size",
}


def _restore_props(props, entry: dict):
    for param_key, prop_key in _PROP_MAP.items():
        if param_key in entry and hasattr(props, prop_key):
            try:
                setattr(props, prop_key, type(getattr(props, prop_key))(entry[param_key]))
            except (TypeError, ValueError):
                pass
