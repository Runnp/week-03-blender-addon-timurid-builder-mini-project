# Changelog

All notable changes to **Registan Generator** are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]
- Phase 2: muqarnas hood inside pishtaq spandrel zone
- Phase 2: boolean wall cuts for arch openings
- Phase 2: geometry nodes re-implementation
- Phase 3: NLP prompt → parameters pipeline

---

## [0.1.0] — Phase 1 Complete

### Push 32 — `chore: CHANGELOG.md + full project wrap-up`
- Added this `CHANGELOG.md` with all 32 entries
- Updated README architecture diagram and contribution guide
- Final test count: **64 pure-Python tests**, all passing

### Push 31 — `fix: dev panel + config hot-reload + 29 new tests`
- Fixed missing `REGISTAN_OT_WriteConfig` registration in `dev_panel.py`
- Added `REGISTAN_OT_ReloadConfig` operator (hot-reloads `config.json` without Blender restart)
- Added "Reload config.json" button to Developer Tools panel
- New `tests/test_systems.py`: 29 tests across `config`, `i18n`, `animation._classify`, `svg_export`
- CI workflow updated to include `test_systems.py`

### Push 30 — `feat: material palette editor panel`
- New `addon/palette_panel.py` — collapsible "Material Palette" sub-panel
- 6 live colour pickers (terracotta, azure tile, white marble, gold, sand, dark brick)
- `update` callbacks push colour changes instantly to existing materials without regenerating
- "Reset to Timurid Defaults" operator
- Registered in `addon/__init__.py`

### Push 29 — `feat: wall arcade generator`
- New `generators/arcade.py` — blind pointed-arch niches along building side walls
- Pilasters, recessed niche panels, pointed arch heads, optional apex roundel boss
- Props: `arcade_enabled`, `arcade_bays`, `arcade_height_factor`, `arcade_back`, `arcade_roundel`
- Panel section added after Girih; wired into Generate operator

### Push 28 — `chore: dev panel WriteConfig fix placeholder`
- Documented missing `WriteConfig` class registration (fixed in Push 31)
- README Phase 1 checklist updated through Push 27

### Push 27 — `feat: config.json system`
- New `utils/config.py` — JSON-based project config loader
- `config.json` shipped in project root with 20 configurable keys
- `apply_to_props()` writes config values to scene properties at addon register
- `write_default_config()` writes template file from Dev Tools panel
- Config loaded on every `register()` call via `addon/__init__.py`

### Push 26 — `feat: multi-language UI label system`
- New `utils/i18n.py` — translation table for EN / O'zbek / Русский
- 60+ panel label strings translated in both languages
- `ui_language` EnumProperty with `update` callback wired to `set_lang()`
- Language dropdown added to Presets box in main panel

### Push 25 — `feat: serefe balcony generator`
- New `generators/balcony.py` — projecting gallery ring at 2/3 minaret height
- Corbel bracket steps (2-level), annular floor slab, low parapet ring
- `balcony_enabled` toggle nested under Minarets in panel

### Push 24 — `feat: build animation keyframe system`
- New `utils/animation.py` — 5-phase construction sequence
- Objects classified by name regex into: base, minaret, dome, arch/pishtaq, courtyard/fountain
- Z-burial keyframes + final-position keyframes; dome uses BACK easing
- Frames slider + Animate / Clear row in panel actions

### Push 23 — `feat: SVG floor plan exporter`
- New `utils/svg_export.py` — pure Python, no bpy render needed
- Building footprint, wall hatching, minaret circles, arch gaps, courtyard, fountain
- North arrow, scale bar, dimension annotations, title block
- "Export Floor Plan SVG…" button in panel actions

### Push 22 — `feat: weathering / displacement system`
- New `utils/weathering.py` — Musgrave Displace modifier + wear node injection
- Vertical gradient darkening at base, roughness boost in worn zones
- `weathering_intensity` slider 0–1, Apply / Remove buttons in panel

### Push 21 — `feat: girih tile relief geometry`
- New `generators/girih.py` — extruded 8-pointed star cells on facade + dome band
- `generate_girih_panel()` tiles across full facade width
- `generate_girih_dome_band()` projects stars radially around drum
- Cell size + extrusion depth sliders; dome band toggle

