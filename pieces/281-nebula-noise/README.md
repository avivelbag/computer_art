# Piece 281 — Celestial Veil

A generative emission nebula rendered by compositing three layered Perlin-noise fields on an HTML5 canvas. Each layer represents a different ionised gas: ionized hydrogen (crimson), doubly-ionized oxygen (teal), and an ultraviolet violet haze. The three emission fields drift at different velocities and directions, creating a continuous parallax that gives the illusion of depth inside a gas cloud light-years across.

## Noise Architecture

The piece uses a classic 2D Perlin noise function built from a 512-entry permutation table and quintic fade curves. Three independent noise layers are defined:

| Layer | Ion / Process              | Colour          | Scale   | Octaves | Power |
|-------|----------------------------|-----------------|---------|---------|-------|
| 1     | Ionized hydrogen (Hα)      | `#c0103a` range | 0.0038  | 4       | 1.9   |
| 2     | Oxygen-III doublet (O III) | `#0aefb0` range | 0.0072  | 3       | 2.3   |
| 3     | UV violet haze             | `#a028dc` range | 0.0140  | 2       | 2.6   |

Each layer is computed into a separate `ImageData` buffer every frame, then drawn to the main canvas with `globalCompositeOperation = "lighter"` (additive blending). Additive blending means overlapping emission regions sum their colours, brightening where multiple gases co-exist — the same physics that makes real nebulae blaze white at their cores.

## Fractional Brownian Motion

Each layer uses *n* octaves of Perlin noise summed with geometrically decaying amplitudes (half-amplitude per octave, slightly more than double frequency with a lacunarity of 2.1 to avoid visible lattice alignment):

```
fbm(x, y, n) = Σᵢ noise(x·2.1ⁱ, y·2.1ⁱ) · 0.5^(i+1)
```

More octaves on the low-frequency layer (4) builds up the large cloud body structure; fewer octaves on the high-frequency layer (2) keeps the bright-knot detail crisp.

## Animation

`time` increments by 1 each frame. The per-layer drift is applied as:

```
nx = px · scale + time · ax · 0.0002
ny = py · scale + time · ay · 0.0002
```

With `ax` and `ay` differing per layer (layer 1 moves mostly right, layer 2 moves up-left, layer 3 moves diagonally down-right), the cloud drifts appear to move at different rates — parallax without a third spatial dimension. The speed constant `0.0002` makes a full noise cell traverse the canvas in roughly 83 seconds, keeping motion below the threshold of conscious perception; the nebula simply breathes.

## Brightness Shaping

After remapping the `fbm` output from `[-1, 1]` to `[0, 1]`, a power transform sharpens the luminance distribution:

```
v = clamp(fbm(...) * 0.65 + 0.5, 0, 1)^power
```

The coefficient `0.65` compresses the range so that roughly 20% of pixels sit at absolute black (the inter-nebular void) and only a small fraction reach full brightness (hot emission knots). The power (1.9 – 2.6 across layers) concentrates colour energy into cloud cores, leaving dark tendrils between them.

## Performance

The canvas is 300×300 pixels, CSS-scaled to `100vmin`. Total noise evaluations per frame: 300² × (4 + 3 + 2) = 810 000. The animation loop is throttled to 60 fps with a `ts - lastTs < 16` guard.

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `thumbnail.svg` — static SVG approximation using radial gradients and blur filters
- `README.md` — this file
