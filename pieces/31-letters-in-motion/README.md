# Letters in Motion

The word **DRIFT** is drawn with a large bold font into a hidden offscreen canvas; `getImageData` then reads back the rasterised bitmap pixel-by-pixel at a 3-pixel stride, collecting the `[x, y]` coordinates of every dark pixel as particle targets. Each target seeds one particle that begins at a random screen position, lerps toward its destination each frame with a sinusoidal wobble that diminishes as the particle converges, and after the full word assembles the particles scatter outward with accelerating random velocity and fade to nothing before the cycle restarts.

## Palette

| Role | Hex |
|------|-----|
| Background | `#f5f0eb` |
| Text particles | `#1a1a2e` |
| Accent particles (~12 %) | `#e94560` |

## Animation loop

1. **Assembling** (3 s) — particles lerp toward targets; wobble amplitude shrinks from 6 px to 0 as they arrive.
2. **Holding** (0.6 s) — particles rest at targets with a gentle ±1.5 px drift.
3. **Dispersing** (3 s) — particles fly outward with exponentially growing velocity and fade to transparent.

Frame delta is capped at 50 ms so backgrounded tabs do not burst on resume.

**Technique:** canvas / generative typography / particle system
**Year:** 2026
