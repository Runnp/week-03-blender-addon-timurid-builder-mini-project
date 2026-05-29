"""
svg_export.py
Generates a top-down 2D architectural floor plan as an SVG file.

No bpy rendering required — draws directly from the parameter dict.

Output includes:
  - Building footprint (thick outer wall lines)
  - Minaret circles at corners
  - Arch opening gaps on the front facade
  - Courtyard outline with fountain circle (if enabled)
  - North arrow + scale bar
  - Title block (building name, preset, dimensions)
  - Dimension annotations (width, depth, minaret positions)

SVG coordinate system: Y increases downward (standard SVG).
Building centre = SVG canvas centre.

Usage:
    from utils.svg_export import export_floor_plan
    export_floor_plan(p, "/path/to/output.svg")
"""

import math
import os


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def export_floor_plan(p: dict, filepath: str):
    """
    Generate a floor plan SVG from building parameters and write to *filepath*.

    Required p keys: width, depth, arch_width, arch_count, minaret_count,
    minaret_radius, courtyard_enabled, courtyard_size, fountain_enabled.
    Optional: preset name, building_height.
    """
    # Canvas setup — scale so 1 Blender metre = SCALE pixels
    SCALE   = 60          # px per metre
    PAD     = 80          # canvas padding px
    w  = p.get("width",  6.0)
    d  = p.get("depth",  6.0)
    mh = p.get("minaret_radius", 0.4)
    mn = p.get("minaret_count",  2)
    cs = p.get("courtyard_size", 5.0)
    cyd = p.get("courtyard_enabled", False)
    fnt = p.get("fountain_enabled", False)
    aw  = p.get("arch_width",  1.6)
    ac  = p.get("arch_count",  1)

    # Canvas size accounts for courtyard depth
    total_depth = d + (cs if cyd else 0)
    canvas_w = int(w * SCALE + PAD * 2 + 120)     # +120 for title block
    canvas_h = int(total_depth * SCALE + PAD * 2 + 80)

    # Centre of building on canvas
    bx = canvas_w / 2 - 60     # shift left to make room for title
    by = PAD + (cs * SCALE if cyd else 0) + d * SCALE / 2

    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                 f'width="{canvas_w}" height="{canvas_h}" '
                 f'viewBox="0 0 {canvas_w} {canvas_h}">')
    lines.append(_defs())
    lines.append(_background(canvas_w, canvas_h))

    # --- Courtyard ---
    if cyd:
        cy_y_top = by - d * SCALE / 2 - cs * SCALE
        cy_rect = _rect(
            bx - w * SCALE / 2, cy_y_top,
            w * SCALE, cs * SCALE,
            fill="#e8dcc8", stroke="#8b7355", stroke_w=1.5,
            dash="4,3",
        )
        lines.append(cy_rect)
        lines.append(f'<!-- courtyard -->')

        # Fountain circle
        if fnt:
            fr = cs * 0.22 * SCALE
            fx, fy = bx, cy_y_top + cs * SCALE / 2
            lines.append(_circle(fx, fy, fr,
                                 fill="#a8c8e0", stroke="#4a7fa0", stroke_w=1.5))
            lines.append(_circle(fx, fy, fr * 0.15,
                                 fill="#4a7fa0", stroke="none", stroke_w=0))
            lines.append(_text(fx, fy + fr + 12, "hauz", size=9,
                               anchor="middle", colour="#4a7fa0"))

    # --- Building footprint ---
    bldg_x = bx - w * SCALE / 2
    bldg_y = by - d * SCALE / 2
    lines.append(_rect(bldg_x, bldg_y, w * SCALE, d * SCALE,
                       fill="#f5f0e8", stroke="#3a2e1a", stroke_w=2.5))

    # Wall hatching (thin diagonal lines inside building)
    lines.append(_hatch(bldg_x, bldg_y, w * SCALE, d * SCALE,
                        spacing=12, colour="#c8b89a"))

    # --- Arch openings on front face ---
    front_y = by - d * SCALE / 2   # top edge in SVG = front face
    spacing = w * SCALE / (ac + 1)
    for i in range(ac):
        ax = bx - w * SCALE / 2 + spacing * (i + 1)
        ah_px = aw * SCALE
        # White gap = arch opening
        lines.append(_rect(ax - ah_px / 2, front_y - 4,
                           ah_px, 8,
                           fill="white", stroke="none", stroke_w=0))
        lines.append(_text(ax, front_y - 10, f"arch {i + 1}",
                           size=8, anchor="middle", colour="#666"))

    # --- Minarets ---
    mr_px = mh * SCALE * 1.1
    corner_offsets = [
        (-w / 2, -d / 2), (w / 2, -d / 2),
        (w / 2,  d / 2),  (-w / 2,  d / 2),
    ]
    for idx in range(min(mn, 4)):
        ox, oy = corner_offsets[idx]
        mx = bx + ox * SCALE
        my = by + oy * SCALE
        lines.append(_circle(mx, my, mr_px,
                             fill="#d4c4a0", stroke="#3a2e1a", stroke_w=1.5))
        lines.append(_circle(mx, my, mr_px * 0.4,
                             fill="#a09070", stroke="none", stroke_w=0))

    # --- Dome circle (centre of building) ---
    dome_r = p.get("dome_size", 2.5) * SCALE * 0.5
    lines.append(_circle(bx, by, dome_r,
                         fill="none", stroke="#2a5a8a",
                         stroke_w=1.5, dash="5,3"))
    lines.append(_text(bx, by + 4, "dome", size=9,
                       anchor="middle", colour="#2a5a8a"))

    # --- Dimension annotations ---
    lines += _dimensions(bx, by, w, d, SCALE, bldg_x, bldg_y)

    # --- North arrow ---
    na_x, na_y = canvas_w - 55, canvas_h - 55
    lines.append(_north_arrow(na_x, na_y))

    # --- Scale bar ---
    sb_x, sb_y = PAD, canvas_h - 28
    lines.append(_scale_bar(sb_x, sb_y, SCALE))

    # --- Title block ---
    lines += _title_block(canvas_w - 110, PAD,
                          p.get("active_preset", "Custom"),
                          w, d, p.get("height", 4.0))

    lines.append('</svg>')

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ---------------------------------------------------------------------------
# SVG primitives
# ---------------------------------------------------------------------------

