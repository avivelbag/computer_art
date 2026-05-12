# Brian's Brain — The Spark That Cannot Rest

Three-state cellular automata on a toroidal grid. Each cell obeys three simultaneous rules: an OFF cell ignites (turns ON) if exactly two of its eight Moore neighbours are currently ON; an ON cell immediately transitions to DYING; a DYING cell resets to OFF. These minimal rules spontaneously produce self-propagating glider patterns that race across the canvas indefinitely without any planted seed.

The grid is randomised on load at roughly 15 % ON and 15 % DYING density, which converges to dense glider swarms within a dozen generations. Cell size is auto-computed: 7 px per side, yielding approximately 137 × 86 cells on a 960 × 600 viewport. Click anywhere to restart with a new random seed. The grid wraps toroidally so gliders cross edges seamlessly.

**Palette:** background `#0f0f14` (near-black charcoal), ON state `#00e5cc` (electric teal), DYING state `#5a2d82` (deep violet). The contrast between the bright teal heads and the dimmer violet trails makes individual gliders trackable by eye.

**Implementation:** two `Uint8Array` buffers (current / next) swap each generation — no per-frame allocation. Toroidal wrap uses `(x + dx + cols) % cols`. The animation loop runs at approximately 25 fps via `setTimeout(loop, 40)`, slower than `requestAnimationFrame` so the grid is readable. Two separate `fillRect` passes (one per non-background state) avoid per-cell style changes.

Built with plain Canvas 2D API, no external libraries.
