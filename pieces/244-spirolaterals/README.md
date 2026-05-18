# 244 — Spirolateral Mandalas

An animated gallery of spirolateral figures — geometric paths produced by "turtle graphics" driven by integer sequences. Each cell in a 4×4 grid shows a different sequence and turning angle; figures draw themselves one stroke at a time and the gallery cycles seamlessly between two sets.

## What is a spirolateral?

A spirolateral is constructed by a turtle that repeats a fixed rule: walk forward `seq[0]` units, turn right by angle `A`, walk `seq[1]` units, turn, …, walk `seq[n-1]` units, turn, then start the sequence again. Under the right conditions the path closes into a rotationally-symmetric figure. Small changes in the sequence or angle produce wildly different shapes — from tight square rosettes to open pentagonal stars to dense hexagonal weaves.

## Closure condition

A spirolateral with `n` elements per cycle and turn angle `A°` closes after `R` repetitions of the full sequence, where:

```
R = 360 / gcd(360, (n × A) mod 360)
```

When `n × A` is itself a multiple of 360° — meaning every pass starts with the turtle facing the same direction — closure requires the net single-pass displacement to equal zero, which is a condition on divisibility within the integer sequence.

| Sequence | Angle | Repeats | Character |
|----------|-------|---------|-----------|
| [1,2,3] | 90° | 4 | Square spiral rosette |
| [1,2,3,4] | 90° | 4 | Layered square |
| [1,2,3,4,5] | 72° | 4 | Pentagonal weave |
| [1,2] | 144° | 5 | Pentagonal rose |
| [1,2,3,4,5,6] | 60° | 4 | Hexagonal star |
| [1,2,3,4] | 120° | 3 | Dense triangular net |

## Animation

The piece runs two "sets" of 16 figures (4×4 grid each). Within a set:

- Every `requestAnimationFrame` tick advances each figure by N new line segments in sequence order (N controlled by Slow / Normal / Fast buttons).
- When all figures in the set are complete, a ~2-second pause follows.
- A smooth crossfade (~0.9 s) transitions to the next set, which then redraws itself stroke by stroke.

## Palette

| Role | Hex |
|------|-----|
| Background | `#0d1117` |
| Mint | `#7fffd4` |
| Rose | `#ffb3c1` |
| Gold | `#ffd700` |
| Violet | `#c9a7ff` |

Colors cycle across the 4×4 grid (cell index mod 4), so each figure has one consistent color.

## Files

| File | Purpose |
|------|---------|
| `index.html` | Self-contained animated gallery — no external dependencies beyond `lib/` |
| `generate_thumbnail.py` | Deterministic SVG thumbnail (stdlib only, 3×3 grid of nine figures) |
| `thumbnail.svg` | Pre-generated thumbnail |
