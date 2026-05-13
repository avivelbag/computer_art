# Piece 102 — Hyperbolic Tiling

A {5,4} tessellation (pentagons, four meeting at each vertex) rendered inside the Poincaré disk model of the hyperbolic plane. The viewpoint slowly rotates via a Möbius transform composed each frame, producing an Escher-like recursive symmetry that converges to the boundary circle.

## Poincaré Disk Model

The hyperbolic plane is mapped conformally into the open unit disk. Hyperbolic straight lines (geodesics) appear as arcs of Euclidean circles that meet the boundary circle at right angles. Distances expand toward the boundary: equal-area tiles shrink visually as they approach the unit circle.

## {5,4} Tiling

A {p,q} tiling has p-gons with q meeting at each vertex. The {5,4} tiling (pentagons, 4 per vertex) exists only in hyperbolic geometry because 4 × (1 - 2/5) = 8/5 > 2, so the angular defect forces the surface to be negatively curved. The circumradius of the fundamental pentagon is:

```
cosh(r) = cos(π/q) / sin(π/p)
```

which in Euclidean (Poincaré) coordinates is `R = tanh(r/2)`.

## Tile Generation

A BFS expands outward from the central tile. Each tile's P adjacent neighbors are reached by reflecting the tile's center through each hyperbolic edge midpoint — equivalent to composing two Möbius transforms (translate edge-midpoint to origin, negate, translate back). Tiles whose Euclidean circumradius in screen space falls below 0.5 px are culled to maintain 60 fps.

## Animation

A global rotation angle advances each frame. The central pentagon's orientation is set to this angle; all BFS-derived centers inherit the rotation because the BFS operates in the rotated frame. This produces continuous Möbius rotation of the entire tiling.

## Colour

| Element           | Colour                          |
|-------------------|---------------------------------|
| Background        | Deep indigo `#0a0818`           |
| Tile fill (amber) | `#c8790a`, `#e8a020`, `#b05a14` |
| Tile stroke       | Pale gold `#f5d070`             |
| Disk boundary     | Indigo `#4433aa`                |

The three amber tones cycle across tiles by `(colorIdx + k + 1) % 3` at each BFS step, creating a three-coloring that prevents adjacent tiles sharing the same hue.

## Performance

BFS terminates when a tile's Euclidean circumradius drops below 0.5 px. `MAX_DEPTH = 12` provides a hard cap. The canvas is drawn at native device size (100vmin × 100vmin) with no pixel-doubling needed.

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `thumbnail.svg` — static SVG preview of the disk pattern
- `README.md` — this file
