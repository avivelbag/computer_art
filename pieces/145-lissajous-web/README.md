# Piece 145 — Frequencies in Resonance: Lissajous Web

A single Lissajous curve x = A·sin(aτ + δ), y = B·sin(bτ) is traced continuously on a
near-black canvas. The x-frequency `a` is held fixed at 3; the y-frequency `b` drifts
upward from 0.98 to 5.02 one small step per frame, then wraps back — cycling through
every near-integer ratio (1:1, 2:3, 3:4, 4:5 …) and the irrational gaps between them.

## Visual idea

At each integer or simple-fraction ratio the curve closes on itself and the path
accumulates into a dense, glowing knot. Between ratios it wanders open orbits that
gradually fill the canvas. The low stroke alpha (0.05) means density builds through
overlap: turning-point tangencies glow brightest, just as they do in real optical
interference patterns.

## Equations

```
x(τ) = A · sin(a · τ + δ)
y(τ) = B · sin(b · τ)
```

with a = 3, A = B = 270 px (canvas radius), and b drifting 0.98 → 5.02.

## Parameters

| Symbol | Value       | Notes                                    |
|--------|-------------|------------------------------------------|
| a      | 3           | x-frequency (fixed)                      |
| b      | 0.98 → 5.02 | y-frequency (drifts 0.00008 / frame)     |
| δ      | 0 → 2π      | phase offset (drifts 0.0001 / frame)     |
| τ step | 0.02        | parameter increment per frame            |
| Points | 200 / frame | path drawn in each requestAnimationFrame |
| α      | 0.05        | stroke alpha — accumulates glow          |
| Color  | HSLA hue    | mapped to fractional part of b/a         |

## Color

Hue = `((b / a) % 1) × 360°`. As b sweeps from ~1 to ~5, the hue cycles through the
full spectrum once per integer ratio, shifting continuously between. Saturation 80%,
lightness 70% keep every hue vivid against the `#08080f` background.

## Animation

- `requestAnimationFrame` at 60 fps.
- 200 curve points per frame; color and frequency advance every frame.
- When b exceeds 5.02 the canvas fades to background and b resets to 0.98 for a seamless
  loop — no hard cut, the viewer watches a new figure grow from the same dark ground.

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `thumbnail.svg` — static SVG of the 3:2 figure at δ = 0.5, six overlaid passes
- `README.md` — this file
