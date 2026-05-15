# Piece 151 — 2D Wave Equation: Interference Ripples

Each frame advances a 512×512 grid one time step using the leapfrog finite-difference scheme `next[i] = 2·curr[i] − prev[i] + r·∇²curr[i]`, where r = c²Δt²/Δx² = 0.24 sits below the 2D Courant stability bound of 0.5, keeping the simulation from growing unbounded. Three point sources at staggered grid positions pulse at different angular frequencies and initial phases, seeding circular wavefronts that travel outward, overlap, and produce constructive and destructive interference fringes whose intensity is mapped to a deep-navy-to-gold two-tone palette. When a wavefront reaches the grid edge (Dirichlet condition: u = 0 on all boundaries), it reflects back with inverted phase; these reflected waves then beat against the outgoing ones to lock certain grid positions into persistent standing-wave antinodes and nodes.

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `thumbnail.svg` — static snapshot showing the three-source ring motif
- `README.md` — this file
