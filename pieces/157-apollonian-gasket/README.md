# Piece 157 — Apollonian Gasket: Every Gap Holds a Circle

A deterministic fractal built from Descartes' Circle Theorem. Three equal circles pack symmetrically inside an enclosing circle; every triangular interstice is then filled by the unique circle tangent to all three boundary circles, recursively. The result is a self-similar foam of infinite depth — every gap is exactly and inevitably filled.

## Algorithm

Three equal inner circles of radius r = R√3/(2+√3) fit symmetrically inside an outer circle of radius R = 376 px, each pair mutually tangent.

For four mutually tangent circles with curvatures k₁…k₄, Descartes' Circle Theorem states:

```
k₄ = k₁ + k₂ + k₃ ± 2√(k₁k₂ + k₂k₃ + k₃k₁)
```

The **Apollonian reflection formula** is used instead to avoid the ±√ sign ambiguity. Given four mutually tangent circles {A, B, C, P}, the unique twin of P tangent to triple (A, B, C) is:

```
k_new = 2(kₐ + k_b + k_c) − k_P
z_new · k_new = 2(zₐkₐ + z_b·k_b + z_c·k_c) − z_P·k_P
```

where z = x + iy is the circle center as a complex number. This is numerically stable and unambiguous — no square root, no sign choice.

BFS processes all interstices in depth order. Circles with radius < 0.5 px or depth > 6 are pruned.

## Palette

| Depth | Color | Role |
|-------|-------|------|
| 0 | `rgb(232, 160, 32)` | Warm amber — the three seed circles |
| 1 | `rgb(212, 90, 64)` | Orange-red |
| 2 | `rgb(180, 60, 120)` | Pink-magenta |
| 3 | `rgb(130, 70, 190)` | Purple |
| 4 | `rgb(80, 90, 220)` | Violet-blue |
| 5 | `rgb(50, 120, 220)` | Periwinkle |
| 6 | `rgb(60, 150, 210)` | Cool blue |

Background: near-black deep navy `#050A1A`. Deeper circles fade slightly (alpha 1.0 → 0.4) to keep the fractal legible at small radii.

## Animation

One depth level (0 through 6) appears every 600 ms, revealing the self-similar structure incrementally. After all seven levels are visible the gasket holds for 2.5 s, then crossfades back to black over 1.2 s and restarts.

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `thumbnail.svg` — static 400×400 SVG snapshot (depth 0–5)
- `generate_thumbnail.py` — Python script that generates `thumbnail.svg`
- `README.md` — this file
