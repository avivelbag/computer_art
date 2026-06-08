# Event Horizon — Accretion Disk

A WebGL fragment-shader simulation of a black hole accretion disk featuring relativistic Doppler colour-shifting and gravitational lensing.

Every pixel fires a ray from the camera. Rays passing close to the Schwarzschild radius are bent toward the disk plane by a first-order lensing deflection (α ∝ Rs / b², where b is the impact parameter). The bent ray is then projected onto the disk plane; if the intersection falls within the inner stable circular orbit (ISCO, r ≈ 1.5 Rs) and the outer disk radius the pixel is shaded as disk plasma.

Disk colour is determined by two competing physics:

- **Radial temperature** — a power-law profile T ∝ r⁻³/⁴ that reproduces the classic Shakura-Sunyaev thin-disk prediction: innermost orbits are hottest and emit white-blue light, outer orbits cool toward deep amber.
- **Doppler shifting** — Keplerian orbital speed v ∝ r⁻¹/² means the approaching side (left, sin φ > 0) is blue-shifted toward cyan/white, while the receding side (right, sin φ < 0) is red-shifted toward deep crimson and amber. The shift magnitude scales with local orbital velocity.

FBM (fractional Brownian motion) noise, advected by orbital phase and time, creates turbulent plasma filaments that swirl continuously. The event horizon itself is a pure-black circle; rays that terminate inside it contribute nothing. A soft vertical-thickness fade models the geometrically thin disk.
