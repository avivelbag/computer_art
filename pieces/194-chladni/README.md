# Chladni Figures — Nodal Lines of a Vibrating Plate

When a rigid square plate vibrates at one of its resonant frequencies, its surface displacement forms a standing wave described by f(x, y) = sin(m·πx)·sin(n·πy) — sand sprinkled on the plate migrates to the nodal lines where f = 0, tracing a Chladni figure for mode (m, n). This visualization computes |f| for every pixel: points where |f| ≈ 0 (the nodal lines) are rendered as bright sand-gold lines on a near-black background, with a white highlight at the narrowest nodal crossings, while the vibrating anti-nodal regions remain dark. Ten mode shapes cycle with smooth 1.5-second cross-fades, holding each figure for 2 seconds before transitioning to the next.

## How it works

The displacement field of a square plate vibrating in mode (m, n) is:

```
f(x, y) = sin(m·πx) · sin(n·πy)
```

Every pixel maps to (x, y) ∈ [0, 1]². Pixels where |f(x, y)| < threshold mark nodal lines where sand accumulates on a real plate; anti-nodes remain dark. A colour LUT maps proximity-to-zero to a sand-gold gradient with white highlights at crossings. The ten mode pairs cycle continuously with 1.5-second cross-fades and 2-second holds.

## What to notice

- Mode (m, n) and mode (n, m) produce mirror-image patterns rotated 90° — compare (2, 3) and (3, 2)
- The number of nodal line segments along each axis equals m − 1 horizontally and n − 1 vertically
- Real Chladni plates are driven at exactly these resonant frequencies with a violin bow; the physics is identical