### Push 20 — `chore: GitHub Actions CI`
- `.github/workflows/lint.yml` — `flake8` lint + `pytest` on push/PR to main/dev
- Runs on Ubuntu latest, Python 3.11

### Push 19 — `feat: full pure-Python test suite (35 tests)`
- `tests/test_utils.py` — math_utils, history, randomizer ratio rules
- `tests/test_snapshots.py` — snapshot serialisation / roundtrip
- mathutils stubbed so tests run without Blender installed

### Push 18 — `feat: generate history stack`
- New `utils/history.py` — module-level deque, max 20 entries
- `push()`, `back()`, `forward()`, `peek()`, `status()` API
- History nav box in Developer Tools panel (cursor position display)
- Every Generate call auto-pushes to stack

### Push 17 — `feat: octagonal hauz fountain generator`
- New `generators/fountain.py` — basin ring, water disc, pedestal, column, capital, nozzle
- Optional 4 rim spout jets; stone / water / marble materials auto-assigned
- `fountain_enabled` + `fountain_spouts` toggles nested under Courtyard

### Push 16 — `feat: headless render pipeline`
- New `scripts/headless_render.py` — full generate → light → render pipeline
- All options via CLI flags: preset, LOD, tiles, complex, seed, samples, outdir
- `scripts/render_all_presets.bat` — renders all 4 presets in one command (Windows)

### Push 15 — `feat: geometry snapshot system`
- New `utils/snapshots.py` — serialise props to Blender Text blocks (saved in .blend)
- New `addon/snapshot_panel.py` — collapsible Snapshots panel
- Save / Load / Delete / Select operators; up to 8 named slots

### Push 14 — `feat: pishtaq portal generator`
- New `generators/pishtaq.py` — tall gateway portal framing the main arch
- Left/right jamb piers, spandrel panel, stepped merlon crown, blind niches with frames
- Height/width as multiples of building/arch dimensions; crown step count slider

### Push 13 — `feat: developer tools panel`
- New `addon/dev_panel.py` — "Developer Tools" collapsible panel
- Live vert/face/object stats; Blender version display
- Reload Addon, Print Props to Console operators
- Inline changelog display (all push entries)

### Push 12 — `feat: full 3-building complex generator`
- New `generators/complex_generator.py` — West / North / East buildings in U-shape
- Each building uses per-building parameter overrides (Tilya-Kori wider, Sher-Dor taller minarets)
- Central stone plaza; sub-collections under `Registan_Complex`
- Complex spacing slider + Auto Tile Materials toggle + Generate Complex / Clear buttons

### Push 11 — `feat: LOD system (LOW / MID / HIGH)`
- New `utils/lod.py` — three detail configurations
- LOW: 8-segment meshes, no modifiers; MID: 1× SubSurf + Bevel; HIGH: 2× SubSurf
- `apply_lod_modifiers()` adds named `Registan_*` modifiers; safely re-applicable

### Push 10 — `feat: controlled randomizer`
- New `utils/randomizer.py` — Full Roll + Tweak modes
- Architectural ratio constraints (dome 35–65% of wall height, minarets always taller, arch width bounded)
- Seed auto-increments for reproducible variation; Tweak % slider

### Push 9 — `feat: scene setup + OBJ export`
- New `utils/scene_setup.py` — three-point lighting, stone ground plane, 3/4 framed camera
- `REGISTAN_OT_ExportOBJ` — file-dialog OBJ export of Registan collection
- `setup_scene()` / `teardown_scene()` operators + panel buttons

### Push 8 — `feat: architectural style presets`
- New `addon/presets.py` — Timurid, Bukharan, Safavid, Minimal
- `active_preset` EnumProperty + Load button in panel
- `apply_preset()` writes all slider values in one call

### Push 7 — `feat: procedural tile material system`
- New `utils/tile_material.py` — three shader node materials built in code
- `DomeTile_Timurid`: Voronoi + Wave cobalt/turquoise
- `FacadeTile_Timurid`: Brick + Wave terracotta
- `GoldTrim_Timurid`: metallic gold
- "Apply Tile Materials" operator auto-assigns by object name prefix

### Push 6 — `feat: muqarnas stalactite vault generator`
- New `generators/muqarnas.py` — N-tier radially-arranged concave cells
- Stucco cream material; placed above arch openings at `arch_height * 0.72`
- `muqarnas_enabled` + `muqarnas_tiers` controls nested under Arch section

