# DLA Crystal — Frost on Glass

Diffusion-Limited Aggregation grown from a single seed pixel at the canvas centre. Each step, a batch of random walkers spawns on a circle just outside the current cluster boundary and diffuses inward one pixel at a time in a random cardinal direction. When a walker lands adjacent to an already-frozen pixel it freezes in place, extending the aggregate. The result is a dendritic fractal — branching like frost on glass or a snowflake's growth edge — because the cluster tips intercept walkers first, starving concave interior regions of new particles.

**Color:** frozen-particle birth order maps to a perceptual gradient through HSL hue 200° (deep blue, seed) → 30° (warm amber, tips). The oldest particles at the cluster core are blue; the newest branch tips are copper-amber. This gives the piece a "time-lapse of crystallization" quality — you can read the growth history directly from the colors.

**Algorithm:** a `Uint8Array` occupancy grid (`600 × 600`) tracks frozen cells. A parallel `Uint16Array` records each cell's birth order for color mapping. An off-screen canvas receives `ImageData` pixel writes on every freeze event; the main canvas scales it to fill the viewport via `drawImage`. Color is precomputed into a 256-entry RGB lookup table so the per-freeze cost is three array reads.

**Adaptive batch:** walker count starts at 20/frame and grows with cluster radius (capped at 200). Each walker executes 20 diffusion steps per frame so the animation stays responsive at both small and large cluster sizes. Walkers that escape the cluster boundary (radius + 35 px) are discarded and replaced.

**Loop:** after 40 000 frozen particles the cluster occupies roughly 70 % of the simulation grid. A 2-second fade to white follows, then the grid resets and a new crystal begins growing from the same central seed.

**Interaction:** click anywhere to restart with a blank grid. The window also reinitialises on resize.

Built with plain Canvas 2D API and `requestAnimationFrame`. No external libraries.
