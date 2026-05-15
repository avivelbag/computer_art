# Voronoi Stipple — Weighted Dot Etching

## Distinction from other Voronoi pieces in the gallery

Pieces 16 (*Light Through Cells*) and 127 (*Voronoi Mosaic*) are both **coloured-cell mosaics**: every pixel is flood-filled with a palette colour, and thin borders produce a stained-glass or tile effect. This piece is categorically different: the Voronoi diagram is never rendered as cells or outlines. Instead, Lloyd's algorithm is used purely as a **stipple engine** — the diagram exists only to redistribute seed points, and the final output is a field of variable-radius ink dots on paper (pen-plotter / copper-plate-etching aesthetic), with a single ink colour.

## Algorithm

A scalar density function ρ(x, y) is defined analytically as a sum of four 2-D Gaussians in normalised coordinates, producing a face-like ovoid: a large elliptical head, two eye peaks, and a mouth ridge. No raster images are loaded; all structure emerges from the mathematics.

Six hundred seed points are initialised via rejection sampling weighted by ρ so they start near their eventual converged positions. On each animation frame (capped at 30 fps) one Lloyd relaxation step runs:

1. A coarse 10-pixel spatial bucket grid is built from the current seed positions.
2. Every pixel of the 600 × 600 canvas is assigned to its nearest seed using a ±2-bucket neighbourhood scan (covers ±20 px, safely beyond the mean cell radius of ≈ 24 px).
3. Each seed moves to the density-weighted centroid of its Voronoi cell: x′ = Σ ρ(p)·p_x / Σ ρ(p).

After 45 iterations the seeds have converged and the animation holds on the final frame.

## Rendering

Each converged seed is drawn as a filled circle in warm charcoal (`#2b2318`) on an off-white paper background (`#f5f0e8`). The dot radius is proportional to the local density:

    r = RMIN + (RMAX − RMIN) × ρ(seed position)

with RMIN = 1 px and RMAX = 6 px. Dense regions (eyes, mouth, face interior) receive thick dots; the low-density periphery receives fine hairline dots — the classic pen-plotter stipple gradation.

## Palette

| Role       | Colour    | Hex       |
|------------|-----------|-----------|
| Paper      | Off-white | `#f5f0e8` |
| Ink        | Warm charcoal | `#2b2318` |

## Performance

The density map is pre-computed once into a `Float32Array(W×H)` so that per-pixel lookups during Lloyd iterations are O(1) array accesses, eliminating repeated `exp()` evaluations. The spatial grid reduces the nearest-seed search from O(N) to O(1) amortised. On a modern laptop the animation runs comfortably above 30 fps.
