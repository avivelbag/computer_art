# 273 — The Grain of Light

A four-term plasma field is thresholded each frame against the 8×8 Bayer ordered-dithering matrix, converting a smoothly-varying grayscale field into a two-tone halftone that continuously breathes and morphs on near-black ground with sand-gold grain. The technique is the same one that gave 1980s low-bit-depth computer graphics their distinctive textured appearance.

## How it works

**Plasma.** Four cosine waves interfere to produce a scalar field in [0, 1]:

```
v(x, y, t) = 0.125 × (
    sin(3π · x/W + 0.7t)   +
    sin(4π · y/H + 0.5t)   +
    sin(5π · (x+y)/W + 0.3t) +
    sin(12π · r   + 0.9t)  +
    4
)
```

where `r = √((x/W − ½)² + (y/H − ½)²)` is the radial distance from the canvas centre. Each term contributes ±1 to the sum, so the parenthesised expression lies in [0, 8]; multiplying by 0.125 normalises to [0, 1].

**Bayer threshold.** For each pixel `(x, y)`, the 8×8 Bayer matrix supplies a fixed threshold `B[y mod 8][x mod 8] / 64 ∈ [0, 63/64)`. The pixel is drawn in sand gold if `v > B`, in near-black otherwise. Because the matrix entries are spatially ordered — not random — the resulting dots form diagonal stripes that self-organise into recognisable grid patterns at mid-densities, unlike noise-based stochastic dithering.

**Performance.** The horizontal term `sin(x/W · 3π + t)` and vertical term `sin(y/H · 4π + t)` are precomputed per frame into two `Float32Array` buffers of length 800. The diagonal term `sin((x+y)/W · 5π + t)` exploits `W = H`: since `x/W + y/H = (x+y)/W`, it is a function of `x + y` alone and precomputed into a 1599-element array. This reduces `Math.sin()` calls in the inner loop from four to one (only the radial term remains).

## Palette

| Role       | Colour     | Hex       |
|------------|------------|-----------|
| Background | Near-black | `#0d0d0d` |
| Grain      | Sand gold  | `#e8c97a` |

## Files

| File                   | Purpose                                             |
|------------------------|-----------------------------------------------------|
| `index.html`           | Self-contained animation — no external dependencies |
| `generate_thumbnail.py`| Deterministic PNG thumbnail generator (stdlib only) |
| `thumbnail.png`        | Pre-generated 400×400 thumbnail at t = 5 s          |
