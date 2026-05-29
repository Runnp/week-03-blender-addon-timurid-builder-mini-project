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

---

## Sliders & Settings

| Setting | Default | Description |
|---|---|---|
| Building Width | 6.0 m | Width of the main body |
| Building Depth | 6.0 m | Depth of the main body |
| Building Height | 4.0 m | Wall height |
| Dome Size | 2.5 m | Hemisphere radius |
| Dome Segments | 16 | Mesh resolution |
| Minaret Count | 2 | 0–4 corner minarets |
| Minaret Height | 7.0 m | Total minaret height |
| Minaret Radius | 0.4 m | Shaft radius |
| Arch Count | 1 | Openings on front face |
| Arch Height | 3.0 m | Arch opening height |
| Arch Width | 1.6 m | Arch opening width |
| Courtyard | off | Add open courtyard |
| Courtyard Size | 5.0 m | Courtyard depth |
| Symmetry | on | Mirror elements across X |

---

## Roadmap

### Phase 1 — Done (32 pushes)
- [x] Addon boilerplate + UI panel
- [x] Utils layer (mesh, math, material helpers)
- [x] Base building + dome generators
- [x] Minaret + arch + courtyard generators
- [x] Repo files + headless test stub
- [x] Muqarnas stalactite vault generator
- [x] Procedural tile shader materials
- [x] Architectural style presets (Timurid / Bukharan / Safavid / Minimal)
- [x] Scene setup (lights, ground plane, camera) + OBJ export
- [x] Controlled randomizer (Full Roll + Tweak + seed)
- [x] LOD system (LOW / MID / HIGH, SubSurf + Bevel modifiers)
- [x] Full 3-building complex generator
- [x] Developer tools panel (stats, reload, changelog)
- [x] Pishtaq portal generator
- [x] Geometry snapshot system (save/load to .blend Text blocks)
- [x] Headless render pipeline (CLI + .bat)
- [x] Octagonal hauz fountain generator
- [x] Generate history stack (back/forward)
- [x] Pure-Python test suite — **64 tests** across 3 files
- [x] GitHub Actions CI (flake8 + pytest)
- [x] Girih tile relief geometry (extruded star patterns)
- [x] Weathering system (Musgrave displacement + wear node injection)
- [x] SVG floor plan exporter (pure Python, annotated architectural drawing)
- [x] Build animation keyframe system (5-phase construction sequence)
- [x] Serefe balcony generator (projecting gallery ring on minarets)
- [x] Multi-language UI labels (EN / O'zbek / Русский)
- [x] Config file system (config.json, hot-reload, write default)
- [x] Wall arcade generator (blind pointed-arch niches on side walls)
- [x] Material palette editor panel (live colour pickers for all 6 slots)
- [x] Dev panel fix + config hot-reload + expanded test suite (64 passing)
- [x] CHANGELOG.md + architecture diagram + contribution guide

### Phase 2
- [ ] Tile pattern textures on dome + facade
- [ ] Parametric muqarnas (stalactite vault) at arch intrados
- [ ] Multiple style presets (Timurid / Safavid / early Uzbek)
- [ ] Better mesh topology (edge loops, bevels)

### Phase 3
- [ ] Full procedural neighbourhood / madrasa complex
- [ ] NLP prompt → parameters pipeline
- [ ] Blender geometry nodes re-implementation

---

## Inspiration

- Registan, Samarkand
- Shah-i-Zinda necropolis
- Kalon Minaret, Bukhara
- Timurid architectural principles

---

## License

MIT — see `LICENSE`.