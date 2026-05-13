# Piece 122 — Ink Dropped in Still Water: Paper Marbling

Turkish Ebru paper marbling rendered in a browser. Five stone (çiçek) drops build
a concentric-ring colour field; two comb (tarak) passes sweep it into swirling
bands. The build-up is animated — each drop and each rake pass appears in
sequence, then the final surface is held before the cycle restarts.

## Algorithm

### Stone drop (damlama)

A stone drop at centre (cx, cy) with radius R pushes all existing ink radially
outward while filling the vacated zone with new concentric colour rings.

**Forward map:** a point originally at distance r from the centre ends up at

```
r_new = r_old + R² / r_old
```

The minimum of r_new is 2R (achieved at r_old = R), so the circular region of
radius 2R around the centre is entirely new ink.

**Inverse warp (used for rendering):** to find the source for a destination
pixel at distance d:

- If d < 2R — the pixel is in the new-ring zone; its colour is determined by
  which concentric ring it falls in (alternating drop colour and background).
- If d ≥ 2R — solve r_new = r_old + R²/r_old for r_old:

  ```
  r_old = (d − √(d² − 4R²)) / 2
  ```

  The source is read from the original buffer at that radial distance.

### Comb / rake drag (taraklama)

A comb has N parallel tines. Each tine at position p₀ drags nearby pixels a
distance δ along the comb direction; influence falls off as:

```
displacement = δ · exp(−(dist_perp / σ)²)
```

where dist_perp is the perpendicular distance from the pixel to the tine path.
All tines act simultaneously — their displacements are summed before the
inverse warp is applied.

The horizontal rake uses alternating left/right tines, producing the wave
interference that characterises Turkish marbling. The vertical rake then pulls
all columns in the same direction for the final "feather" variation.

### Implementation

Both deformations use an inverse-warp approach: for each destination pixel, the
source coordinates in the previous buffer are computed, then sampled with
bilinear interpolation. A full copy of the buffer is taken at the start of each
pass so the read and write halves of the buffer don't interfere.

The JavaScript animation pre-computes eight ImageData keyframes
(blank → 5 drops → 2 comb passes) synchronously at startup, then cross-fades
between them using a simple 640K-pixel blend loop at 60 fps.

## Palette

| Role | Hex | Description |
|------|-----|-------------|
| Base | `#f2e6c8` | Warm cream |
| Drop 1 | `#c0522a` | Terracotta |
| Drop 2 | `#3a5fa8` | Cobalt |
| Drop 3 | `#e8a020` | Saffron |
| Drop 4 | `#2d6040` | Forest green |
| Drop 5 | `#963757` | Wine |

## Files

- `index.html` — self-contained canvas animation; no external dependencies
- `generate_thumbnail.py` — pure Python stdlib; writes `thumbnail.png`
- `thumbnail.png` — 400×400 PNG snapshot of the final marbled surface
- `README.md` — this file
