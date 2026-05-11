# Still Oscillating

A harmonograph simulation: two coupled pendulums drive a virtual XY pen plotter, tracing Lissajous-family curves that decay as the pendulums lose energy.

## Pendulum equations

```
x(t) = sin(f1·t + φ1)·e^(−d·t) + sin(f2·t + φ2)·e^(−d·t)
y(t) = sin(f3·t + φ3)·e^(−d·t) + sin(f4·t + φ4)·e^(−d·t)
```

Each pendulum pair shares a common decay constant `d = 0.0002`. At 3000 steps the
amplitude reaches `e^(−0.6) ≈ 0.55`, giving a dense layered trace before the canvas
fades and restarts.

## Frequency ratios

| Parameter | Base value | Perturbation per cycle |
|-----------|-----------|------------------------|
| f1 (x, pendulum A) | 2.001 | ±0.002 |
| f2 (x, pendulum B) | 3.001 | ±0.002 |
| f3 (y, pendulum A) | 1.001 | ±0.002 |
| f4 (y, pendulum B) | 2.001 | ±0.002 |

The near-integer ratios 2:3 (x) and 1:2 (y) produce a recognisable Lissajous
skeleton. The small irrational nudge (`.001`) prevents exact closure so the figure
drifts gracefully over each 25-second draw cycle. Phase offsets `φ = [0, π/2, π/4, 0]`
prevent degenerate straight-line figures.

## Visual approach

Thin strokes (`rgba(220, 200, 255, 0.15)`) on a near-black canvas (`#0a0a0f`).
Overdrawing at curve crossings builds luminous nodes naturally without blending code.
After 3000 steps the canvas dissolves with a slow semi-transparent overlay, then
restarts with slightly varied frequencies so consecutive loops never repeat.

**Technique:** HTML5 Canvas, harmonograph / Lissajous parametric equations  
**Year:** 2026
