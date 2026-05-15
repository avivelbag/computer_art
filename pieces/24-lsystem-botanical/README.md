# The Plant That Writes Itself

An animated L-system botanical. A context-free string rewriting rule expands 6 times into a 1,995-segment fractal plant, then a turtle-graphics interpreter draws it branch by branch over 4 seconds. The plant holds at full opacity for 1 second, fades to nothing in 0.5 seconds, then regrows in a seamless loop.

## Grammar

**Fractal plant** (Prusinkiewicz & Lindenmayer, *The Algorithmic Beauty of Plants*, p. 25):

| Symbol | Production |
|--------|------------|
| X      | `F+[[X]-X]-F[-FX]+X` |
| F      | `FF` |

- **Axiom:** `X`
- **Angle:** 25°
- **Iterations:** 6 → 6,048 F-segments

## Turtle interpretation

| Symbol | Meaning |
|--------|---------|
| `F`    | Draw forward one segment; advance turtle |
| `+`    | Rotate left 25° (counter-clockwise) |
| `-`    | Rotate right 25° (clockwise) |
| `[`    | Push turtle state (position + heading + depth) onto stack; increase depth |
| `]`    | Pop turtle state from stack |
| `X`    | No-op production helper (no drawing) |

## Palette

| Role | Hex |
|------|-----|
| Background | `#f5f0e8` |
| Trunk (depth 0–1) | `#2d6a4f` |
| Branches (depth 2–3) | `#74c69d` |
| Leaf tips (depth 4+) | `#d8f3dc` |

Line width tapers with depth: 3 px (trunk) → 1.5 px (branches) → 0.7 px (tips). Depth is the bracket-nesting level at the time each `F` segment is drawn.

## Animation

The complete string expansion and turtle walk are computed once at startup. The animation loop reveals pre-computed segments in turtle-walk order (trunk first, tips last):

1. **Grow** (~4 s): segments appear progressively, proportional to elapsed time.
2. **Hold** (1 s): plant rests at full opacity.
3. **Fade** (0.5 s): plant fades to transparent.
4. Loop.

Frame delta is capped at 100 ms so backgrounded tabs do not burst on resume.

**Technique:** canvas / L-system / turtle graphics
**Year:** 2026
