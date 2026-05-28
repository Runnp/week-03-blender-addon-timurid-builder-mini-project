import math
from mathutils import Vector


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b."""
    return a + (b - a) * t


def circle_points(n: int, radius: float, z: float = 0.0) -> list:
    """Return *n* evenly-spaced points around a circle of *radius* at height *z*."""
    points = []
    for i in range(n):
        angle = 2 * math.pi * i / n
        points.append(Vector((math.cos(angle) * radius, math.sin(angle) * radius, z)))
    return points


def dome_profile(segments_v: int, radius: float, z_base: float = 0.0) -> list:
    """
    Return a list of (r, z) pairs describing a half-sphere profile
    from equator to pole, with *segments_v* rings.
    Useful for building a lathe/spin mesh manually.
    """
    profile = []
    for i in range(segments_v + 1):
        angle = math.pi / 2 * i / segments_v  # 0 → π/2
        r = math.cos(angle) * radius
        z = math.sin(angle) * radius + z_base
        profile.append((r, z))
    return profile


def minaret_taper(base_radius: float, top_radius: float, t: float) -> float:
    """Radius at normalised height *t* (0=base, 1=top)."""
    return lerp(base_radius, top_radius, t)


def symmetric_x_positions(count: int, spread: float) -> list:
    """
    Return *count* x-positions mirrored across x=0.
    count=1  → [0]
    count=2  → [-spread/2, spread/2]
    count=4  → [-spread, -spread/3, spread/3, spread]  (evenly spaced)
    """
    if count == 1:
        return [0.0]
    step = spread / (count - 1) if count > 1 else 0
    return [- spread / 2 + step * i for i in range(count)]
