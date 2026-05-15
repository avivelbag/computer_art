# Piece 156 — Wet Pigment: Watercolor Wash

Layered translucent polygon fills with edge distortion simulate the wet-on-wet look of watercolor painting. Every ~600–800 ms a new "stroke blob" appears: a base polygon of 8–12 slightly irregular vertices is recursively subdivided using midpoint displacement (4 levels deep, displacement halving each level), then that distorted outline is filled 25–40 times at 5–10 % opacity. Because each subdivision pass re-randomises the midpoints, successive layers never land in exactly the same place — pigment accumulates heaviest at the polygon edges, reproducing the characteristic bead effect of real watercolor where pigment flows to the drying boundary.

Three hue families drive the palette: warm reds/oranges (hue 5–45°), cool blues/teals (hue 190–240°), and earthy yellows/greens (hue 70–120°), all at 70 % saturation and 55 % lightness. Where blobs from different families overlap the browser blends their translucent fills, producing natural-looking secondary hues without any explicit colour-mixing logic.

After ~45 s the composition softly fades: a semi-opaque cream overlay is applied every frame over ~3 s until the canvas returns to bare paper, then a new composition begins.

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `thumbnail.svg` — static snapshot showing three overlapping wash regions
- `README.md` — this file
