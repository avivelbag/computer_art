# Piece 81 — Newton's Basin

Newton's method fractal: basins of attraction on the complex plane, rendered entirely in a WebGL fragment shader.

## Algorithm

For each pixel the shader maps screen coordinates to a complex number `z₀ = (uv − 0.5) × scale + pan`, then iterates Newton's method up to 80 times:

```
z ← z − p(z) / p′(z)
```

Iteration stops when `|Δz| < 10⁻⁵` (convergence) or the loop exhausts. The pixel colour is determined by which root attracted `z`, modulated by a brightness ramp `0.25 + 0.75 · (1 − √(iter/80))` so fractal boundaries darken naturally.

## Polynomials

| Key | Polynomial     | Roots                          | Basin geometry              |
|-----|----------------|--------------------------------|-----------------------------|
| 1   | z³ − 1         | Cube roots of unity            | Classic triskelion / 3-way  |
| 2   | z⁴ − 1         | ±1, ±i                         | 4-fold checkerboard         |
| 3   | z⁵ − 1         | Fifth roots of unity           | 5-petal flower              |
| 4   | z³ − 2z + 2    | Three off-centre roots         | Asymmetric swirling basins  |

Polynomials auto-cycle every 8 seconds. Press **1–4** to jump directly, or **click** to step forward.

## Palette

Jewel tones: amber `#f29d0a`, teal `#08c8b8`, violet `#8c20d0`, rose `#e63373`, lime `#38cc2e`. The 3-root and 5-root polynomials use 3 and 5 colours respectively; the 4-root polynomial uses amber/teal/violet/rose.

## Controls

- **Scroll** — zoom in / out
- **Drag** — pan
- **1–4** / **click** — select polynomial

## Files

- `index.html` — self-contained WebGL animation, no external dependencies
- `thumbnail.svg` — SVG representation of the z³ − 1 basin triskelion
- `README.md` — this file
