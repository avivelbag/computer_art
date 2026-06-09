# Piece 03 — Liquid Color (Plasma Cosine Palette)

A demoscene plasma effect: four layered sine waves summed per pixel and mapped through an Inigo Quilez–style cosine palette, producing a seamlessly looping field of flowing color.

## Plasma formula

Each pixel at (px, py) at time t evaluates:

```
x = (px / W - 0.5) * 4
y = (py / H - 0.5) * 4
v = sin(x + t)
  + sin(y·0.7 + t·1.3)
  + sin((x+y)·0.5 + t·0.8)
  + sin(√(x²+y²)·0.9 − t·1.1)
n = (v + 4) / 8   ← normalized to [0, 1]
```

The four terms use different spatial frequencies and temporal speeds. The pattern is complex but every term is periodic in t, so the field never jumps.

## Cosine palette

Color lookup: RGB = a + b·cos(2π·(c·n + d))

| Name   | a               | b               | c               | d               |
|--------|-----------------|-----------------|-----------------|-----------------|
| lava   | (0.5, 0.1, 0.0) | (0.5, 0.4, 0.3) | (1.0, 1.0, 0.5) | (0.0, 0.2, 0.6) |
| arctic | (0.4, 0.5, 0.6) | (0.4, 0.4, 0.3) | (1.0, 1.0, 1.0) | (0.0, 0.1, 0.5) |

Clicking the palette button triggers a 60-frame (~1 s at 60 fps) crossfade by linearly interpolating all four vec3 parameters from their current interpolated state to the new target.

## Rendering

The animation writes into a 800×800 `ImageData` buffer (one `Uint8ClampedArray`) and calls `putImageData` each frame. `requestAnimationFrame` drives the loop; the browser naturally caps at the display refresh rate (≤ 60 fps).

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `thumbnail.svg` — static SVG preview in the lava palette
- `README.md` — this file
