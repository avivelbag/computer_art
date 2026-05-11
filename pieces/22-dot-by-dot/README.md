# Dot by Dot the Light Falls

A halftone risograph print simulation. The canvas is divided into a 60 × 60 grid; at each cell the radius of a filled circle is determined by a damped radial ripple function evaluated at that cell's position. The result mimics two-colour riso printing: fluorescent coral ink on cream paper with a deep navy misregistration ghost offset by two pixels.

## Mathematics

The surface value at grid cell *(gx, gy)* with animation phase *φ* is:

```
nx  = (gx + 0.5) / 60 − 0.5
ny  = (gy + 0.5) / 60 − 0.5
r   = √(nx² + ny²) × π × 12
v   = (sin(r − φ) / (r + 1) + 1) / 2
dot radius = v × 4.8 px
```

`sin(r − φ) / (r + 1)` is a damped sinusoid: amplitude falls as 1/(r+1) with distance from the canvas centre, producing roughly **six concentric rings** from centre to edge. Subtracting a slowly increasing phase causes the rings to appear to expand outward, completing one full outward cycle every **8 seconds**.

## Palette

| Role | Colour | Hex |
|------|--------|-----|
| Background (paper) | cream | `#FAF3E0` |
| Foreground dots | fluorescent coral | `#FF6B6B` |
| Misregistration shadow | deep navy | `#1A1A2E` |

The navy shadow is drawn first at 35 % opacity, offset (+2 px, +2 px), then the coral dots are drawn on top. This two-pass approach replicates the slight ink mis-registration visible on real risograph prints.

## Implementation

Each animation frame:
1. Fill the canvas with the cream background.
2. Shadow pass: draw every grid dot in `#1A1A2E` at 35 % opacity, offset (+2, +2).
3. Dot pass: draw every grid dot in `#FF6B6B` at full opacity, centred on its cell.

Dots with radius < 0.4 px are skipped to avoid sub-pixel artefacts. The animation phase advances at 2π/8 rad s⁻¹ and wraps to [0, 2π). Frame delta is capped at 100 ms so backgrounded tabs don't burst on resume.

**Technique:** canvas / halftone grid / damped radial ripple / risograph  
**Year:** 2026
