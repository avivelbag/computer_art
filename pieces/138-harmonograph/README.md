# Piece 138 — Harmonograph: Four Pendulums, One Stroke

A **bilateral lateral harmonograph** — both the x-axis and y-axis are each driven by
two independent damped pendulums, producing a more complex figure than a classic
single-axis harmonograph.

## How it differs from Piece 80

Piece 80 (`80-harmonograph`) uses two pendulums on the x-axis but only **one** on the
y-axis, plus `globalAlpha 0.6` and a tapering line width. This piece uses the full
bilateral form (two pendulums on each axis), constant thin stroke, and low alpha (0.15)
so density accumulates purely through overlapping passes — the aesthetic is a
pen-plotter trace rather than a glowing ribbon.

## Equations

```
x(t) = A1·sin(f1·t + φ1)·exp(−d1·t)  +  A2·sin(f2·t + φ2)·exp(−d2·t)
y(t) = A3·sin(f3·t + φ3)·exp(−d3·t)  +  A4·sin(f4·t + φ4)·exp(−d4·t)
```

## Parameters

| Symbol | Value            | Notes                       |
|--------|------------------|-----------------------------|
| A1, A2 | 1.0, 1.0         | x-pendulum amplitudes       |
| f1, f2 | 2.0, 3.0         | x-pendulum frequencies (2:3 ratio) |
| φ1, φ2 | 0, π/4           | x phase offsets             |
| d1, d2 | 0.002, 0.002     | x damping constants         |
| A3, A4 | 1.0, 1.0         | y-pendulum amplitudes       |
| f3, f4 | 3.0, 2.0         | y-pendulum frequencies (3:2 ratio, inverted x) |
| φ3, φ4 | π/6, π/2         | y phase offsets             |
| d3, d4 | 0.002, 0.002     | y damping constants         |
| SCALE  | 140 px/unit      | canvas mapping              |
| α      | 0.15             | stroke alpha                |
| DT     | 0.01             | integration time step       |
| T_MAX  | 400              | total time (damping makes trace invisible past this) |

The x-axis ratio f1:f2 = 2:3 and y-axis ratio f3:f4 = 3:2 are inverted mirrors of each
other. Combined with the phase offsets (φ2−φ1 = π/4, φ4−φ3 = π/3), the figure traces a
**near-closed compound Lissajous** — the 6-fold symmetry of 2×3 and 3×2 creates a
complex web that the viewer watches emerge stroke by stroke before the damping spirals
it to a resting point.

## Animation

- 40 000 integration steps drawn at 200 steps per frame (~33 seconds at 60 fps).
- Stroke color: `rgba(160, 210, 255, 0.15)` — cool steel-blue on deep navy `#0a0a14`.
- After the curve completes it pauses 1.5 s then replays from the beginning.

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `thumbnail.svg` — static SVG of the full curve after damping decay
- `README.md` — this file
