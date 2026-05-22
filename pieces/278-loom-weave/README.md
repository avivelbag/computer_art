# 278 — The Loom Remembers

A digital loom simulation where 60 warp threads and 60 weft threads interlace following four threading drafts, the warm terracotta-to-cream warp palette meeting a cool indigo-to-sky weft palette, as the color gradient drifts continuously over a 60-second sinusoidal cycle.

## How it works

**Threading drafts.** Each draft is encoded as a flat integer array (1 = warp over weft, 0 = weft over warp) with a column-repeat size and a row-repeat size. A single function `warpOver(draft, r, c)` indexes the array via `(r % rows) * size + (c % size)` to determine which thread is on top at each intersection.

**Plain weave (2×2 repeat).** Warp and weft alternate strictly — warp over, weft over, warp over — giving the maximum interlacing frequency and the tightest, most balanced structure.

**2/2 Twill (4×4 repeat).** Each warp thread floats over two weft picks then under two, with the pattern shifting one column per row. This produces the characteristic diagonal rib visible in denim and flannel.

**4/1 Satin (5×5 repeat).** One weft pick per five is weft-over; the remaining four are warp-over. The "down" column steps by three each row (the satin step for a 5-shaft loom), deliberately breaking the diagonal so no twill rib appears, producing a smooth warp-faced surface.

**Herringbone (8×4 repeat).** A 2/2 twill running in the forward direction (+1 per row) for the first four columns, then reversed (−1 per row) for the next four. The diagonal rib reverses at every fourth column, producing the V-shaped herringbone motif.

**Color.** Warp threads (vertical) sample a warm palette — terracotta `#c2714f` → ochre `#c99a3a` → cream `#f0e0c0` — mapping column position to palette position. Weft threads (horizontal) sample a cool palette — indigo `#3b3078` → slate `#6b7ba4` → sky `#a8c4d4` — mapping row position. A slow sinusoidal drift offsets both mappings over 60 seconds, causing the warm and cool gradients to shift across the cloth without any jump cut.

**Animation.** The weave structure cycles automatically every 20 seconds (plain → twill → satin → herringbone → plain). A subtle highlight along the top and left edges of raised (warp-over) cells reinforces the three-dimensional over/under illusion. Redraws are throttled: a state key encodes the current draft index and quantized drift value, so no pixel work happens between slow color ticks.

## Palette

| Thread | Role         | From            | To              |
|--------|--------------|-----------------|-----------------|
| Warp   | Warm (vertical)  | Terracotta `#c2714f` | Cream `#f0e0c0` |
| Weft   | Cool (horizontal) | Indigo `#3b3078`   | Sky `#a8c4d4`  |
| Gap    | Background   | Near-black `#110a05` | —           |

## Files

| File                    | Purpose                                                       |
|-------------------------|---------------------------------------------------------------|
| `index.html`            | Self-contained canvas animation — no external dependencies    |
| `generate_thumbnail.py` | Deterministic SVG thumbnail generator (stdlib only)           |
| `thumbnail.svg`         | Pre-generated 400×400 thumbnail, 30×30 grid, 2/2 twill draft |
