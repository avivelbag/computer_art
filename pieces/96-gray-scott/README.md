# Piece 96 — Mitosis in Amber

A Gray-Scott reaction-diffusion simulation running on a 512×512 canvas. Two chemical species U and V interact through autocatalytic reaction and diffusion, self-organising from a small seeded patch into coral-like Turing patterns. The palette maps V concentration from near-black ground through warm amber filaments to ivory peaks.

## Gray-Scott Model

The governing equations are:

```
dU/dt = Du·∇²U  −  U·V²  +  F·(1−U)
dV/dt = Dv·∇²V  +  U·V²  −  (F+K)·V
```

U (the activator's substrate) is fed in continuously at rate F. V (the activator) autocatalytically converts U to V at rate U·V², and decays at rate (F+K)·V. The feed rate F and kill rate K together select which morphological mode the system settles into.

## Parameters

| Parameter | Value  | Role                                          |
|-----------|--------|-----------------------------------------------|
| F         | 0.0545 | Feed rate — replenishes U from the boundary   |
| K         | 0.062  | Kill rate — drains V beyond the feed          |
| Du        | 0.2097 | Diffusion coefficient for U                   |
| Dv        | 0.105  | Diffusion coefficient for V                   |

At these values the system lies in the coral/mitosis region of the Gray-Scott parameter space. Spots nucleate at the seeded center, grow into elongated fingers, then split repeatedly — a continuous self-similar division reminiscent of cell mitosis.

## Implementation

A double-buffered pair of `Float32Array` grids stores U and V for the current and next step. The Laplacian is a 5-point finite-difference stencil on a toroidal grid (wrap-around edges eliminate boundary artefacts):

```
∇²U[i] = U[left] + U[right] + U[up] + U[down] − 4·U[i]
```

Eight simulation steps run per animation frame inside `requestAnimationFrame`. A delta-time cap of 50 ms prevents a burst of steps when a backgrounded tab is foregrounded.

## Colour Palette

Three stops map V concentration to colour:

| Stop  | V range | Colour              | Hex      |
|-------|---------|---------------------|----------|
| 0     | 0.0     | near-black          | #0a0800  |
| 1     | 0.5     | warm amber          | #c8780a  |
| 2     | 1.0     | ivory               | #f5e6c3  |

Linear interpolation between adjacent stops; the transition point at V=0.5 places the amber glow at medium V concentrations, the filament shoulders of each coral branch.

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `thumbnail.svg` — static SVG preview in the amber palette
- `README.md` — this file
