# Piece 95 — Dragon Curve: The Fold That Never Repeats

An order-15 dragon curve (32 768 segments) animated on an 800 × 800 canvas. Segments grow one by one from the starting point, coloured by position along the curve using a deliberate teal-to-rose gradient that reveals the layered structure of repeated paper folds. After the full curve is visible it holds briefly, fades to black, and restarts.

## Paper-Folding Construction

Take a long strip of paper. Fold it in half — right half over left half. Unfold. Looking at the crease from left to right, you see one valley fold: **L**.

Fold again (right over left, twice). Unfold. Now there are three creases left-to-right: **L L R**.

Repeat: each new fold inserts an **L** in the middle and then interleaves the previous sequence with each crease mirrored and reversed on the right half. After *k* folds you have 2^k − 1 creases, and the sequence of turns they prescribe, when walked as unit steps on a grid, traces the order-*k* dragon curve.

### Why It Never Repeats

The fold rule is deterministic but not periodic: no finite rotation or translation maps the full infinite limit curve onto itself. It is self-similar under a 90° rotation by factor 1/√2, but that similarity is not a periodicity — every sub-curve appears embedded in larger scales infinitely often without the overall pattern ever tiling the plane.

## Bit-Sequence Shortcut

Walking the paper-fold sequence naively requires storing or regenerating 2^k − 1 turns. The bit-sequence algorithm computes the turn at position *n* (1-indexed) in O(1) time and O(1) memory:

```
ctz(n)       = number of trailing zero bits of n
turn(n) = LEFT  if ((n >> (ctz(n) + 1)) & 1) == 0
          RIGHT otherwise
```

**Why it works:** The dragon curve turn sequence equals the *regular paper-folding sequence*. The paper-folding sequence has the property that position *n* records the direction of the fold at the hierarchical level corresponding to the lowest set bit of *n*. The bit immediately above that lowest set bit encodes whether the fold at that level is left or right.

For example:

| n | binary | ctz | bit above | turn |
|---|--------|-----|-----------|------|
| 1 | 001    | 0   | bit 1 = 0 | L    |
| 2 | 010    | 1   | bit 2 = 0 | L    |
| 3 | 011    | 0   | bit 1 = 1 | R    |
| 4 | 100    | 2   | bit 3 = 0 | L    |
| 5 | 101    | 0   | bit 1 = 1 | L    |
| 6 | 110    | 1   | bit 2 = 1 | R    |
| 7 | 111    | 0   | bit 1 = 1 | R    |

This matches the known sequence LLRLLRR… exactly, with no string rewriting, no recursion, and no storage beyond a direction variable.

## Canvas Sizing

All 32 769 grid points of the iteration-15 curve are pre-computed once at page load. The bounding box is found in a single pass, and a scale factor is chosen so the curve fills ~85% of the 800 × 800 canvas with equal margins. This prevents clipping regardless of how the curve's asymmetric bounding box happens to fall.

## Colour Palette

- **Start (segment 0):** deep teal `#0d7377` (rgb 13, 115, 119)
- **End (segment 32 767):** rose `#c45c8e` (rgb 196, 92, 142)
- **Background:** near-black navy `#0a1628`

Intermediate segments are linearly interpolated in RGB space, so the teal region marks the beginning of the curve and the rose marks the furthest-folded end. The gradient makes the hierarchical self-similar layering visible at a glance.

## Files

- `index.html` — self-contained canvas animation, no external dependencies
- `thumbnail.svg` — iteration-13 static preview with 32 colour bands
- `generate_thumbnail.py` — Python script that produced `thumbnail.svg`
- `README.md` — this file
