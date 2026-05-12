# Two Truths Overlapping

Two families of concentric rings interfere per-pixel to produce a hypnotic **moiré** beating pattern. For every pixel the piece evaluates two sinusoidal ring functions

```
f1 = sin( √((x−cx1)² + (y−cy1)²) / λ )
f2 = sin( √((x−cx2)² + (y−cy2)²) / λ )
value = (f1 + f2) / 2
```

and writes the result directly into an `ImageData` buffer — no canvas drawing primitives are used. The buffer is 400 × 300 (half the display resolution) and upscaled to the viewport with `imageSmoothingEnabled = false`, halving the pixel budget while keeping edges sharp.

**Animation:** `cx2` orbits `cx1` on a 25-second circular path of radius 90 px, driven by `requestAnimationFrame`. As the centre offset rotates, the interference fringes (hyperbolic loci of constant `|r1 − r2|`) rotate and breathe. The wavelength λ oscillates slowly between 20 and 35 px on an incommensurate 27-second cycle so the pattern never quite repeats.

**Colour:** `value ∈ [−1, 1]` is mapped to hue via `hsl(value × 180 + 180, 40%, …)`, keeping saturation low enough that the optical intensity comes from the beating pattern rather than the colour. Lightness varies ±15 % with the amplitude for extra punch at the constructive maxima.
