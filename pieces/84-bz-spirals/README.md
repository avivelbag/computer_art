# Belousov-Zhabotinsky — Oscillating Spiral Waves

A discrete simulation of the Belousov-Zhabotinsky (BZ) chemical oscillator using the Greenberg-Hastings / Wiener-Rosenblueth cellular automaton on a 300 × 300 toroidal grid.

## The model

The real BZ reaction is an autocatalytic chemical oscillator: a reducing agent oxidises, changes colour, then slowly recovers — and the oxidation wave spreads autocatalytically through the medium. The discrete Greenberg-Hastings approximation captures this with three phases per cell:

- **Quiescent (state 0):** the resting medium, unable to react.
- **Excited (state 1):** the oxidation wavefront, lasting one tick.
- **Refractory (states 2–5):** four-tick inhibitory period; the cell cannot be re-excited until it returns to quiescent.

Transition rules, applied simultaneously every tick:

| Current state | Condition | Next state |
|---|---|---|
| Quiescent | ≥ 2 of 8 Moore neighbours are excited | Excited |
| Quiescent | < 2 excited neighbours | Quiescent |
| Excited | — | Refractory step 1 |
| Refractory step k < 4 | — | Refractory step k+1 |
| Refractory step 4 | — | Quiescent |

The threshold of two excited neighbours creates autocatalytic propagation: a wavefront advances into quiescent territory, while the refractory trail prevents the wave from folding back on itself. Random initial seeding creates broken wavefronts; each broken end curls inward under the threshold rule, nucleating a self-sustaining rotating spiral. The toroidal grid lets spirals cross edges without boundary artefacts.

## Palette

- **Quiescent:** `#0a0e1a` — deep navy, representing the resting chemical medium.
- **Excited:** `#00e5c0` — electric teal, the advancing oxidation front.
- **Refractory:** linear RGB gradient teal → `#c44b4b` (coral-red) over 4 sub-steps, representing the inhibitory decay period.

The teal-to-coral gradient makes individual spiral arms readable at a glance: bright teal marks the live wavefront, coral shows the refractory tail, and the deep navy background gives maximum contrast.

## Implementation

Two `Uint8Array` buffers (current / next) swap each generation — no per-frame allocation. Each state's RGBA colour is pre-computed into a flat lookup table at startup; rendering iterates cells and writes 2 × 2 pixel blocks directly into a `ImageData` buffer, flushed with a single `putImageData` call per frame. Animation runs via `requestAnimationFrame` (≤ 60 fps). Click anywhere to reseed from a new random state.

Built with plain Canvas 2D API, no external libraries.
