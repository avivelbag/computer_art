# Piece 300 — Stone Memory (Marble Veining)

Generative marble using layered turbulence noise fed through a sine distortion, producing
organic vein patterns that look convincingly geological.

## Noise algorithm

4-octave value noise is computed at each pixel.  A deterministic hash maps integer lattice
points to pseudo-random values in [0, 1]; bilinear (Hermite-smoothed) interpolation between
lattice corners gives the continuous noise field:

```glsl
float hash3(vec3 p) {
  p = fract(p * vec3(0.1031, 0.1030, 0.0973));
  p += dot(p, p.yxz + 33.33);
  return fract((p.x + p.y) * p.z);
}
```

Turbulence folds the centered noise with abs(), creating cusps that resemble mineral banding:

```
turbulence(p) = Σ_{i=0}^{3}  |noise(p · 2^i) − 0.5| · 0.5^i
```

## Vein formula

```glsl
float v = sin(uv.x * 3.0 + turbulence(vec3(uv * 4.0, uTime * 0.0003)) * 8.0);
```

The phase displacement by `turbulence * 8` stretches and folds the sine bands into sinuous,
branch-like veins.  Peaks of |v| near 1 mark the vein centrelines.

## Palette — Calacatta

| Role | Hex | RGB | GLSL vec3 |
|------|-----|-----|-----------|
| Base ivory | `#f5f0e8` | 245 240 232 | 0.961 0.941 0.910 |
| Primary vein | `#2a2520` | 42 37 32 | 0.165 0.145 0.125 |
| Secondary vein | `#9e8e7a` | 158 142 122 | 0.620 0.557 0.478 |

Blending:

```
secondary_weight = smoothstep(0.50, 0.70, |v|) · (1 − smoothstep(0.70, 0.85, |v|))
primary_weight   = smoothstep(0.85, 1.00, |v|)

color = mix(base, taupe,    secondary_weight × 0.7)
color = mix(color, charcoal, primary_weight)
```

## Animation

The turbulence is evaluated in 3D.  The third coordinate drifts as `z = uTime × 0.0003`,
where `uTime` is milliseconds since the animation started, giving z a rate of 0.3 units/second.
This makes the stone appear to breathe almost imperceptibly.

## Rendering

The primary path is a WebGL fragment shader — each pixel is independent so the GPU can
evaluate all 800 × 800 = 640 000 pixels in parallel.  If WebGL is unavailable the page
falls back to a CPU ImageData loop at 400 × 400 using the same formula in JavaScript.
Both paths cap frame rate at 60 fps with `requestAnimationFrame`.

## Files

- `index.html` — self-contained animation, no external dependencies
- `thumbnail.svg` — hand-drawn SVG approximating the marble vein aesthetic
- `README.md` — this file