def _defs():
    return (
        '<defs>'
        '<marker id="arr" markerWidth="6" markerHeight="6" '
        'refX="3" refY="3" orient="auto">'
        '<path d="M0,0 L6,3 L0,6 Z" fill="#3a2e1a"/>'
        '</marker>'
        '</defs>'
    )


def _background(w, h):
    return f'<rect width="{w}" height="{h}" fill="#faf8f4"/>'


def _rect(x, y, w, h, fill, stroke, stroke_w, dash=""):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}"{dash_attr}/>')


def _circle(cx, cy, r, fill, stroke, stroke_w, dash=""):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}"{dash_attr}/>')


def _text(x, y, text, size=10, anchor="start", colour="#222"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" '
            f'text-anchor="{anchor}" font-family="monospace" fill="{colour}">'
            f'{text}</text>')


def _hatch(x, y, w, h, spacing=12, colour="#c8b89a"):
    """Diagonal hatch lines clipped to rectangle."""
    lines = [f'<g opacity="0.4" clip-path="url(#hclip_{int(x)})">',
             f'<clipPath id="hclip_{int(x)}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>']
    n = int((w + h) / spacing) + 2
    for i in range(n):
        ox = x - h + i * spacing
        lines.append(f'<line x1="{ox:.0f}" y1="{y:.0f}" '
                     f'x2="{ox + h:.0f}" y2="{y + h:.0f}" '
                     f'stroke="{colour}" stroke-width="0.6"/>')
    lines.append('</g>')
    return "\n".join(lines)


def _dimensions(bx, by, w, d, scale, bldg_x, bldg_y):
    lines = []
    # Width dim (above building)
    oy = bldg_y - 22
    lines.append(f'<line x1="{bldg_x:.0f}" y1="{oy:.0f}" '
                 f'x2="{bldg_x + w * scale:.0f}" y2="{oy:.0f}" '
                 f'stroke="#555" stroke-width="0.8" marker-end="url(#arr)" marker-start="url(#arr)"/>')
    lines.append(_text(bx, oy - 4, f"{w:.1f} m", size=9, anchor="middle", colour="#555"))
    # Depth dim (right of building)
    ox = bldg_x + w * scale + 22
    lines.append(f'<line x1="{ox:.0f}" y1="{bldg_y:.0f}" '
                 f'x2="{ox:.0f}" y2="{bldg_y + d * scale:.0f}" '
                 f'stroke="#555" stroke-width="0.8" marker-end="url(#arr)" marker-start="url(#arr)"/>')
    lines.append(_text(ox + 4, by, f"{d:.1f} m", size=9, anchor="start", colour="#555"))
    return lines


def _north_arrow(cx, cy):
    tip  = (cx, cy - 20)
    bl   = (cx - 8, cy + 12)
    br   = (cx + 8, cy + 12)
    mid  = (cx, cy + 4)
    return (
        f'<polygon points="{tip[0]},{tip[1]} {bl[0]},{bl[1]} {mid[0]},{mid[1]}" '
        f'fill="#3a2e1a"/>'
        f'<polygon points="{tip[0]},{tip[1]} {br[0]},{br[1]} {mid[0]},{mid[1]}" '
        f'fill="#aaa"/>'
        f'<text x="{cx}" y="{cy - 26}" font-size="10" text-anchor="middle" '
        f'font-family="monospace" fill="#3a2e1a">N</text>'
    )


def _scale_bar(x, y, scale):
    bar_w = scale  # = 1 metre
    return (
        f'<rect x="{x}" y="{y - 6}" width="{bar_w}" height="6" fill="#3a2e1a"/>'
        f'<text x="{x}" y="{y + 8}" font-size="8" font-family="monospace" fill="#555">0</text>'
        f'<text x="{x + bar_w}" y="{y + 8}" font-size="8" font-family="monospace" fill="#555">1 m</text>'
    )


def _title_block(x, y, preset, w, d, h):
    lines = []
    lines.append(_rect(x, y, 105, 90, fill="#f0ebe0",
                        stroke="#8b7355", stroke_w=1))
    lines.append(_text(x + 52, y + 16, "REGISTAN",  size=11, anchor="middle", colour="#2a1a0a"))
    lines.append(_text(x + 52, y + 30, "GENERATOR",  size=9,  anchor="middle", colour="#5a3a2a"))
    lines.append(_text(x + 8,  y + 46, f"Style: {preset}", size=8, colour="#444"))
    lines.append(_text(x + 8,  y + 58, f"W={w:.1f}m  D={d:.1f}m", size=8, colour="#444"))
    lines.append(_text(x + 8,  y + 70, f"H={h:.1f}m", size=8, colour="#444"))
    lines.append(_text(x + 8,  y + 84, "Floor Plan  1:1", size=7, colour="#888"))
    return lines