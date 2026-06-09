# Cathedral Light

A static SVG rose window generated under D12 dihedral symmetry — 12-fold
rotational symmetry combined with reflections. Three concentric rings of
petal and lancet-arch forms are filled with a saturated stained-glass
palette of ruby, cobalt, gold, emerald, violet, and amber, separated by
lead-gray caming lines.

## Structure

| Region | Radii | Subdivisions | Coloring |
|---|---|---|---|
| Center disc | r = 60 | — | Gold |
| Ring 1 — trefoil petals | r 60–160 | 12 × 30° annular sectors | Ruby / cobalt alternating |
| Ring 2 — quatrefoil lobes | r 160–280 | 24 × 15° annular sectors | Emerald / violet / amber cycling |
| Ring 3 — lancet arch slivers | r 280–320 | 12 × 30° annular sectors | 4-color: ruby / cobalt / gold / emerald |
| Ring 3 — lancet arch bodies | r 320–400 | 12 pointed arches | 4-color offset by 2 (gold / emerald / ruby / cobalt) |
| Outer border | r = 400 | Lead circle | Dark gray #222 |

## Symmetry — D12

The dihedral group D12 has 24 elements: 12 rotations (multiples of 30°) and
12 reflections. Every ring is constructed by placing one fundamental domain
and rotating it through all 12 positions, so the design is automatically
symmetric under any 30° rotation or reflection through a spoke line.

## Coloring

Within each ring, a proper graph coloring (no two adjacent regions share the
same color) is achieved by:

- **Ring 1** (2-colorable cycle of 12): alternating ruby / cobalt.
- **Ring 2** (3-colorable cycle of 24): cycling emerald → violet → amber.
- **Ring 3** (4-colorable — slivers and bodies share boundaries):
  slivers cycle ruby → cobalt → gold → emerald; bodies are offset by +2
  (gold → emerald → ruby → cobalt), so every sliver-body pair and every
  pair of adjacent slivers or bodies is a different color.

## Lancet arch shape

Each Ring 3 body is a curved triangle: a circular arc base at r = 320, with
two straight sides converging on a pointed tip at r = 400 at the sector
mid-angle. The dark gaps between adjacent lancet tips reproduce the mortar
and tracery openings seen in Gothic rose-window stonework.

## Reproducibility

```
python3 generate.py
```

Pure Python standard library (`math`, `pathlib`). No external dependencies.
The SVG is deterministic: running `generate.py` again produces bit-identical
output.

**Year:** 2026
