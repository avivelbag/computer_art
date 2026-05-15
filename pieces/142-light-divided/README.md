# Light Divided

~400 random seed points triangulated by the Bowyer-Watson algorithm into a
stained-glass mosaic. Each triangle is a facet of quiet light, colored rose
through amber to slate by its centroid's position along the canvas diagonal.

## Algorithm — Bowyer-Watson

Bowyer-Watson is an incremental insertion algorithm for Delaunay triangulation:

1. **Super-triangle**: Start with a single enormous triangle whose circumcircle
   contains every seed point.
2. **Insert each point**: Find all "bad" triangles — triangles whose
   circumcircle strictly contains the new point (the Delaunay in-circle test).
3. **Cavity boundary**: Collect edges on the boundary of the cavity formed by
   removing the bad triangles. An edge is a boundary edge iff it belongs to
   exactly one bad triangle.
4. **Re-triangulate**: Connect the new point to every boundary edge, sealing
   the cavity with new triangles that satisfy the Delaunay property.
5. **Strip super-triangle**: After all points are inserted, discard any
   triangle that shares a vertex with the original super-triangle.

This produces the unique triangulation maximising the minimum angle across all
triangles — the Delaunay criterion — which is why the mosaic tiles look regular
and organic rather than slivered.

## Color mapping

Each triangle is coloured by its centroid's diagonal parameter:

```
t = (centroid_x / width + centroid_y / height) / 2
t += Gaussian(0, 0.04)   # organic jitter
```

`t` is then lerped through three RGB stops:

| Stop  | t   | Color   | Hex approx  |
|-------|-----|---------|-------------|
| Rose  | 0.0 | warm pink  | `rgb(220,100,130)` |
| Amber | 0.5 | golden ochre | `rgb(210,148,55)` |
| Slate | 1.0 | cool blue-grey | `rgb(90,110,145)` |

Triangles near the top-left are rose; those near the bottom-right shade toward
slate; the diagonal band passing through the center glows amber.

## Stroke

Each polygon carries a 0.5 px stroke in near-black `#1a1214` — the "lead came"
line that gives stained glass its structural look without overwhelming the color.

## Reproducibility

`piece.svg` and `thumbnail.svg` are fully static; regenerate them at any time:

```
python3 generate.py
```

`generate.py` uses only the Python standard library (`math`, `pathlib`,
`random`). No NumPy, no SciPy, no external dependencies.

**Year:** 2026
