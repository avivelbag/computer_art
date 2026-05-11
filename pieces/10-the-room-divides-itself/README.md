# The Room Divides Itself

A square canvas subdivided recursively by a seeded random process — architectural like a floor plan, organic like a cell dividing.

## Splitting algorithm

The process starts with the full 800×800 square. At each step, a rectangle decides whether to split:

```
split_probability = SPLIT_PROB_BASE ^ depth   (0.85^0=1.0, 0.85^1=0.85, …)
```

If it splits, it chooses a direction (horizontal or vertical, preferring the longer axis) and picks a cut position uniformly from `[0.3, 0.7]` of that dimension — preventing slivers under 30% of the parent's size. The two children recurse at `depth + 1`.

Stopping conditions (any one is sufficient):
- `depth >= MAX_DEPTH` (6)
- `min(width, height) < MIN_SIZE` (40 px)
- the random draw exceeds `split_prob`
- the proposed cut would produce a child narrower than `MIN_SIZE / 2`

Leaf rectangles are filled from the palette; approximately 22% receive a warm white/cream colour to provide breathing room in the composition.

## Palette

Contemporary earthy, five core hues plus two off-whites (seven colours total):

| Swatch | Hex | Name |
|--------|-----|------|
| ![](https://via.placeholder.com/14/c2644f/000000?text=+) | `#c2644f` | Terracotta |
| ![](https://via.placeholder.com/14/8fad75/000000?text=+) | `#8fad75` | Sage |
| ![](https://via.placeholder.com/14/d4a853/000000?text=+) | `#d4a853` | Ochre |
| ![](https://via.placeholder.com/14/4a6fa5/000000?text=+) | `#4a6fa5` | Dusty blue |
| ![](https://via.placeholder.com/14/5c5c5c/000000?text=+) | `#5c5c5c` | Charcoal |
| ![](https://via.placeholder.com/14/f5f0e8/000000?text=+) | `#f5f0e8` | Warm white |
| ![](https://via.placeholder.com/14/ede7d9/000000?text=+) | `#ede7d9` | Linen |

Inspired by the earthy palettes of Japanese mingei ceramics — an aesthetic where every colour feels like it could be found in soil, wood, or fired clay.

## Seed

`random.seed(42)` — the composition is fully deterministic. Run `python3 generate.py` to regenerate `piece.svg` and `thumbnail.svg` identically.

## Technique

Static SVG — no JavaScript, no server. Open `piece.svg` directly in any browser.

**Year:** 2026