### Push 5 — `chore: repo files + headless test stub`
- `README.md`, `.gitignore`, `requirements.txt`, `LICENSE`
- `tests/test_generators.py` — headless Blender test script (run locally)

### Push 4 — `feat: minaret + arch + courtyard generators`
- `generators/minaret.py` — tapered shaft, cone cap, corner placement
- `generators/arch.py` — pointed iwan arch with two-centred geometry
- `generators/courtyard.py` — ground slab + three-sided perimeter walls

### Push 3 — `feat: base building + dome generators`
- `generators/base_building.py` — stepped two-tier cuboid with inset upper block
- `generators/dome.py` — hemisphere dome with tambour drum; auto material

### Push 2 — `feat: utils layer`
- `utils/mesh_utils.py` — new_mesh_object, apply_bmesh, set_origin_to_bottom
- `utils/math_utils.py` — lerp, circle_points, dome_profile, minaret_taper, symmetric_x_positions
- `utils/material_utils.py` — Timurid colour palette, get_or_create_material, assign helpers

### Push 1 — `feat: addon boilerplate + UI panel`
- `addon/__init__.py` — bl_info, register/unregister
- `addon/properties.py` — full RegistanProperties PropertyGroup (13 sliders/toggles)
- `addon/panels.py` — REGISTAN_PT_MainPanel in VIEW_3D N-panel
- `addon/operators.py` — REGISTAN_OT_Generate + REGISTAN_OT_Clear

---

## Contributing

1. Fork the repository and create a feature branch: `git checkout -b feat/my-feature`
2. Each commit should correspond to one logical change (generator, util, panel section)
3. Add tests for any pure-Python logic in `tests/`; run `pytest` before pushing
4. Run `flake8` with `--max-line-length=120`; CI will catch violations
5. Open a PR against `main` with a description of what changed and why

## Architecture

```
addon/              Blender registration layer
  __init__.py         register() / unregister() orchestration + config load
  properties.py       RegistanProperties PropertyGroup (all sliders)
  operators.py        All bpy.types.Operator subclasses
  panels.py           Main N-panel sidebar
  dev_panel.py        Developer Tools sub-panel
  snapshot_panel.py   Snapshots sub-panel
  palette_panel.py    Material Palette sub-panel
  presets.py          Named preset dicts + apply_preset()

generators/         Procedural mesh builders (pure bpy + bmesh)
  base_building.py    Stepped cuboid building body
  dome.py             Hemisphere + tambour drum
  minaret.py          Tapered shaft + cone cap
  balcony.py          Serefe gallery ring
  arch.py             Pointed iwan arch
  muqarnas.py         Stalactite vault cells
  pishtaq.py          Gateway portal + stepped crown
  girih.py            Extruded star-pattern relief
  arcade.py           Blind arch wall niches
  courtyard.py        Ground plane + perimeter walls
  fountain.py         Octagonal hauz basin + column
  complex_generator.py  3-building madrasa complex

utils/              Shared tools (most are pure Python, testable without bpy)
  math_utils.py       lerp, circle_points, dome_profile, …
  mesh_utils.py       new_mesh_object, apply_bmesh, …
  material_utils.py   PALETTE dict, get_or_create_material, …
  tile_material.py    Procedural shader node materials
  lod.py              LOD configs + modifier management
  randomizer.py       Full Roll + Tweak with ratio constraints
  history.py          In-session generate history deque
  snapshots.py        Persistent param snapshots → .blend Text blocks
  scene_setup.py      Lighting, ground plane, camera rig
  animation.py        Build-up keyframe animation
  weathering.py       Displacement + wear node injection
  svg_export.py       Pure-Python 2D floor plan SVG writer
  i18n.py             EN / UZ / RU translation table
  config.py           config.json loader + apply_to_props()

scripts/
  headless_render.py  CLI: generate + render without Blender UI
  render_all_presets.bat  Windows batch: render all 4 presets

tests/
  test_utils.py       math_utils, history, randomizer (35 tests)
  test_snapshots.py   snapshot serialisation (12 tests)
  test_systems.py     config, i18n, animation, svg_export (29 tests - actually 29 test methods)
  test_generators.py  Blender headless tests (run locally only)
```