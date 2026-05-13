# Piece 87 — Phyllotaxis: The Angle the Sunflower Chose

Sunflowers, pine cones, and daisy heads all pack their seeds using the same placement rule: each new seed is placed at exactly the golden angle from the previous one, at a distance proportional to the square root of its index. This produces the densest possible packing with no visible radial spokes.

## The Golden Angle

The golden angle is derived from the golden ratio φ = (1 + √5) / 2 ≈ 1.618:

    golden angle = 2π / φ² ≈ 2.39996 rad ≈ 137.508°

It is the smaller of the two angles formed when a circle is divided in the golden ratio.

## The Fermat Spiral Formula

Each seed *n* (counting from the centre) is placed at:

    r = c · √n            (radius — square-root spacing gives uniform area per seed)
    θ = n · golden_angle  (angle — stepped by the golden angle each time)

where *c* is a scale constant.

## Why the Golden Angle Avoids Spokes

Because the golden ratio is the *most irrational* number — its continued-fraction expansion [1; 1, 1, 1, …] converges more slowly to any rational approximation than any other real number — seeds placed at the golden angle never align into visible radial columns. Any other angle, being closer to some rational fraction *p/q* of the full circle, causes seeds to line up into *q* radial spokes or *p* spiral arms. The irrational nature of φ guarantees that no such resonance ever occurs, producing the maximally dense, spoke-free packing seen in nature.

The animation demonstrates this directly: as the placement angle morphs ±10° away from the golden angle, the dense cloud of seeds collapses into visible spokes. When the angle returns to 137.508°, the packing recovers.

## Animation

1. **Growing phase** (~25 s at 60 fps): 1 500 seeds appear one per frame from the centre outward, placed at the golden angle.
2. **Morphing phase** (~8 s): the placement angle oscillates from golden_angle + 10° back through golden_angle to golden_angle − 10° and returns, making the spoke structure appear and dissolve. The full oscillation uses sin(t · 2π) so both ±10° deviations are shown.
3. The cycle restarts.

## Palette

Dot colour encodes distance from the centre: saffron (#F5A623) at the centre, copper (#C0562A) at mid-radius, and dark rust (#501400) at the edge, on a near-black ground (#1a0800). Dot size also decreases with radius, echoing the smaller seeds found at the periphery of a real sunflower.

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `thumbnail.svg` — static SVG preview of ~300 golden-angle seeds
- `generate_thumbnail.py` — Python script that produced `thumbnail.svg`
- `README.md` — this file
