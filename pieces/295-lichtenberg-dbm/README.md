# Arc & Ether

Electric discharge trees grown in real time by the Dielectric Breakdown Model
(Niemeyer, Pietronero & Wiesmann, 1984).

A single seed cell at the canvas centre is held at zero potential while the canvas
boundary is held at unit potential. The Laplace equation ∇²φ = 0 is solved
iteratively (Gauss-Seidel relaxation) so that the potential field increases
smoothly from the tree outward. At each animation step, a frontier cell is
chosen with probability proportional to φ^η (η = 1.5) and added to the discharge
tree. The ETA exponent amplifies potential differences so the branch tips — which
reach into unscreened, high-potential territory — grow far more readily than
shielded trunk cells, producing the characteristic fractal branching of real
Lichtenberg figures.

To keep growth within the 16 ms/frame budget, Gauss-Seidel relaxation runs only
over cells within 22 pixels of the newest tree node rather than sweeping the
entire 500 × 500 grid each step.

Once the tree touches the canvas edge the animation pauses, fades the tree to
black, and restarts from the same seed — the stochastic growth rule produces a
different fractal each time.

## Visual language

| Element | Value |
|---------|-------|
| Background | `#08071a` — deep indigo |
| Outer glow | `#6040c0` — violet, 14 px canvas `shadowBlur` |
| Bright core | `#d0c8ff` — white-violet, narrow stroke |
| Canvas | 500 × 500 px |

## Technique

- Dielectric Breakdown Model (DBM) — Niemeyer et al. 1984
- Laplace potential field solved with sparse Gauss-Seidel relaxation
- Weighted frontier sampling: probability ∝ φ^η
- Canvas 2D API — no external libraries

## Thumbnail

```
python3 generate.py
```

Runs a deterministic DBM on a 120 × 120 grid (seed 42) and exports the
700-segment tree as an SVG with a Gaussian glow filter.

**Year:** 2026
