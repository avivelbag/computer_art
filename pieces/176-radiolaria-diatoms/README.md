# 176 — Radiolaria & Diatom Morphology

Seven microscopic siliceous organisms — radiolaria and diatoms — rendered as pen-plotter-style line art on deep navy.

Each form is generated from a polar equation:

**r(θ) = R · (a + b·sin(n·θ) + c·sin(m·θ))**

with n, m ∈ {3, 4, 6, 8, 12, 16, 24}, producing the characteristic radial lobing of real microorganism shells.

## Structure of each organism

- **Outer outline** — the full polar curve at radius R
- **Concentric shells** — 2–3 scaled copies of the outline at inner radii
- **Spines** — N radial strokes from 0.75R to 1.25R, each capped with a diamond tip
- **Inner lattice** (selected forms) — 2N fine radial spokes + two small concentric rings
- **Nucleus** — teal accent ring and filled dot at center

## Palette

| Role | Color |
|------|-------|
| Background | deep navy `#070d1a` |
| Primary strokes | bone white `#e8e0d0` |
| Secondary strokes | pale gold `#d4b483` |
| Nuclei / centers | teal `#4dd9c0` |

## Animation

Each organism rotates slowly via SMIL `<animateTransform>` around its own center. Rotation periods range from 35 s to 60 s — all well above the 20 s minimum.

## Technique

SVG / polar equations / sinusoidal radial symmetry / SMIL animation
