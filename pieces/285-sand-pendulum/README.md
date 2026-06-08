# The Sifting Hour — Sand Pendulum

A conical sand pendulum suspended above a dark umber surface. As it swings, it
scatters 35 grains per frame in a Gaussian cloud around the instantaneous tip
position. No canvas clear is ever called, so grains accumulate into a thickening
Lissajous trace — brightest along the densely-traced path, fading outward.

## Technique

- **Lissajous motion** — `x(t) = ax·cos(fx·t + φ)`, `y(t) = ay·sin(fy·t)`.
  Integer frequency ratios produce closed figures; near-integer produce open
  precessing curves.
- **Amplitude decay** — both amplitudes multiply by 0.9995 each frame, spiralling
  the trace inward over roughly 160 seconds.
- **Grain scatter** — each grain is offset from the tip by `|N(0, 2.2)|` pixels
  (polar Box-Muller) at a random angle, drawn as a 1×1 px `fillRect` with alpha
  0.08–0.13.  Density accumulates because `clearRect` is never called.
- **Hue shift** — inner grains lean warm ochre (r≈0 → rgb(245,220,150)),
  outer grains lean dusty rose (r≥5 → rgb(220,170,165)); controlled by the
  normalised grain radius.
- **Seamless loop** — when amplitude falls below 2 px a 60-frame overlay of
  semi-transparent umber dissolves the image; the piece then resets with the
  next frequency ratio from the curated list.

## Frequency ratios

| ratio | Lissajous type        | approx. cycle (DT=0.04, 60 fps) |
|-------|-----------------------|----------------------------------|
| 3 : 2 | trefoil-like closure  | 2.6 s                            |
| 4 : 3 | quatrefoil            | 2.6 s                            |
| 5 : 4 | five-pointed          | 2.6 s                            |
| 5 : 3 | wide asymmetric       | 2.1 s                            |
| 7 : 4 | seven-lobe            | 2.4 s                            |

## Palette

| element     | value                                  |
|-------------|----------------------------------------|
| background  | #1a0f06 (deep umber)                   |
| core grain  | rgb(245, 220, 150), α 0.13 (ochre)     |
| edge grain  | rgb(220, 170, 165), α 0.08 (dusty rose)|
