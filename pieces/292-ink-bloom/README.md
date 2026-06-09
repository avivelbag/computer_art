# Ink Bloom

Dropped ink diffusing through still water — four colors injected at the
corners of a 256×256 fluid simulation, swirling endlessly without ever
settling.

## Algorithm

Jos Stam's stable-fluids solver runs each frame:

1. **Force/dye injection** — every 120 frames, one of four edge injection
   points emits a Gaussian blob of colored dye and a velocity impulse
   directed toward the canvas center.
2. **Diffuse velocity** — viscous diffusion via Gauss-Seidel (`lin_solve`,
   8 iterations).
3. **Project** — Helmholtz decomposition enforces incompressibility;
   divergence is driven to zero via the same iterative solver.
4. **Advect velocity** — semi-Lagrangian back-trace through the current
   velocity field (unconditionally stable regardless of time step).
5. **Project again** — second projection pass cleans up advection-induced
   divergence.
6. **Diffuse + advect each dye channel** — four independent scalar fields,
   one per ink color, each diffused and advected by the same velocity.

The solver uses a flat `(N+2)²` 1D array per field with explicit boundary
conditions (reflecting walls for velocity, zero-gradient for density).

## Rendering

Each pixel samples all four dye channels and accumulates their colors
additively. `ImageData` writes the pixel buffer directly, bypassing the
compositing pipeline for maximum throughput.

## Colors

| Ink | Hex | Injection corner |
|-----|-----|------------------|
| Deep violet | `#3a0066` | top-left |
| Cobalt | `#1040c0` | top-right |
| Rose | `#c02060` | bottom-left |
| Amber | `#d08000` | bottom-right |

## Performance

Grid size 256×256 with 8 Gauss-Seidel iterations runs comfortably at 60 fps
on a modern laptop. The solver is ~200 lines of plain JavaScript with no
external libraries.
