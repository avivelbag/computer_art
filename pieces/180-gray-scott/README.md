# Piece 180 — Chemical Dreams: Gray-Scott Mitosis

A Gray-Scott reaction-diffusion simulation in the **mitosis regime**, running on a 512×512 canvas.
Two chemical species U and V self-organise from a small seeded patch into a continuously
self-replicating population of circular spots that spontaneously divide into daughter spots.

**Sibling piece:** [Piece 96 — Mitosis in Amber](../96-gray-scott/) uses the coral regime
(F=0.0545, K=0.062) with a near-black/amber/ivory palette. This piece targets the true mitosis
regime (F=0.0367, K=0.0649) with a deep-indigo-to-electric-cyan gradient — a different
morphological class and a completely different colour family.

## Gray-Scott Model

The governing equations are:

```
dU/dt = Du·∇²U  −  U·V²  +  F·(1−U)
dV/dt = Dv·∇²V  +  U·V²  −  (F+K)·V
```

U (the substrate) is continuously replenished at feed rate F. V (the activator) autocatalytically
converts U at rate U·V², and decays at rate (F+K)·V.

## Parameters

| Parameter | Value  | Role                                          |
|-----------|--------|-----------------------------------------------|
| F         | 0.0367 | Feed rate — replenishes U from the boundary   |
| K         | 0.0649 | Kill rate — drains V beyond the feed          |
| Du        | 0.2100 | Diffusion coefficient for U                   |
| Dv        | 0.1050 | Diffusion coefficient for V                   |

At F=0.0367, K=0.0649 the system lies in the **mitosis** region of the Gray-Scott parameter
space. Spots grow to a critical radius, elongate, then split into two daughter spots. This
produces a self-replicating population that fills the canvas over time, reaching a dynamic
steady state with hundreds of slowly migrating spots.

## Implementation

Double-buffered `Float32Array` grids store U and V. The Laplacian uses a **9-point stencil**
including diagonal neighbors on a toroidal (wrap-around) grid:

```
∇²U[i] = 0.05·(NW + NE + SW + SE) + 0.20·(N + S + W + E) − U[i]
```

Ten simulation steps run per animation frame. A 50 ms delta-time cap prevents a burst of
steps when a backgrounded tab is foregrounded.

Rendering uses a precomputed 256-entry LUT (a `Uint32Array`) mapping V∈[0,1] to RGBA values.
Each frame the ImageData buffer is written as a `Uint32Array` view, storing four bytes per
pixel in a single 32-bit store for cache efficiency.

## Colour Palette

Two stops map V concentration to colour via linear interpolation through the LUT:

| Stop | V   | Colour         | Hex      |
|------|-----|----------------|----------|
| 0    | 0.0 | Deep indigo    | #1a0a2e  |
| 1    | 1.0 | Electric cyan  | #00e5ff  |

Low-V background appears as deep indigo space; high-V spot cores glow electric cyan with a
smooth gradient halo in between.

## What to notice

- Watch a spot elongate then pinch in two: this is the mitosis instability — once a spot exceeds a critical radius, curvature-driven diffusion splits it
- Spots strongly repel each other; after saturation the canvas holds a nearly uniform lattice of slowly drifting spots
- The system reaches a dynamic steady state where spontaneous splits and occasional mergers balance — the total spot count fluctuates but does not grow indefinitely

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `thumbnail.svg` — stylized SVG of the mitosis spot pattern in the indigo/cyan palette
- `README.md` — this file
