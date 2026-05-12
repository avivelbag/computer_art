# Piece 42 — Circles Within Circles

A heart shape traced by a chain of 50 rotating circles, each spinning at a
different integer multiple of the base frequency. The path emerges entirely from
circular motion — no curve equations are evaluated during the animation itself.

## What is Fourier decomposition here?

The heart is sampled as 64 complex points (x + iy, one per equal step around
the parametric curve). The Discrete Fourier Transform decomposes this sequence
into 64 frequency components. Each component is a complex number whose magnitude
becomes the radius of an epicycle and whose argument becomes its starting angle.
Epicycle k rotates at exactly k times the base rate, so frequency 1 makes one
full revolution per loop, frequency 7 makes seven, and so on.

Chaining the circles tip-to-tail and summing their contributions reconstructs
the original signal exactly. The animation is the reconstruction playing out in
real time.

## Why do the circles produce the heart shape?

The heart parametric uses only four harmonics in each coordinate:

```
x = 16 sin³(t)     = 12 sin(t) − 4 sin(3t)
y = −(13 cos(t) − 5 cos(2t) − 2 cos(3t) − cos(4t))
```

So the DFT energy concentrates in fewer than ten coefficients. The largest
epicycle (frequency 1) sweeps out a wide arc that accounts for the overall
round shape; the next few sharpen the lobes and pull the bottom into a cusp.
All remaining circles are small corrective terms. Because all frequencies are
integers, after exactly one base period every circle has completed an integer
number of revolutions and the tip returns to its start — the path closes
without a gap.

## What makes it surprising

Hearts are not round. Their cusps and double lobes seem to require something
essentially non-circular to describe. Yet every feature — the indentation at
the top, the sharp point at the bottom — is produced by nothing more than
circles added together. Watching the chain fold and unfold to trace the cusp
reveals the mechanism: at that moment several fast-spinning small circles
briefly all point in the same direction, pulling the tip into a tight turn.

The first five epicycles alone produce a recognizable heart. Each additional
circle is a refinement — a smaller correction that sharpens a detail the
previous circles approximated. This layered convergence, from rough blob to
precise shape, is Fourier analysis made visible.

## Palette

| Role | Colour |
|---|---|
| Background | `#07070f` near-black navy |
| Circle strokes | `#2a58a0` muted cool blue |
| Arm lines | `#4488cc` lighter blue |
| Trace | `#00e5ff` bright cyan |

## Files

- `generate_thumbnail.py` — renders epicycles at t=π with partial trace as SVG
- `thumbnail.svg` — 400×400 px static preview
- `index.html` — canvas animation, self-contained, no external scripts

**Year:** 2026
