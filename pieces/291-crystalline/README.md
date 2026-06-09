# Crystalline

A snowflake grown by diffusion-limited aggregation on a hexagonal grid, with
strict 6-fold rotational and reflective symmetry enforced at every growth step.

## Algorithm

The simulation maintains a `frozen` set of occupied hex cells in axial
coordinates (q, r). Each animation frame:

1. **Spawn** up to 80 random-walk particles on a circle just beyond the current
   cluster radius.
2. **Walk** each particle on the hex grid (up to 30 steps per frame) until it
   either neighbours a frozen cell or escapes the kill radius.
3. **Freeze**: when a particle sticks at (q, r), all 12 cells in its D6
   symmetry orbit are frozen simultaneously — this is the mechanism that
   produces the six-armed symmetric snowflake.

The 12 symmetry operations are the elements of the dihedral group D6:
six 60° rotations R^k and six reflected variants R^k ∘ S, where the
reflection S maps (q, r) → (q, −q−r) in axial coordinates.

## Hex Grid

Pointy-top hexagons in axial (q, r) coordinates:

- Pixel coordinates: `px = cx + size·(√3·q + √3/2·r)`, `py = cy + size·3/2·r`
- Hex distance: `max(|q|, |r|, |q+r|)` (Chebyshev in cube coords)
- Six neighbors: (±1, 0), (0, ±1), (±1, ∓1)

## Visual Encoding

- Background: `#080c18` (deep indigo-black)
- Crystal colour: `rgba(222, 238, 255, α)` — pure `#deeeff` at varying opacity
- Opacity encodes distance from centre: core cells 40 % opaque (appear dim),
  tip cells 100 % opaque (appear brightest)

## Animation

The flake grows from a single seed until it reaches hex radius 38 (≈ 90 % of
the 300 px canvas half-width at 4 px/cell). It then fades to `#080c18` and
a fresh seed begins, creating a seamless loop.
