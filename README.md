# week-03-blender-addon-registan-mini-project

Procedural Uzbek / Timurid-style architecture generator addon for Blender.

---

# Vision

A Blender addon that can generate stylized Central Asian architectural structures with adjustable procedural settings.

The long-term goal is to explore:

* procedural generation
* computer graphics
* digital heritage
* parametric architecture
* Blender Python API
* geometry systems

Inspired by:

* Timurid architecture
* Uzbek mosques and madrasas
* courtyards and ayvans
* blue domes
* tiled facades
* traditional symmetry

---

# Current Goals (Week 03)

## MVP

Generate:

* base structure
* dome
* minaret
* arch entrance

Using sliders/settings for:

* building width
* building height
* dome size
* minaret height
* arch count
* symmetry
* courtyard size

---

# Tech Stack

* Python
* Blender API (`bpy`)
* VS Code
* Git + GitHub

---

# Planned Features

## Phase 1

* Procedural mosque generator
* Simple UI panel
* Adjustable dimensions
* Modular geometry system

## Phase 2

* Materials/colors
* Tile pattern generation
* Multiple architectural presets
* Better topology

## Phase 3

* Full procedural neighborhoods
* Uzbek traditional homes
* Timurid madrasa presets
* AI/NLP prompt-based generation

---

# Project Structure

```text
week-03-blender-addon-registan-mini-project/
│
├── addon/
│   ├── __init__.py
│   ├── operators.py
│   ├── panels.py
│   └── properties.py
│
├── generators/
│   ├── base_building.py
│   ├── dome.py
│   ├── minaret.py
│   ├── arch.py
│   └── courtyard.py
│
├── utils/
│   ├── mesh_utils.py
│   ├── material_utils.py
│   └── math_utils.py
│
├── materials/
│
├── demo_renders/
│
├── screenshots/
│
├── tests/
│
├── .gitignore
├── README.md
├── requirements.txt
└── LICENSE
```

---

# First Development Steps

## 1. Setup Blender addon boilerplate

* register addon
* create UI panel
* add generate button

## 2. Create primitive building generator

* cube base
* scalable dimensions

## 3. Create dome generator

* UV sphere
* scaling
* placement logic

## 4. Create minaret generator

* cylinders
* modular segments

## 5. Combine into one-click generation

---

# Example Future Usage

```python
Generate Building:
- Style: Timurid
- Dome Size: 4
- Minarets: 2
- Tile Color: Blue
- Courtyard: Enabled
```

---

# Research Possibilities

Potential future directions:

* procedural reconstruction of cultural heritage
* NLP-to-3D architecture generation
* computer graphics for digital humanities
* educational visualization systems
* procedural preservation of Central Asian architecture

---

# Notes

This project is intentionally scoped as a learning-focused mini-project.

The goal is not photorealism.
The goal is learning procedural graphics and Blender systems through culturally meaningful architecture.
