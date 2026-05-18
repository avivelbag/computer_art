# Hankin's Infinite Rose — Islamic Star Patterns

An animated canvas tiling that cross-fades between two symmetry families of Islamic geometric art: the 6-fold hexagonal family and the 8-fold square family. Both use star polygons in the Hankin tradition, where each tile is divided into a central star body and surrounding geometric fills.

## Symmetry Families

### 6-Fold (Hexagonal)

Each cell is a regular hexagon with circumradius 74 px. A 6-pointed star is centred on each hex, with outer tips aligned to the hex vertices. Six off-white triangular kite shapes fill the corners between the star tips and the hex boundary. The three-hex vertex gap (where hexes meet) is left in the background teal, creating the signature ring-and-triangle residual pattern of hexagonal girih work.

### 8-Fold (Square)

Each cell is a square with half-side 52 px. An 8-pointed star (regular star polygon with 8 outer tips and 8 inner notches) is centred on each square. Four off-white triangles sit at the four corner positions, between the diagonal star arms. The resulting residual — a cross-shaped dark channel between adjacent squares — is characteristic of the 8-fold girih family and appears in tilework from Isfahan, Marrakesh, and the Alhambra.

## Star Polygon Construction

Stars are parameterised as regular `n`-pointed star polygons:

```
for i in 0..n:
    outer_tip  = (R · cos(a + 2πi/n),  R · sin(a + 2πi/n))
    inner_notch = (r · cos(a + π/n + 2πi/n), r · sin(a + π/n + 2πi/n))
```

where `R` is the outer radius (tip distance from centre) and `r` is the inner notch radius. The ratio `r/R` controls how "fat" or "needle-thin" the star points are. The animation slowly oscillates this ratio between 0.38 and 0.62, morphing stars from sharp to broad continuously without any jump cut.

## Animation

Two independent animated layers are composited with `globalAlpha`:

- **Cross-fade**: a smooth hermite-eased sine wave cycles every 960 frames (≈ 16 seconds at 60 fps), ramping `alpha_6` from 1→0 and `alpha_8` from 0→1 and back, giving a seamless morph between the two families.
- **Star angle oscillation**: the inner notch radius oscillates via `sin(frame × 0.011)`, so stars breathe slowly even when a single family is fully opaque.
- **Slow rotation**: the entire tiling rotates at 0.00025 rad/frame (one full revolution every ≈ 69 minutes), eliminating any fixed boundary.

## Palette

| Role | Colour |
|---|---|
| Canvas background | `#081818` near-black teal |
| Tile fill | `#0d4040` deep teal |
| Star body | `#c8922a` warm gold |
| Corner fills | `#e8dfc0` off-white parchment |
| Tile separators | `#051010` near-black |

The palette references traditional Persian and Moroccan zellige tilework — lapis lazuli grounds with gilded star bosses.
