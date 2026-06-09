# Piece 299 — Complex Portrait (Domain Coloring)

Domain coloring maps every pixel in the complex plane to a color encoding
`arg f(z)` as hue and `|f(z)|` as brightness, producing vivid portraits where
zeros appear as rainbow spirals and poles as inverted spirals.

## Domain coloring formula

For each pixel at complex coordinate `z`:

```
fz  = f(z)
hue = (atan2(Im fz, Re fz) + π) / (2π)   ← 0..1, cycles once per 2π
bri = 0.5 + 0.5 · sin(2π · log₂|fz|)     ← isochromatic rings
sat = 0.85                                  ← fixed: vivid but not garish
RGB = hsv2rgb(hue, sat, bri)
```

The brightness formula `sin(2π·log₂|fz|)` produces concentric rings spaced
one octave apart in magnitude, making zeros (|fz|→0) and poles (|fz|→∞)
immediately recognisable as dense nested spirals.

## Curated functions

Three functions cycle automatically every ~7 seconds with a 1.5-second crossfade:

| ID | Formula | Visual character |
|----|---------|------------------|
| 0 | z³ − 1 | Three zeros at cube roots of unity; three 120°-symmetric rainbow petals |
| 1 | sin(z) | Periodic zeros along real axis; horizontal stripe structure |
| 2 | (z²+1)/(z²−1) | Zeros at ±i, poles at ±1; four-fold symmetry with bright poles |

## GLSL complex arithmetic

All complex arithmetic is implemented inline in the fragment shader — no external
libraries:

```glsl
vec2 cmul(vec2 a, vec2 b) { return vec2(a.x*b.x - a.y*b.y, a.x*b.y + a.y*b.x); }
vec2 cdiv(vec2 a, vec2 b) { float d = dot(b,b); return vec2(dot(a,b), a.y*b.x - a.x*b.y)/d; }
vec2 csin(vec2 z) { return vec2(sin(z.x)*cosh(z.y), cos(z.x)*sinh(z.y)); }
vec2 ccos(vec2 z) { return vec2(cos(z.x)*cosh(z.y), -sin(z.x)*sinh(z.y)); }
vec2 cexp(vec2 z) { return exp(z.x) * vec2(cos(z.y), sin(z.y)); }
```

## Controls

- **Drag** — pan the view
- **Scroll** — zoom in/out (default view covers Re/Im ∈ [−3, 3])
- **Click** — skip immediately to the next function

## Files

- `index.html` — self-contained WebGL animation, no external dependencies
- `thumbnail.png` — static 400×400 domain coloring of z³ − 1 at the default view
- `generate_thumbnail.py` — Python script that produced thumbnail.png (stdlib only)
- `README.md` — this file
