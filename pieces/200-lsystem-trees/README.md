# Piece 200 — L-System Branching Trees: Pen-Plotter Grammar

Two L-system grammars grow stroke by stroke from axiom to fractal canopy on alternating backgrounds: a symmetric branching plant (ink-black on warm cream) and a baroque bush (copper on near-black). Each tree is revealed one turtle step at a time via requestAnimationFrame, then fades and restarts with a slightly varied starting angle for organic variation.

## Grammars

**Grammar 1 — Branching Plant**
- Axiom: `F`
- Rule: `F → F[+F]F[-F]F`
- Angle: 25.7°, Depth: 5 → 3 125 strokes
- Palette: ink-black `#1a1007` on warm cream `#f5ede0`

**Grammar 2 — Bush**
- Axiom: `F`
- Rule: `F → FF-[-F+F+F]+[+F-F-F]`
- Angle: 22.5°, Depth: 4 → 4 096 strokes
- Palette: copper `#c87941` on near-black `#0d0a06`

## Turtle Interpretation

Symbol meanings during string interpretation:
- `F` — step forward and draw a stroke
- `+` — turn left by the grammar's angle
- `-` — turn right by the grammar's angle
- `[` — push turtle state (position, direction, branch depth) onto a stack
- `]` — pop turtle state from the stack

Branch depth (number of unclosed brackets enclosing the current position) drives line-width tapering via `baseWidth × 0.55^depth`, so trunk strokes are thick and tips become hairlines down to 0.3 px.

## Animation

The full segment list is precomputed once at grammar load time. Each `requestAnimationFrame` callback draws the next batch of strokes up to a linearly-interpolated target index, so the tree visibly grows from root to canopy. After the complete tree is revealed it holds for 2.5 seconds, fades to the background colour over 1.5 seconds, then switches to the next grammar with a ±2° angle jitter applied to the starting direction.

## Technique

canvas / L-system / turtle graphics / parametric grammar / requestAnimationFrame

**Year:** 2026
