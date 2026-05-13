# Piece 111 — Bifurcation: Where Order Fractures Into Chaos

The logistic map `x → r·x·(1−x)` is one of the simplest non-linear recurrences and one of the most consequential. By sweeping the growth parameter *r* from 2.5 to 4.0 and plotting the long-run attractor of *x*, a single image captures the entire transition from order to chaos.

## The logistic map

At each step the population fraction *x* ∈ (0, 1) is updated by:

```
x_{n+1} = r · x_n · (1 − x_n)
```

The constant *r* controls growth rate. For each *r*:

1. **Warmup** — iterate 300 times to let transients die out.
2. **Plot** — iterate 300 more times and light up the corresponding pixel row for each *x* value.

## Bifurcation structure

| r range | Behaviour |
|---|---|
| 2.5 – 3.0 | Single stable fixed point: x* = 1 − 1/r |
| 3.0 – 3.449 | Period-2 oscillation |
| 3.449 – 3.544 | Period-4 |
| 3.544 – 3.565 | Period-8, 16, 32 … (Feigenbaum cascade) |
| ≈ 3.57 | Onset of chaos |
| 3.57 – 4.0 | Chaotic with intermittent periodic windows |

The ratio of successive bifurcation intervals converges to the **Feigenbaum constant** δ ≈ 4.669 — the same constant appears in any one-parameter family with a smooth maximum, a deep universality result.

## Color palette

Point color is determined solely by *r*, not by *x* or iteration count:

- `t = (r − 2.5) / 1.5` maps the full range to [0, 1]
- **Blue** `(30, 80, 200)` at `t = 0` (stable region)
- **Gold** `(255, 200, 30)` at `t = 1` (chaotic region)

A subtle dashed vertical line marks the onset of chaos at r ≈ 3.57.

## Animation

The diagram draws one r-column per frame (~7 columns/frame at 60 fps), building left to right over roughly two seconds. After completion it holds for four seconds, then resets and repeats.

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `generate_thumbnail.py` — pure-stdlib Python script that writes `thumbnail.png`
- `thumbnail.png` — 400 × 400 static render
- `README.md` — this file
