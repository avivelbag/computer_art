# The Land Before Memory — Contours of a Dreamed Terrain

A slowly drifting 3-D noise field is sampled onto a 120×90 grid every frame. Twelve evenly spaced height thresholds are extracted as isolines using the marching squares algorithm, then stroked in a geological color palette — deep indigo at sea level through teal, khaki, sand, and cream at the peaks. The noise time slice advances at ≈0.003 per frame so the contours flow like a time-lapse tidal map, hills rising and sinking without interruption.

## Technique

The noise function is 3-D value noise with smooth (quintic) interpolation, run through four octaves of fractal Brownian motion (fBm) to add fine-detail ridgelines on top of the large-scale hills.

Marching squares processes each 2×2 cell of the grid, classifies the four corner values against the current threshold (16 possible bit patterns), and draws the interpolated line segment for that case. Saddle cases (patterns 5 and 10) are disambiguated by the cell's average height. The 12 isolines are drawn in a single `beginPath`/`stroke` call per level, so there is no per-segment state-change overhead.

Every fifth isoline ("index contour") is drawn at 1.8 px instead of 0.8 px — the standard cartographic convention that helps the eye count elevation bands quickly.

## Parameters

- Grid: 120 × 90 nodes (one node every 10 px on a 1200 × 900 canvas)
- Noise: 4-octave fBm, spatial frequency 0.035, time increment ≈0.003 s⁻¹
- Levels: 12, thresholds evenly spaced in [0.15, 0.85]
- Palette: deep indigo → teal → olive → khaki → sand → cream
- Background: near-black (#0d0d0b)
