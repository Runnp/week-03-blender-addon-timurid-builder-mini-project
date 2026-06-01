# week-03-blender-addon-registan-mini-project

**Procedural Timurid / Uzbek architecture generator — Blender addon**

Inspired by the Registan of Samarkand, Uzbek mosques, and Central Asian Timurid heritage.

---

## What It Does

One-click procedural generation of stylised Timurid buildings inside Blender:

- Stepped building base with wall inset
- Blue hemisphere dome with tambour drum
- Tapered minarets at corners
- Pointed iwan arch entrances
- Optional open courtyard with perimeter walls

All elements are adjustable via a sidebar panel (`N` panel → **Registan** tab).

---

## Installation

1. Zip the `addon/` folder (or the whole repo root).
2. In Blender: **Edit → Preferences → Add-ons → Install** → select the zip.
3. Enable **"Registan Generator"** in the list.
4. Open the sidebar in the 3D Viewport (`N`), go to the **Registan** tab.

> Tested on Blender 3.6+. Python 3.10 (bundled with Blender) — no extra pip installs needed.

---

## Project Structure

```
addon/           Blender addon registration, UI panel, operators, properties
generators/      Procedural geometry builders (base, dome, minaret, arch, courtyard)
utils/           Shared mesh, math, and material helpers
materials/       (Phase 2) texture/node group presets
tests/           Headless test scripts for geometry validation
```

