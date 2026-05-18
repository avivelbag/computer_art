# 247 — Smooth Life: The Creature That Has No Name

SmoothLife is a continuous-space, continuous-state generalization of Conway's Game of Life introduced by Stephan Rafler in 2011. Where Life operates on a discrete binary grid, SmoothLife uses floating-point states in [0,1] and circular neighborhood kernels, producing slow undulating organisms that feel genuinely alive.

## The Rule

For each cell position (cx, cy), two neighborhood density averages are computed:

- **n** — inner average over a disk of radius r_i = 3 (the "inner neighborhood")
- **m** — outer average over the annulus r_i < r < r_o = 6 (the "outer neighborhood")

These are combined via a birth/survival function built from logistic sigmoids:

```
σ₁(x, a, α)     = 1 / (1 + exp(−4/α × (x − a)))
σ₂(x, a, b, α)  = σ₁(x,a,α) × (1 − σ₁(x,b,α))

birthLo = σ₁(m, b₁=0.278, α_m=0.147)
birthHi = σ₁(m, b₂=0.365, α_m=0.147)
deathLo = σ₁(m, d₁=0.267, α_m=0.147)
deathHi = σ₁(m, d₂=0.445, α_m=0.147)

s = σ₂(n, birthLo, birthHi, α_n=0.028) × (1 − σ₂(n, deathLo, deathHi, α_n))
  + σ₂(n, deathLo, deathHi, α_n)

next = clamp(2s − 1 + 0.9 × cur, 0, 1)
```

The damping term `0.9 × cur` means cells don't snap instantly to their target state — structures drift and reform rather than blinking in and out.

## Initialization

A 20×20 random patch of values in [0.1, 0.5] is placed at the center of a zero-filled grid. Within 50–100 frames the patch self-organizes into traveling blobs, rings, and other persistent structures that spread across the canvas.

## Color Mapping

| State | Color |
|-------|-------|
| 0.0 | near-black `#050508` |
| 0.5 | deep violet `#7b3fff` |
| 1.0 | bright cyan/white `#00e8d6 → #ffffff` |

A 256-entry RGBA LUT is precomputed at startup for O(1) per-pixel coloring.

## Implementation

The simulation uses two `Float32Array` buffers (current/next) on a logical grid of ~128×128 cells, rendered at 4× zoom via `image-rendering: pixelated` for the pixelated alien aesthetic. Boundary conditions are toroidal (periodic wrap). The convolution kernels (inner disk and outer annulus offsets) are precomputed once and stored as flat integer arrays.

## Controls

| Control | Function |
|---------|----------|
| Pause / Play | Toggle animation |
| Step | Advance one generation |
| Reset | Re-seed a fresh central patch |
| Splash | Add several random patches across the grid |
| Speed | Steps per second (1–20) |
| Zoom | Grid cell size in CSS pixels (2–8) |
| Click/drag | Paint live cells onto the grid |

## Files

| File | Purpose |
|------|---------|
| `index.html` | Self-contained simulation — no external dependencies |
| `thumbnail.svg` | Static thumbnail |
| `README.md` | This file |

## References

Rafler, S. (2011). *Generalization of Conway's "Game of Life" to a continuous domain — SmoothLife*. arXiv:1111.1567.
