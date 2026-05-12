# String Art — The Curve Lives Between the Lines

Straight lines, drawn between numbered points on a circle, conspire to trace a curve that no single line contains. This is the "times tables on a circle" construction: connect point *i* to point *(i × m) mod N* for every *i*. As the integer multiplier *m* rises from 2, a cardioid emerges, then a nephroid, then a succession of stranger epicycloid families — all from nothing but straight chords.

## Technique

300 anchor points sit at equal angular intervals on a circle of radius 270 px. Each frame the real-valued multiplier

```
m = 2 + 48 × (0.5 + 0.5 × sin(t × 0.3))
```

oscillates smoothly between 2 and 50. For each anchor *i* the chord target is the real-valued index `j = (i × m) mod 300`; the landing coordinate is linearly interpolated between the two integer-indexed neighbours of *j*, so the geometry morphs without any discontinuous jump.

Each chord is stroked at `globalAlpha 0.35` so overlapping lines add luminosity at the densest parts of the envelope — the curve appears to glow even though it is never drawn directly.

## Mathematical note

The envelope visible in the resulting image is the *involute* of the parametric family of chords. When *m* is exactly the integer *k*, the envelope is an epicycloid with *(k − 1)* lobes:

- *m = 2* → cardioid (1 lobe)
- *m = 3* → nephroid (2 lobes)
- *m = 4* → three-cusped epicycloid
- and so on for higher integers

Between integers the envelope blurs into a transitional form, giving the animation its fluid quality. The piece loops seamlessly because the sin-based easing is periodic with no discontinuity at the wraparound.
