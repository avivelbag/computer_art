# 221 — Ulam Spiral: The Hidden Order of Primes

Interactive canvas visualisation of the Ulam prime spiral up to N = 200 000 integers.

## Algorithm

**Spiral construction** — integers are placed in a square spiral starting from 1 at the centre. The walk follows the sequence: right 1, up 1, left 2, down 2, right 3, up 3, … where each run length is used twice before incrementing. Grid coordinates are stored in a `Uint32Array` of size 500 × 500 (covering ±250 in each axis), which is sufficient for N = 200 000 (max coordinate ≈ ±224).

**Sieve** — smallest prime factors (SPF) for all integers 1..N are computed with a standard Eratosthenes sieve in O(N log log N). A number n ≥ 2 is prime iff `spf[n] === n`. The SPF array also drives factorisation: dividing out `spf[n]` repeatedly yields the complete factorisation in O(log n) per number.

**Colour precomputation** — on colour mode change, `colorR/G/B` typed arrays are filled for every n in a single O(N) pass, so the render loop only needs one array read per grid cell.

## Rendering

Each frame is written to an `ImageData` buffer (one pixel at a time). A horizontal-repeat cache skips the grid lookup when consecutive pixels map to the same grid column — effective when `scale > 1`. A 1-pixel gap is drawn between cells when `scale ≥ 5` to make individual cells legible.

The viewport is defined by `(viewCx, viewCy, scale)` — centre in grid coordinates and pixels per cell. Zoom keeps the grid point under the cursor fixed by adjusting the centre after scaling.

## Colour modes

| Mode | Prime colour | Composite colour |
|------|-------------|-----------------|
| Monochrome | Amber | Near-black |
| Residue mod 4 | Teal (p≡1), Rose (p≡3), Purple (p=2) | Near-black |
| Smallest factor | Gold (prime) | Blue/green/amber/purple/orange by factor |

## Files

- `index.html` — self-contained interactive piece
- `thumbnail.svg` — 200×200 SVG preview (41×41 grid, n=1..1681)
- `README.md` — this file
