# Density Wave — Galactic Spiral

5 500 star particles orbit a simulated galactic disk under a flat rotation curve
while three logarithmic spiral arms rotate as a density wave, continuously
modulating the brightness of every star that passes through them.

## Technique

- **Logarithmic spiral arms** — each arm follows r = A·e^(B·θ) with A = 14 px,
  B = 0.22, spanning 2.4 full turns from galactic centre to rim.  Three arms are
  evenly offset by 2π/3 radians.

- **Flat rotation curve** — every star orbits at a fixed tangential speed V_c
  (constant regardless of radius), so angular velocity ω = V_c / r: inner stars
  orbit faster than outer stars.

- **Density wave** — the spiral arm pattern rotates at a slower angular rate
  Ω_p < ω for all disk stars, so stars continually pass through the arms.  Each
  star's displayed brightness is modulated by a Gaussian proximity kernel
  exp(−Δθ² / 2σ²), where Δθ is the angular distance to the nearest arm locus at
  that radius.  Stars at the arm centre are fully bright; stars between arms dim
  to ~15 % of their base brightness.

- **Initial arm bias** — 74 % of stars are placed with a Gaussian scatter
  (σ = 0.32 rad) around the arm loci at t = 0, matching the density enhancement
  expected from the density wave slowing orbital motion near the arm.

- **Galactic core** — a radial gradient blob from near-white through warm amber
  (#f5a623) to transparent represents the nuclear bulge.

- **Arm glow** — faint wide strokes rendered in screen mode trace the rotating
  arm spines, providing a subtle ionised-gas glow on top of the star field.

- **TypedArray rendering** — all star positions are stored as `Float32Array` /
  `Uint8Array` columns; each frame clears the 800 × 800 `ImageData` buffer and
  writes each star as one (or five, for giant stars) pixels with additive
  blending, then `putImageData()` writes the buffer.  `Math.log(r/A)/B` is
  precomputed per star so the per-frame arm-proximity loop avoids any log() calls.

## Palette

| element            | colour            | hex       |
|--------------------|-------------------|-----------|
| background         | deep space black  | `#04040c` |
| main-sequence star | blue-white        | `#f0f4ff` |
| giant star         | pure white        | `#ffffff` |
| ionised gas (HII)  | teal              | `#80dcdc` |
| nuclear bulge peak | warm white        | `#fffcf0` |
| bulge mid          | amber             | `#f5a623` |

## Parameters

| constant  | value     | meaning                                          |
|-----------|-----------|--------------------------------------------------|
| N         | 5 500     | total star count                                 |
| ARMS      | 3         | number of spiral arms                            |
| A         | 14 px     | spiral scale (inner radius at θ = 0)            |
| B         | 0.22      | spiral pitch (winding tightness)                |
| VC        | 0.038 px/frame | flat rotation curve speed                  |
| OMEGA_P   | 1×10⁻⁴ rad/frame | arm pattern rotation speed             |
| σ (arm)   | 0.32 rad  | arm half-width for Gaussian proximity            |

## References

- Lin & Shu (1964). *On the Spiral Structure of Disk Galaxies.* ApJ 140, 646.
- Binney & Tremaine (2008). *Galactic Dynamics*, Chapter 6.
