# 271 — Sorted Light

A sinusoidal interference field is sorted column-by-column by brightness, collapsing the waveform into vertical strata that resemble liquid settling under gravity — then the sort reverses and the original pattern re-emerges.

## How it differs from related pieces

**31 — Glitch** uses scanline displacement, chromatic aberration, and block-copy corruption to simulate digital data damage. The effect is horizontal and feels random (though seeded). This piece performs a mathematically precise vertical sort — every column independently ordered by brightness, no displacement, no channel split.

**128 — Quasicrystal** and the wave-interference pieces also start from sinusoidal fields, but they do not modify the pixel order; their fields are static or phase-animated. Here the field is read once and then restructured by sorting, creating a fundamentally different spatial grammar: the horizontal frequency information of the source survives intact while the vertical ordering is entirely replaced.

## Technique

**Source field.** Three sinusoidal waves combine via interference:

```
value(x, y) = sin(nx·8π)·cos(ny·5π)·0.40
            + sin((nx+ny)·6π)·0.35
            + cos((nx−ny)·9π)·0.25
```

where `nx = x/800`, `ny = y/800`. The coefficients sum to 1.0, so the raw result lies in [−1, 1]; normalising to [0, 1] gives the brightness value used for both color mapping and sorting.

**Pixel sort.** Each column of 800 values is sorted descending independently using `Float32Array.prototype.sort`. Bright pixels rise to the top, dark ones sink — a vertical "gravity" collapse that reveals the column's brightness distribution as a gradient rather than a wave.

**Animation.** Four phases loop continuously:

| Phase | Action | Duration |
|-------|--------|----------|
| hold-source | Source image displayed | 90 frames |
| sorting | Sort front sweeps left → right, 4 columns/frame | ~200 frames |
| hold-sorted | Sorted image displayed | 90 frames |
| unsorting | Restore front sweeps left → right, 4 columns/frame | ~200 frames |

**Pre-computation.** Both `srcCols` and `sortedCols` are built once at startup from `Float32Array` buffers. The animation loop only reads and writes `ImageData` — no sorting occurs during playback.

## Palette

| Role | Color | Hex |
|------|-------|-----|
| Dark (value 0) | Deep navy | `#0a0a14` |
| Mid (value 0.5) | Electric violet | `#7c3aed` |
| Bright (value 1) | Amber gold | `#fbbf24` |

The three-stop gradient is a linear interpolation: dark→violet for the lower half of the brightness range, violet→gold for the upper half.

## Files

| File | Purpose |
|------|---------|
| `index.html` | Self-contained animation — no external dependencies |
| `generate_thumbnail.py` | Deterministic SVG thumbnail generator (stdlib only) |
| `thumbnail.svg` | Pre-generated 400×400 thumbnail (≈22 KB) |
