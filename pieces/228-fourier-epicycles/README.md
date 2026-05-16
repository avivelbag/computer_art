# Piece 228 — Fourier Epicycles: Draw Anything with Rotating Circles

An interactive canvas that decomposes any closed 2D path into a sum of rotating circles
(epicycles) via the Discrete Fourier Transform, then animates the reconstruction in real time.

## How it works

### DFT on a 2D path

Each closed path is sampled to N = 512 evenly-spaced points. Both coordinates are packed into
a single complex number: z[n] = x[n] + i·y[n]. The DFT is then:

```
X[k] = (1/N) Σₙ z[n] · e^(−i 2π k n / N)    for k = 0 … N−1
```

Each frequency component X[k] encodes:
- **|X[k]|** — epicycle radius (how big the kth circle is)
- **arg(X[k])** — starting angle (where on the circle the animation begins)
- **k** — rotation speed (k full revolutions per animation cycle)

Components are sorted by amplitude descending so adding harmonics one at a time always
includes the next most significant contribution first.

### Reconstruction (animation)

At animation time t ∈ [0, 2π) the tip position is:

```
x(t) + i·y(t)  =  Σₖ X[k] · e^(i k t)
               =  Σₖ |X[k]| · [cos(k·t + φₖ)  +  i·sin(k·t + φₖ)]
```

Each term draws one epicycle: a ring of radius |X[k]| rotates at speed k, offset by phase φₖ.
The tip of the last spoke traces the reconstructed path.

### Convergence

The DFT is exactly invertible: with all N harmonics the trace exactly reproduces the original
512-sample path. Restricting to the K largest amplitudes gives the best K-term L² approximation.
A heart curve converges visually around K ≈ 20; a square or sharp star needs K ≈ 60+ because
sharp corners require many high-frequency terms (Gibbs phenomenon).

## Algorithm details

- **Resampling**: input strokes are resampled to N_SAMPLES via arc-length parameterisation and
  linear interpolation, so the DFT sees uniformly-distributed samples regardless of drawing speed.
- **DFT**: naive O(N²) — fast enough for N = 512 (≈ 262 000 multiply-adds, < 30 ms in modern JS).
- **Fading tail**: tip positions stored in a ring buffer, rendered in 16 alpha-bucket batches
  to avoid one `ctx.stroke()` call per segment while still producing a smooth fade.
- **Animation**: `requestAnimationFrame` advances time proportional to `dt / PERIOD_MS · 2π`
  for frame-rate-independent looping at ≤ 60 fps.

## Controls

| Control | Effect |
|---------|--------|
| Harmonics − / + | Remove or add one frequency component; watch the approximation jump |
| Harmonics slider | Jump directly to any count from 1 to 512 |
| ♥ Heart | Load the parametric heart curve (16 sin³t, −13 cos t + …) |
| ∞ Figure-8 | Load the lemniscate of Bernoulli |
| ✏ Draw Path | Enter draw mode; drag to sketch a closed shape, release to compute |

## Palette

| Element | Colour |
|---------|--------|
| Background | `#060612` deep navy |
| Epicycle rings & spokes | `rgba(192,160,60,…)` gold |
| Traced path | `rgba(255,255,255,…)` white with fade |
| Tip dot | `#ff5555` coral |
