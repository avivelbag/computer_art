# Chladni Figures — Standing Waves Made Visible

Chladni figures are the nodal patterns that appear when a rigid plate vibrates at one of its resonant frequencies. Sprinkle sand on a metal plate, draw a violin bow along its edge, and the grains migrate to the stillest points — the nodal lines — forming intricate geometric patterns. This piece renders those patterns as glowing lines on a dark field.

## Technique

Each mode is described by two integers (m, n) and evaluated on a 600 × 600 pixel grid using the antisymmetric eigenmode function:

```
f(x, y) = cos(m·π·x)·cos(n·π·y) − cos(n·π·x)·cos(m·π·y)
```

where x and y are normalised to [−1, 1]. The zero set of f is the nodal pattern — the lines where a vibrating plate would be perfectly still.

Rendering uses the Canvas 2D `ImageData` API for per-pixel throughput. The computation exploits the separability of f: cosine arrays are precomputed once per axis (4·N trig calls) and combined with multiplications (2·N² ops), avoiding redundant 4·N² trig evaluations.

Each pixel's brightness is `max(0, 1 − |f| / threshold)`, giving a glow that peaks at the nodal line and falls off to the deep indigo background. A white-to-cyan colour ramp makes the nodal core brighter than its surrounding halo.

## Animation

The piece cycles through six mode pairs — (1,2), (2,3), (3,4), (3,5), (4,5), (2,5) — holding each for roughly four seconds before a one-second crossfade to the next. During a crossfade the brightness of each pixel is a weighted blend of the current and next mode tables, so the nodal lines morph rather than cut. The threshold pulses sinusoidally at 2 Hz with amplitude ±0.04, making the lines breathe as if the plate were still ringing.

## Mathematical note

The antisymmetric form guarantees f(y, x) = −f(x, y). This means the zero set is invariant under swapping x and y — equivalently, both diagonals y = x and y = −x always lie in the nodal pattern for any pair where m ≠ n. You can watch this invariant persist across every mode transition.
