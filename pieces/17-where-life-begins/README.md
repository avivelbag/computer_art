# Where Life Begins

Reaction-diffusion is a mathematical model of two chemicals that simultaneously spread through a medium and transform each other: species U fuels an autocatalytic reaction that produces V, while V is gradually removed by a kill term. The Gray-Scott variant of these equations spontaneously generates Turing patterns — spots, stripes, and coral-like labyrinths — from a uniform initial state disturbed by a tiny seed. This piece uses feed rate **F = 0.0545** and kill rate **K = 0.062**, parameters known to produce branching coral-like structures, seeded from a single 24 × 24 square of V at the canvas centre.

## Implementation

The simulation runs on a **512 × 512** flat `Float32Array` ping-pong pair (`u[]` / `v[]`). Each animation frame advances the system **10 discrete steps** using a 5-point finite-difference Laplacian on a toroidal (wrap-around) grid, then writes pixel colours directly via `putImageData`. The canvas is CSS-scaled to fill the viewport so the logical simulation resolution stays at 512 × 512 regardless of screen size.

## Palette

Three colours committed as JS constants map V concentration to colour via a 3-stop linear lerp:

| Stop | Colour | Hex |
|------|--------|-----|
| V ≈ 0 (background) | charcoal | `#1c2126` |
| V ≈ 0.5 (transition) | deep teal | `#0d4f6e` |
| V ≈ 1 (pattern peak) | warm cream | `#e8d5a0` |

**Technique:** canvas / reaction-diffusion / Gray-Scott  
**Year:** 2026
