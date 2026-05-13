# Piece 101 — SDF Metaballs

Eight metaball blobs travel on quasi-periodic Lissajous paths and merge organically. The scene is rendered pixel-by-pixel into a 300×300 ImageData buffer each frame, then upscaled to fill the viewport by the browser's CSS scaling engine.

## Signed-Distance Field Approach

Rather than tracing implicit surfaces in 3D, this piece evaluates a 2D potential field:

```
field(x, y) = Σ  r_i / dist(pixel, center_i)
```

A pixel is inside the blobscape when `field > threshold` (threshold = 1.0). Because the contributions add, two nearby balls whose individual contributions each reach ~0.5 at an in-between point will sum to 1.0 there, smoothly bridging the gap — the classic metaball merge.

## Motion

Each ball follows an independent Lissajous-like path:

```
x(t) = (cx + ax · sin(fx · t + φx)) · W
y(t) = (cy + ay · sin(fy · t + φy)) · H
```

The eight pairs of frequencies are drawn from {1, √2, √3, φ, 1.3, 1.5, 1.7, φ√2}, ensuring no two balls share a frequency. Because all ratios are irrational, no Lissajous path ever closes; the blobs drift endlessly without repeating a configuration.

## Colour

| Region                | Colour                         |
|-----------------------|--------------------------------|
| Core (high field)     | Deep violet `#1c0050`          |
| Edge (at iso-surface) | Cyan `#00dcdc`                 |
| Specular highlight    | Near-white cyan, upper-left lit|
| Outside glow          | Near-black with faint violet   |

The interior gradient maps `inner = (field − threshold) / threshold` from 0 (at the iso-surface) to 1 (one threshold-unit deeper). Red, green, and blue channels interpolate linearly between the edge and core colours.

## Specular Highlight

The finite-difference gradient of the field approximates the iso-surface normal:

```
∇field ≈ (field(x+ε, y) − field(x−ε, y),
           field(x, y+ε) − field(x, y−ε)) / 2ε
```

Because the field increases toward ball centres, `∇field` points inward; the outward normal is `−∇field / |∇field|`. Dot-product with a fixed upper-left light direction `(−0.707, −0.707)` gives `N·L = 0.707·nx + 0.707·ny`. A cubic falloff sharpens the highlight, and a boundary-proximity factor `(1 − inner / 0.3)` restricts it to a thin ring at the iso-surface edge.

## Performance

The pixel grid is 300×300. Gradient evaluations are skipped for pixels deeper than 30% inside the blob, reducing the gradient computation to the boundary band only. The canvas element is sized at 300×300 in HTML and scaled to `100vmin × 100vmin` in CSS with `image-rendering: pixelated` for crisp, zero-cost upscaling.

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `thumbnail.svg` — static SVG preview showing merged blobs
- `README.md` — this file
