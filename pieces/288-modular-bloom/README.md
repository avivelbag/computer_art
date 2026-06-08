# Modular Bloom — Times-Table Cardioids

200 points on a circle; each point i is connected to point (i×K mod 200) by a
chord. As K sweeps continuously from 2 to 50 the envelope of the 200 chords
morphs through every epicycloid family — cardioid at K=2, nephroid at K=3,
and an n-cusped form for each integer K — in a seamless rainbow loop.

## Technique

- **Modular multiplication** — for each integer i the target index is
  `round(i × K) mod N`, mapping each point to another point via the times-table.
  Using a real-valued K with `Math.round` gives crisp chord endpoints while still
  allowing smooth morphing as K advances.

- **Epicycloid envelopes** — at integer K the 200 chords are tangent to a
  (K−1)-cusped epicycloid: cardioid (1 cusp) at K=2, nephroid (2 cusps) at K=3,
  and so on up to K=50. The curve is never drawn explicitly; it emerges from the
  density of the chords.

- **Hue sweep** — the stroke colour is `hsla(H, 80%, 65%, 0.15)` where H tracks
  K linearly over the full 0–360° spectrum. Low opacity lets overlapping chords
  accumulate into luminous cusps while leaving inter-cusp regions dark.

- **Full canvas clear each frame** — no trail accumulation; the canvas is filled
  with `#0a0a0f` every frame so each snapshot shows only the current K value.

- **60 fps** — `requestAnimationFrame` is used directly; browsers cap the
  callback at the display refresh rate, which is typically 60 fps.

## Palette

| element    | colour      | hex / value          |
|------------|-------------|----------------------|
| background | near-black  | `#0a0a0f`            |
| chords     | rainbow     | `hsla(H,80%,65%,0.15)` — H tracks K |

## Parameters

| constant | value   | meaning                              |
|----------|---------|--------------------------------------|
| N        | 200     | number of points on the circle       |
| SPEED    | 3       | K units advanced per second          |
| K range  | 2 – 50  | cardioid through 49-cusped epicycloid |
| opacity  | 0.15    | per-chord stroke opacity             |

## References

- Nathaniel Bowditch / Jules Lissajous — harmonic analysis of circular motion.
- "Times Tables, Mandelbrot and the Heart of Mathematics" — Mathologer (YouTube 2015).
