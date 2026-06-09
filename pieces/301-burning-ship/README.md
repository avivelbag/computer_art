# Piece 301 — The Wreck Below (Burning Ship Fractal)

The Burning Ship fractal folds the complex plane with absolute values before each
squaring step, producing an asymmetric structure with a famous "ship" silhouette,
angular flame-like masts, and an entirely different character from the Mandelbrot set.

## Iteration formula

For each pixel at complex coordinate `c`:

```
z₀ = 0
z_{n+1} = (|Re z_n| + i|Im z_n|)² + c
```

The absolute-value fold before squaring is the only difference from the Mandelbrot
iteration; it mirrors the real and imaginary components into the positive quadrant
each step, creating the angular, flame-shaped tendrils.

## Smooth colouring

Discrete escape bands are eliminated via the standard smooth iteration formula:

```
nu = n − log₂(log₂|z_N|)
t  = nu / 256                   ← normalised to [0, 1]
```

`t` is then mapped through a 3-stop gradient:

| t range | from | to |
|---------|------|----|
| 0 → 0.3 | deep indigo `#0d0221` | amber `#e07b00` |
| 0.3 → 1 | amber `#e07b00` | pale cream `#fff8e7` |

Interior (non-escaping) points are rendered as near-black `#050008`.

## WebGL shader

All iteration and colouring runs in a GLSL fragment shader for interactive performance.
Key uniforms:

| Uniform | Type | Purpose |
|---------|------|---------|
| `uRes` | vec2 | canvas resolution in pixels |
| `uCenter` | vec2 | current complex-plane centre |
| `uScale` | float | half-height extent of the view in complex units |

The fragment-to-complex mapping (with y-axis flip so the ship appears upright):

```glsl
c = uCenter + (uv - 0.5) * uScale * vec2(aspectRatio, -1.0)
```

## Controls

- **Drag** — pan the view
- **Scroll** — zoom in/out
- **URL hash** — `#cx,cy,scale` encodes the current view for sharing

## Idle drift zoom

The default idle state slowly zooms toward a mast tip at approximately
Re ≈ −0.52, Im ≈ −0.62, multiplying `scale` by 0.998 per frame. When the zoom
exceeds 200× the initial scale the view resets to the classic full-ship overview.

## Files

- `index.html` — self-contained WebGL animation, no external dependencies
- `thumbnail.png` — 400×400 render of the classic full-ship view
- `generate_thumbnail.py` — Python script that produced thumbnail.png (stdlib only)
- `README.md` — this file
