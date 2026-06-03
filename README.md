<div align="center">

# 🕌 Registan Generator

**Procedural Timurid & Uzbek architecture addon for Blender**

*Inspired by the Registan of Samarkand, the Kalon Minaret of Bukhara,*
*and a thousand years of Central Asian architectural heritage.*

![Blender](https://img.shields.io/badge/Blender-3.6%2B-orange?logo=blender)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-87%20passing-brightgreen)

</div>

---

## What Is This?

Registan Generator is a **Blender addon** that procedurally builds
Timurid-style Central Asian architecture from a set of sliders — no
3D modelling required. Adjust a few parameters, click **Generate
Building**, and a complete mosque or madrasa appears in your scene.

Every element is parametric:

- **Building base** — stepped two-tier body with adjustable width, depth, height
- **Dome** — hemisphere with tambour drum; blue glazed tile shader
- **Minarets** — tapered shafts with cone caps and optional serefe balcony gallery
- **Iwan arch** — pointed entrance arch with optional muqarnas vault above it
- **Pishtaq portal** — tall gateway frame with stepped crown parapet
- **Iwan hall** — deep vaulted room behind the arch with side niches
- **Courtyard** — open yard with perimeter walls and optional hauz fountain
- **Girih relief** — extruded 8-pointed star tile pattern on facade and dome band
- **Wall arcade** — blind pointed-arch niches along side walls
- **Full complex** — three-building Registan layout (Ulugh Beg + Tilya-Kori + Sher-Dor)

---

## Quick Start

### 1 — Install

> **No pip installs needed inside Blender.** The addon uses only
> Blender's bundled Python.

1. Download **`registan_generator.zip`** from the releases page
2. Open Blender → **Edit → Preferences → Add-ons → Install**
3. Select the zip file
4. Search for **Registan** in the add-on list and tick the checkbox
5. Press **N** in the 3D Viewport to open the sidebar
6. Click the **Registan** tab

### 2 — Generate your first building

1. Pick a style preset from the dropdown: `Timurid`, `Bukharan`, `Safavid`, or `Minimal`
2. Click **Load** to apply all preset values
3. Click **Generate Building**
4. A complete building appears in the `Registan` collection in the Outliner

### 3 — Make it look good

Click **Apply Tile Materials** → dome turns cobalt blue, walls go terracotta.
Click **Setup Scene** → three-point lighting and a framed camera appear.
Press **F12** to render.

---

## Installation for Development

If you want to run the tests or edit the source:

```powershell
# Clone the repo
git clone https://github.com/yourname/week-03-blender-addon-registan-mini-project
cd week-03-blender-addon-registan-mini-project

# Create a virtual environment (for linting + tests only — NOT inside Blender)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dev dependencies
pip install -r requirements.txt

# Run pure-Python tests (no Blender needed)
python -m pytest tests/test_utils.py tests/test_snapshots.py `
                 tests/test_systems.py tests/test_integration.py -v
```

To run the Blender-dependent tests you need a Blender binary on your PATH:

```powershell
blender --background --python tests/test_generators.py
```

---

## Panel Reference

### Presets & Detail

| Control | Description |
|---|---|
| Style Preset dropdown | Timurid / Bukharan / Safavid / Minimal |
| **Load** button | Apply all preset slider values at once |
| Detail Level | LOW (game) / MID (preview) / HIGH (render) |
| **Apply LOD** | Add SubSurf + Bevel modifiers for chosen level |
| Language | EN / O'zbek / Русский — switches all panel labels |

### Randomizer

| Control | Description |
|---|---|
| Seed | Integer seed for reproducible results |
| **Full Roll** | Randomize everything within architectural constraints |
| **Tweak** | Nudge current values by ±N% |
| Tweak % slider | How much Tweak moves each value |

### Building Elements

| Section | Key Sliders | Sub-toggles |
|---|---|---|
| Building Base | Width, Depth, Height | Dimensions |
| Dome | Size, Segments | Facet |
| Minarets | Count, Height, Radius, Segments | Serefe Balcony |
| Arch Entrance | Count, Height, Width | Muqarnas Vault, Pishtaq Portal, Iwan Hall |
| Courtyard | Size | Hauz Fountain |
| Girih Relief | Cell Size, Extrusion | Dome Band |
| Wall Arcade | Bays, Height, Back Wall | Apex Roundels |

### Actions

| Button | What It Does |
|---|---|
| **Generate Building** | Build the full building from current settings |
| **Apply Tile Materials** | Swap flat colours for procedural shaders |
| **Apply Advanced Shaders** | Inject girih star node groups onto dome |
| Weather slider + **Apply** | Add displacement + wear to age the building |
| Frames + **Animate** | Keyframe a 5-phase construction build-up animation |
| **Setup Scene** | Add 3-point lights, ground plane, framed camera |
| **Export OBJ…** | Save all Registan meshes as an OBJ file |
| **Export Floor Plan SVG…** | Save a 2D architectural floor plan |
| **Generate Complex** | Build a 3-building Registan complex |
| **Clear Scene** | Remove all generated objects |

### Developer Tools panel *(collapsed by default)*

- Live vert / face / object counts
- Generate history nav (◀ Back / Forward ▶)
- Reload Addon, Reload config.json, Write Default config.json
- Print Stats Report → full build report in system console
- Print Props to Console
- Inline changelog

### Snapshots panel *(collapsed by default)*

Save, load, and delete named parameter snapshots stored inside the
`.blend` file — survives across sessions.

### Material Palette panel *(collapsed by default)*

Live colour pickers for all 6 palette slots. Changes apply to existing
objects instantly without regenerating.

---

## Project Structure

```
addon/
  __init__.py           Register / unregister + config load on startup
  properties.py         All sliders and toggles (RegistanProperties)
  operators.py          Every bpy.types.Operator subclass
  panels.py             Main N-panel sidebar
  dev_panel.py          Developer Tools sub-panel
  snapshot_panel.py     Snapshots sub-panel
  palette_panel.py      Material Palette sub-panel
  presets.py            Named preset dicts

generators/
  base_building.py      Stepped cuboid building body
  dome.py               Hemisphere + tambour drum
  minaret.py            Tapered shaft + cone cap
  balcony.py            Serefe gallery ring
  arch.py               Pointed iwan arch
  muqarnas.py           Stalactite vault cells
  pishtaq.py            Gateway portal + stepped crown
  iwan.py               Deep vaulted entrance hall
  girih.py              Extruded star-pattern relief
  taq.py                Diamond spandrel tile pattern
  arcade.py             Blind arch wall niches
  courtyard.py          Ground plane + perimeter walls
  fountain.py           Octagonal hauz basin + column
  complex_generator.py  3-building madrasa complex

utils/
  base_shader.py        Foundational Principled BSDF builder
  math_utils.py         lerp, circle_points, dome_profile …
  mesh_utils.py         new_mesh_object, apply_bmesh …
  material_utils.py     PALETTE dict, assign helpers
  tile_material.py      Procedural shader node materials
  node_groups.py        Reusable NodeGroup datablocks
  lod.py                LOD configs + modifier management
  randomizer.py         Full Roll + Tweak with ratio constraints
  history.py            In-session generate history deque
  snapshots.py          Persistent param snapshots → .blend Text blocks
  scene_setup.py        Lighting, ground plane, camera rig
  animation.py          Build-up keyframe animation
  weathering.py         Displacement + wear node injection
  svg_export.py         Pure-Python 2D floor plan SVG writer
  i18n.py               EN / UZ / RU translation table
  config.py             config.json loader + apply_to_props()

scripts/
  headless_render.py    CLI: generate + render without opening Blender
  render_all_presets.bat  Render all 4 presets in one command (Windows)
  project_stats.py      Headless build report

tests/
  test_utils.py         math_utils, history, randomizer — 35 tests
  test_snapshots.py     Snapshot serialisation — 12 tests
  test_systems.py       config, i18n, animation, svg — 29 tests
  test_integration.py   Iwan math, node API, svg edge cases — 23 tests
  test_generators.py    Blender headless geometry tests (needs Blender)
```

---

## Headless Rendering

Render without opening the Blender UI — useful for batch jobs or CI:

```powershell
# Single render
blender --background --python scripts/headless_render.py -- `
    --preset Timurid --lod HIGH --tiles --samples 128

# All four presets at once
scripts\render_all_presets.bat "C:\Program Files\Blender Foundation\Blender 3.6\blender.exe"
```

Options: `--preset`, `--lod`, `--outdir`, `--samples`, `--tiles`, `--complex`, `--seed`

---

## Configuration

Edit `config.json` in the project root to set your personal defaults.
The addon reads it every time it registers (addon reload or Blender restart).

```json
{
  "default_preset":       "Timurid",
  "default_lod":          "MID",
  "default_language":     "UZ",
  "building_width":       8.0,
  "minaret_count":        4,
  "girih_enabled":        true
}
```

Click **Write Default config.json** in the Developer Tools panel to
generate a fresh template with all available keys.

---

## About the Architecture

> **Why Timurid?**

The Timurid dynasty (14th–16th century) produced some of the most
geometrically sophisticated architecture ever built. The Registan of
Samarkand, the Gur-e-Amir mausoleum, and the Shah-i-Zinda necropolis
are among the finest examples of parametric thinking in pre-modern
construction — every proportion governed by ratio, every surface covered
in geometric interlace derived from a handful of repeating units.

This project is an attempt to encode those rules in Python.

> **How accurate is it?**

Phase 1 is intentionally stylised — the goal is learning procedural
graphics and Blender systems through culturally meaningful architecture,
not photorealistic heritage reconstruction. Phase 2 will push toward
historically grounded proportions and proper tile UV mapping.

---

## Your Original Question — 3D Models as Reference

You asked whether you could give me 3D models of real buildings and
have the addon generate based on those. That's a great idea and it's
exactly where Phase 3 is headed. Here's how it would work:

**What you were thinking of is called *reference-driven procedural generation*
or *geometry fitting*.** The workflow would be:

1. You import a reference mesh (photogrammetry scan, or a model you
   built manually from photos)
2. A fitting algorithm measures the key dimensions — building width,
   dome radius, minaret positions, arch proportions — from the mesh
3. Those measurements are fed into the addon as parameter values
4. The addon regenerates a clean procedural version matching those proportions

This is real and doable. The tools for step 2 are Blender's `bmesh`
raycasting + bounding box analysis. Step 3 is already built. We just
need the fitting layer in between.

**For now the fastest manual version of this:**
- Open your reference model in Blender
- Use the Measure tool (N panel → View → Length) to read off dimensions
- Type those numbers into the Registan Generator sliders
- Hit Generate

That gets you a parametric twin of whatever building you measured.

---

## Roadmap

### Phase 1 — Done ✅ (36 pushes)
All generators, materials, presets, LOD, randomizer, complex builder,
snapshots, animation, weathering, SVG export, i18n, CI, 87 tests.

### Phase 2 — In Progress
- [ ] Boolean wall cuts for arch openings (real topology)
- [ ] UV-mapped tile textures (image-based, not just nodes)
- [ ] Muqarnas hood inside pishtaq spandrel
- [ ] Calligraphy band (extruded Arabic/Uzbek text curves)
- [ ] Geometry Nodes re-implementation (non-destructive)

### Phase 3 — Planned
- [ ] Reference mesh dimension fitting
- [ ] NLP prompt → parameters (`"tall bukharan style, 4 minarets, blue dome"`)
- [ ] Full procedural neighbourhood / mahalla
- [ ] Educational visualisation mode

---

## License

MIT — see `LICENSE`.

---

<div align="center">
<em>Developed by Runnp. Built in Tashkent, Uzbekistan. Inspired by Samarkand.</em>
</div>
