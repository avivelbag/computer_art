# 238 — Curl Noise: The River That Doesn't Repeat

3 000 particles follow a divergence-free 2D curl-noise vector field, tracing the look of ink dropped in water. The velocity at each point is derived from a scalar potential **P(x, y, t)** via central finite differences:

```
vx = ∂P/∂y       vy = −∂P/∂x
```

Because the field is the curl of a potential, its divergence is identically zero — particles cannot pile up or drain. The underlying noise is 3D value noise sampled at **P(x·s, y·s, t·0.0003)**, where the slow third-axis drift shifts the flow continuously without jump cuts.

## Technique

- **True curl noise**: velocity derived from finite differences of a scalar potential, not a plain noise-angle field.
- **Trail fade**: each frame a semi-transparent dark fill (`rgba(10,0,16,0.03)`) is drawn over the canvas. The canvas is never fully cleared — trails accumulate then decay organically.
- **Torus topology**: particles that exit the canvas wrap to the opposite edge.
- **Color**: particles are colored by their instantaneous speed using a 3-stop gradient — deep violet `#2d0a50` → electric cyan `#00c8dc` → pale gold `#ffdc82`.

## Palette

| Stop | Color | Hex |
|------|-------|-----|
| 0 (slow) | Deep violet | `#2d0a50` |
| 0.5 (mid) | Electric cyan | `#00c8dc` |
| 1 (fast) | Pale gold | `#ffdc82` |

## Files

| File | Purpose |
|------|---------|
| `index.html` | Self-contained animation — no external dependencies |
| `generate_thumbnail.py` | Deterministic PNG thumbnail generator (stdlib only) |
| `thumbnail.png` | Pre-generated 400×250 thumbnail |
