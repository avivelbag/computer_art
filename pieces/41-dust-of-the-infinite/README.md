# Piece 41 — Dust of the Infinite

A Clifford strange attractor plotted by iterating two coupled recurrence equations
2 million times. Each point is binned into one pixel of an 800×800 accumulation
buffer; bin counts are logarithmically normalised and mapped to a warm
amber-to-rose gradient, making density structure visible as a glowing fractal dust.

## Equations

```
x′ = sin(a · y) + c · cos(a · x)
y′ = sin(b · x) + d · cos(b · y)
```

Parameters: **a = −1.4, b = 1.6, c = 1.0, d = 0.7** — fixed values that produce
a rich butterfly shape with fine filaments and a visible central void.

## Technique

1. **Accumulation buffer**: a `Float32Array` of 800×800 cells counts how many
   attractor points land in each pixel — no canvas alpha compositing.
2. **Logarithmic density mapping**: `t = log(count + 1) / log(max + 1)` compresses
   the wide range of hit counts so both sparse filaments and dense cores are visible.
3. **Gamma compression**: `t^0.3` shifts the colour mapping so faint regions pick
   up colour early, revealing the full extent of the dust cloud.
4. **Chunked iteration**: 50 000 points per `setTimeout` call keeps the page
   responsive; the canvas refreshes after every chunk so the image builds up
   visibly over ~40 frames.

## Palette

| Role | Colour |
|---|---|
| Background | `#0a0600` near-black |
| Low density | `#320C00` dark amber |
| Medium density | `#D25500` amber |
| High density | `#FFA80A` bright amber |
| Peak density | `#FF5082` rose |

## Files

- `generate_thumbnail.py` — generates `thumbnail.svg` with 3 000 attractor sample dots
- `thumbnail.svg` — 400×400 px static preview
- `index.html` — interactive canvas piece, self-contained, no external scripts

**Year:** 2026
