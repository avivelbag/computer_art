# 272 — Pendulum Wave

Each of the 20 pendulums has a length chosen so it completes a whole number of full oscillations in exactly 60 seconds — the shortest completes 40 swings, the longest 59. Because the oscillation count differs by exactly one between adjacent pendulums, coherent wave patterns emerge, sweep through braids and spirals, then fully collapse back into synchrony at the 60-second mark. This phenomenon requires no external forcing or dissipation: it is pure simple harmonic motion where the integer-ratio constraint on period guarantees a mathematically exact seamless loop.

## Physics

Each pendulum `i` (i = 0..19) has period `T_i = T_gallery / (N_min + i)` where `T_gallery = 60 s` and `N_min = 40`. The corresponding physical length is `L_i = g·(T_i / 2π)²`, ranging from ~0.56 m (pendulum 0, slowest) to ~0.26 m (pendulum 19, fastest). The animation uses closed-form SHM — `x_i(t) = A·sin(2π·t / T_i)` — with no damping, so the loop is exact.

## Palette

Bobs are colour-mapped along a three-stop cool-to-warm gradient: indigo `hsl(260,80%,62%)` at index 0, transitioning through cyan at the midpoint, to amber gold `hsl(38,80%,62%)` at index 19. Background is near-black `#0d0d12`; strings are rendered at 10% white opacity to keep visual weight on the bobs.

## Files

| File | Purpose |
|------|---------|
| `index.html` | Self-contained animation — no external dependencies |
| `thumbnail.svg` | Pre-computed mid-cycle braid state at t = 8 s |
